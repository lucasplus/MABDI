"""
In this script we are going to compare surface reconstruction methods
- vtkSurfaceReconstruction
- vtkDelaunay2D
- vtkDelaunay3D
"""

# TODO make it work with the table environment
# TODO show the table environment as opaque

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

""" Point source (pointSource) """

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
                points.InsertNextPoint(y, z, x)
        line = datafile.readline()
pointSource.SetExecuteMethod(func_read_points)

# actor to show the points
ball = vtk.vtkSphereSource()
ball.SetRadius(0.005)
ball.SetThetaResolution(12)
ball.SetPhiResolution(12)
balls = vtk.vtkGlyph3D()
balls.SetInputConnection(pointSource.GetOutputPort())
balls.SetSourceConnection(ball.GetOutputPort())
mapBalls = vtk.vtkPolyDataMapper()
mapBalls.SetInputConnection(balls.GetOutputPort())
pointActor = vtk.vtkActor()
pointActor.SetMapper(mapBalls)
pointActor.GetProperty().SetColor(hot_pink)
pointActor.GetProperty().SetSpecularColor(1, 1, 1)
pointActor.GetProperty().SetSpecular(0.3)
pointActor.GetProperty().SetSpecularPower(20)
pointActor.GetProperty().SetAmbient(0.2)
pointActor.GetProperty().SetDiffuse(0.8)

""" vtkSurfaceReconstructionFilter """

# parameters, set 0 to not set them
surf_neighborhood_size = 20  # default is 20
surf_sample_spacing = .01

surf = vtk.vtkSurfaceReconstructionFilter()
mabdi.DebugTimeVTKFilter(surf)
if surf_neighborhood_size != 0:
    surf.SetNeighborhoodSize(surf_neighborhood_size)
if surf_sample_spacing != 0:
    surf.SetSampleSpacing(surf_sample_spacing)
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

surfao = mabdi.VTKPolyDataActorObjects()
surfao.mapper.SetInputConnection(reverse.GetOutputPort())

surfao.mapper.ScalarVisibilityOff()

surfao.actor.GetProperty().SetDiffuseColor(1.0000, 0.3882, 0.2784)
surfao.actor.GetProperty().SetSpecularColor(1, 1, 1)
surfao.actor.GetProperty().SetSpecular(.4)
surfao.actor.GetProperty().SetSpecularPower(50)

""" vtkDelaunay2D """

delny2D = vtk.vtkDelaunay2D()
mabdi.DebugTimeVTKFilter(delny2D)
delny2D.SetInputConnection(pointSource.GetOutputPort())
delny2D.SetAlpha(0.05)
delny2D.SetTolerance(0.001)

delny2Dao = mabdi.VTKPolyDataActorObjects()
delny2Dao.mapper.SetInputConnection(delny2D.GetOutputPort())

delny2Dao.mapper.ScalarVisibilityOff()

delny2Dao.actor.GetProperty().SetDiffuseColor(1.0000, 0.3882, 0.2784)
delny2Dao.actor.GetProperty().SetSpecularColor(1, 1, 1)
delny2Dao.actor.GetProperty().SetSpecular(.4)
delny2Dao.actor.GetProperty().SetSpecularPower(50)

""" vtkDelaunay3D """

# Delaunay3D is used to triangulate the points. The Tolerance is the
# distance that nearly coincident points are merged
# together. (Delaunay does better if points are well spaced.) The
# alpha value is the radius of circumcircles, circumspheres. Any mesh
# entity whose circumcircle is smaller than this value is output.
delny3D = vtk.vtkDelaunay3D()
mabdi.DebugTimeVTKFilter(delny3D)
delny3D.SetInputConnection(pointSource.GetOutputPort())
delny3D.SetTolerance(0.001)
# delny3D.SetAlpha(0.05)
delny3D.BoundingTriangulationOff()

delny3Dao = mabdi.VTKPolyDataActorObjects()
delny3Dao.mapper.SetInputConnection(delny3D.GetOutputPort())

delny3Dao.mapper.ScalarVisibilityOff()

delny3Dao.actor.GetProperty().SetDiffuseColor(1.0000, 0.3882, 0.2784)
delny3Dao.actor.GetProperty().SetSpecularColor(1, 1, 1)
delny3Dao.actor.GetProperty().SetSpecular(.4)
delny3Dao.actor.GetProperty().SetSpecularPower(50)

""" Render objects """

renWin = vtk.vtkRenderWindow()
renWin.SetSize(640*3, 480)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renSurf = vtk.vtkRenderer()
renSurf.SetBackground(1, 1, 1)

renDy2D = vtk.vtkRenderer()
renDy2D.SetBackground(1, 1, 1)

renDy3D = vtk.vtkRenderer()
renDy3D.SetBackground(1, 1, 1)

renSurf.SetViewport(0.0, 0.0, 1.0/3, 1.0)
renDy2D.SetViewport(1.0/3, 0.0, 2.0/3, 1.0)
renDy3D.SetViewport(2.0/3, 0.0, 3.0/3, 1.0)

renWin.AddRenderer(renSurf)
renWin.AddRenderer(renDy2D)
renWin.AddRenderer(renDy3D)

renSurf.AddActor(surfao.actor)
renSurf.AddActor(pointActor)
renDy2D.AddActor(delny2Dao.actor)
renDy2D.AddActor(pointActor)
renDy3D.AddActor(delny3Dao.actor)
renDy3D.AddActor(pointActor)

""" Control point visibility """


def user_event_callback(obj, env):
    if not hasattr(user_event_callback, 'point_visibility'):
        user_event_callback.point_visibility = True
    user_event_callback.point_visibility = not user_event_callback.point_visibility
    if user_event_callback.point_visibility:
        pointActor.SetVisibility(1)
    else:
        pointActor.SetVisibility(0)
    iren.Render()
iren.AddObserver('UserEvent', user_event_callback)

""" Start Rendering """

print vtkGetDataRoot()

iren.Initialize()
iren.Start()
