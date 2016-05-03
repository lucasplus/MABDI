import vtk
from vtk.util.colors import *
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np

import time
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

"""
Script to test the ability of vtk's surface reconstruction methods to work on our data
Render Window top row
- [Scenario View] renSc; Interactive
- [POV of sensor] renSV; Not Interactive (unless offscreen rendering works)
- [Sensor output] renSO; Not Interactive
Render Window bottom row [surf] [delny2D] [delny3D] Interactive
- Output of the algorithms
- Translucent environment
- Input points to the algorithm
"""

"""
Source and filters (source->depthimage->pointcloud)
[source] [sourceAo] - polydata describing environment
[di] [diAo] - Depth image
[pc] [pcAo] - Point cloud
[spc] [spcActor] - Subsampled point cloud
"""

# source
source = mabdi.SourceEnvironmentTable()
# source.set_object_state(object_name='table', state=False)
# source.set_object_state(object_name='left_cup', state=False)
# source.set_object_state(object_name='right_cup', state=False)
source.Update()
sourceAo = mabdi.VTKPolyDataActorObjects()
sourceAo.mapper.SetInputConnection(source.GetOutputPort())
sourceAo.actor.SetMapper(sourceAo.mapper)
sourceAo.actor.GetProperty().SetColor(slate_grey_light)
sourceAo.actor.GetProperty().SetOpacity(0.8)

# depth image
di = mabdi.FilterDepthImage()
di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects()
diAo.mapper.SetInputConnection(di.GetOutputPort())
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

# point cloud
pc = mabdi.FilterPointCloud()
pc.SetInputConnection(di.GetOutputPort())
pcAo = mabdi.VTKPolyDataActorObjects()
pcAo.mapper.SetInputConnection(pc.GetOutputPort())
pcAo.actor.GetProperty().SetPointSize(1.5)
pcAo.actor.GetProperty().SetColor(red)

# subsampled point cloud
spc = vtk.vtkMaskPoints()
mabdi.DebugTimeVTKFilter(spc)
spc.SetInputConnection(pc.GetOutputPort())
spc.SetOnRatio(31)
spc.RandomModeOff()
spc.SetRandomModeType(0)

# subsampled point cloud actor
ball = vtk.vtkSphereSource()
ball.SetRadius(0.01)
ball.SetThetaResolution(12)
ball.SetPhiResolution(12)
balls = vtk.vtkGlyph3D()
balls.SetInputConnection(spc.GetOutputPort())
balls.SetSourceConnection(ball.GetOutputPort())
mapBalls = vtk.vtkPolyDataMapper()
mapBalls.SetInputConnection(balls.GetOutputPort())
spcActor = vtk.vtkActor()
spcActor.SetMapper(mapBalls)
spcActor.GetProperty().SetColor(hot_pink)
spcActor.GetProperty().SetSpecularColor(1, 1, 1)
spcActor.GetProperty().SetSpecular(0.3)
spcActor.GetProperty().SetSpecularPower(20)
spcActor.GetProperty().SetAmbient(0.2)
spcActor.GetProperty().SetDiffuse(0.8)

""" vtkSurfaceReconstructionFilter """

# parameters, set 0 to not set them
surf_neighborhood_size = 5  # default is 20
surf_sample_spacing = 0

surf = vtk.vtkSurfaceReconstructionFilter()
mabdi.DebugTimeVTKFilter(surf)
if surf_neighborhood_size != 0:
    surf.SetNeighborhoodSize(surf_neighborhood_size)
if surf_sample_spacing != 0:
    surf.SetSampleSpacing(surf_sample_spacing)
surf.SetInputConnection(spc.GetOutputPort())

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

surfAo = mabdi.VTKPolyDataActorObjects()
surfAo.mapper.SetInputConnection(reverse.GetOutputPort())

surfAo.mapper.ScalarVisibilityOff()

surfAo.actor.GetProperty().SetDiffuseColor(red)
surfAo.actor.GetProperty().SetSpecularColor(1, 1, 1)
surfAo.actor.GetProperty().SetSpecular(.4)
surfAo.actor.GetProperty().SetSpecularPower(50)

""" vtkDelaunay2D """

delny2D = vtk.vtkDelaunay2D()
mabdi.DebugTimeVTKFilter(delny2D)
delny2D.SetInputConnection(spc.GetOutputPort())
delny2D.SetAlpha(0.05)
delny2D.SetTolerance(0.001)

delny2DAo = mabdi.VTKPolyDataActorObjects()
delny2DAo.mapper.SetInputConnection(delny2D.GetOutputPort())

delny2DAo.mapper.ScalarVisibilityOff()

delny2DAo.actor.GetProperty().SetDiffuseColor(red)
delny2DAo.actor.GetProperty().SetSpecularColor(1, 1, 1)
delny2DAo.actor.GetProperty().SetSpecular(.4)
delny2DAo.actor.GetProperty().SetSpecularPower(50)

""" vtkDelaunay3D """

