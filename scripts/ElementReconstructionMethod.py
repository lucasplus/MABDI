"""
In this script we are going to compare surface reconstruction methods
- vtkSurfaceReconstruction
- vtkDelaunay2D
- vtkDelaunay3D
"""

import os
import string

import vtk
from vtk.util.colors import *
from vtk.util.misc import vtkGetDataRoot

import mabdi

import random

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

# Read some points. Use a programmable filter to read them.
pointSource = vtk.vtkProgrammableSource()


def func_read_points():
    output = pointSource.GetPolyDataOutput()
    points = vtk.vtkPoints()
    output.SetPoints(points)

    datafile = open(os.path.normpath(os.path.join(vtkGetDataRoot(), "Data/cactus.3337.pts")))

    line = datafile.readline()
    while line:
        data = line.split()
        if data and data[0] == 'p':
            x, y, z = float(data[1]), float(data[2]), float(data[3])
            if random.random() < 0.4 and x > .5:
                points.InsertNextPoint(x, y, z)
        line = datafile.readline()
pointSource.SetExecuteMethod(func_read_points)


# Construct the surface and create isosurface.
surf = vtk.vtkSurfaceReconstructionFilter()
surf.SetNeighborhoodSize(20)
surf.SetSampleSpacing(.01)
mabdi.DebugTimeVTKFilter(surf)
surf.SetInputConnection(pointSource.GetOutputPort())

cf = vtk.vtkContourFilter()
mabdi.DebugTimeVTKFilter(cf)
cf.SetInputConnection(surf.GetOutputPort())
cf.SetValue(0, 0.0)

# Sometimes the contouring algorithm can create a volume whose gradient
# vector and ordering of polygon (using the right hand rule) are
# inconsistent. vtkReverseSense cures this problem.
reverse = vtk.vtkReverseSense()
mabdi.DebugTimeVTKFilter(reverse)
reverse.SetInputConnection(cf.GetOutputPort())
reverse.ReverseCellsOn()
reverse.ReverseNormalsOn()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(reverse.GetOutputPort())
mapper.ScalarVisibilityOff()

surfaceActor = vtk.vtkActor()
surfaceActor.SetMapper(mapper)
surfaceActor.GetProperty().SetDiffuseColor(1.0000, 0.3882, 0.2784)
surfaceActor.GetProperty().SetSpecularColor(1, 1, 1)
surfaceActor.GetProperty().SetSpecular(.4)
surfaceActor.GetProperty().SetSpecularPower(50)

ball = vtk.vtkSphereSource()
ball.SetRadius(0.005)
ball.SetThetaResolution(12)
ball.SetPhiResolution(12)
balls = vtk.vtkGlyph3D()
balls.SetInputConnection(pointSource.GetOutputPort())
balls.SetSourceConnection(ball.GetOutputPort())
mapBalls = vtk.vtkPolyDataMapper()
mapBalls.SetInputConnection(balls.GetOutputPort())
ballActor = vtk.vtkActor()
ballActor.SetMapper(mapBalls)
ballActor.GetProperty().SetColor(hot_pink)
ballActor.GetProperty().SetSpecularColor(1, 1, 1)
ballActor.GetProperty().SetSpecular(0.3)
ballActor.GetProperty().SetSpecularPower(20)
ballActor.GetProperty().SetAmbient(0.2)
ballActor.GetProperty().SetDiffuse(0.8)

# Create the RenderWindow, Renderer and both Actors
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(surfaceActor)
ren.AddActor(ballActor)
ren.SetBackground(1, 1, 1)
renWin.SetSize(400, 400)
ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
ren.GetActiveCamera().SetPosition(1, 0, 0)
ren.GetActiveCamera().SetViewUp(0, 0, 1)
ren.ResetCamera()
ren.GetActiveCamera().Azimuth(20)
ren.GetActiveCamera().Elevation(30)
ren.GetActiveCamera().Dolly(1.2)
ren.ResetCameraClippingRange()

print surf.GetSampleSpacing()

iren.Initialize()
renWin.Render()
iren.Start()
