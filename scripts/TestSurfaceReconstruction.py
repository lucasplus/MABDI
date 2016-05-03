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