# Delaunay3D is used to triangulate the points. The Tolerance is the
# distance that nearly coincident points are merged
# together. (Delaunay does better if points are well spaced.) The
# alpha value is the radius of circumcircles, circumspheres. Any mesh
# entity whose circumcircle is smaller than this value is output.
delny3D = vtk.vtkDelaunay3D()
mabdi.DebugTimeVTKFilter(delny3D)
delny3D.SetInputConnection(spc.GetOutputPort())
delny3D.SetTolerance(0.001)
delny3D.SetAlpha(0.1)
delny3D.BoundingTriangulationOff()

delny3DAo = mabdi.VTKPolyDataActorObjects()
delny3DAo.mapper.SetInputConnection(delny3D.GetOutputPort())

delny3DAo.mapper.ScalarVisibilityOff()

delny3DAo.actor.GetProperty().SetDiffuseColor(red)
delny3DAo.actor.GetProperty().SetSpecularColor(1, 1, 1)
delny3DAo.actor.GetProperty().SetSpecular(.4)
delny3DAo.actor.GetProperty().SetSpecularPower(50)

""" Render objects """

renWin = vtk.vtkRenderWindow()
renWin.SetSize(640*3, 480*2)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

""" Render objects top row """

renSc = vtk.vtkRenderer()
renSc.SetBackground(eggshell)
renSc.SetViewport(0.0, 0.5, 1.0/3, 1.0)
renSc.AddActor(sourceAo.actor)
renSc.AddActor(pcAo.actor)
renSc.AddActor(spcActor)

renSo = vtk.vtkRenderer()
renSo.SetViewport(2.0/3, 0.5, 3.0/3, 1.0)
renSo.SetInteractive(0)
renSo.AddActor(diAo.actor)

renWin.AddRenderer(renSc)
renWin.AddRenderer(renSo)

""" Render objects bottom row """

renSurf = vtk.vtkRenderer()
renSurf.SetBackground(eggshell)
renSurf.SetViewport(0.0, 0.0, 1.0/3, 0.5)
renSurf.AddActor(surfAo.actor)
renSurf.AddActor(sourceAo.actor)

renDy2D = vtk.vtkRenderer()
renDy2D.SetBackground(eggshell)
renDy2D.SetViewport(1.0/3, 0.0, 2.0/3, 0.5)
renDy2D.AddActor(delny2DAo.actor)
renDy2D.AddActor(sourceAo.actor)
# renDy2D.AddActor(spcActor)

renDy3D = vtk.vtkRenderer()
renDy3D.SetBackground(eggshell)
renDy3D.SetViewport(2.0/3, 0.0, 3.0/3, 0.5)
renDy3D.AddActor(delny3DAo.actor)
renDy3D.AddActor(sourceAo.actor)

renWin.AddRenderer(renSurf)
renWin.AddRenderer(renDy2D)
renWin.AddRenderer(renDy3D)

""" Move the sensor """

rang = np.arange(-40, 41, dtype=float)
position = np.vstack((rang/20,
                      np.ones(len(rang)),
                      np.ones(len(rang))*2)).T
lookat = np.vstack((rang/40,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

for i, (pos, lka) in enumerate(zip(position, lookat)):
    di.set_sensor_orientation(pos, lka)
    di.Modified()
    iren.Render()
    iren.Start()
    time.sleep(.1)


"""
surf = vtk.vtkSurfaceReconstructionFilter()
surf.SetInputConnection(fpc.GetOutputPort())

cf = vtk.vtkContourFilter()
cf.SetInputConnection(surf.GetOutputPort())
cf.SetValue(0, 0.0)

reverse = vtk.vtkReverseSense()
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

sro.ren.AddActor(surfaceActor)
"""

"""
# We will now create a nice looking mesh by wrapping the edges in tubes,
# and putting fat spheres at the points.
extract = vtk.vtkExtractEdges()
extract.SetInputConnection(delny.GetOutputPort())
tubes = vtk.vtkTubeFilter()
tubes.SetInputConnection(extract.GetOutputPort())
tubes.SetRadius(0.01)
tubes.SetNumberOfSides(6)
mapEdges = vtk.vtkPolyDataMapper()
mapEdges.SetInputConnection(tubes.GetOutputPort())
edgeActor = vtk.vtkActor()
edgeActor.SetMapper(mapEdges)
edgeActor.GetProperty().SetColor(peacock)
edgeActor.GetProperty().SetSpecularColor(1, 1, 1)
edgeActor.GetProperty().SetSpecular(0.3)
edgeActor.GetProperty().SetSpecularPower(20)
edgeActor.GetProperty().SetAmbient(0.2)
edgeActor.GetProperty().SetDiffuse(0.8)

ball = vtk.vtkSphereSource()
ball.SetRadius(0.02)
ball.SetThetaResolution(12)
ball.SetPhiResolution(12)
balls = vtk.vtkGlyph3D()
balls.SetInputConnection(delny.GetOutputPort())
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
"""