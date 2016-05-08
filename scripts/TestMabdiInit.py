import vtk
from vtk.util.colors import eggshell, red, slate_grey_light
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
Script to test the simulated sensor output generated from rendering
the output of the surface reconstruction
Render Window top row
- [Scenario] renScenario; Interactive [source]
- [Sensor] renSensor; Not Interactive [di]
Render Window bottom row
- [Mesh] renMesh; Interactive
- [Simulated Sensor] renSSensor; Not Interactive [sdi]
"""

""" Filters and sources """

source = mabdi.SourceEnvironmentTable()
source.Update()
sourceAo = mabdi.VTKPolyDataActorObjects(source)
sourceAo.actor.SetMapper(sourceAo.mapper)
sourceAo.actor.GetProperty().SetColor(slate_grey_light)
sourceAo.actor.GetProperty().SetOpacity(0.5)

di = mabdi.FilterDepthImage(offscreen=False)
di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects(di)
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

surf = mabdi.FilterDepthImageToSurface()
surf.SetInputConnection(di.GetOutputPort())
surfAo = mabdi.VTKPolyDataActorObjects(surf)
surfAo.actor.GetProperty().SetPointSize(1.5)
surfAo.actor.GetProperty().SetColor(red)

sdi = mabdi.FilterDepthImage(offscreen=False)
sdi.set_polydata(surf)
sdiAo = mabdi.VTKImageActorObjects(sdi)
sdiAo.mapper.SetColorWindow(1.0)
sdiAo.mapper.SetColorLevel(0.5)

""" Render objects """

renWin = vtk.vtkRenderWindow()
renWin.SetSize(640*3, 480*1)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# scenario
renScenario = vtk.vtkRenderer()
renScenario.SetBackground(eggshell)
renScenario.SetViewport(0.0, 0.0, 1.0 / 3, 1.0)
cameraActor = vtk.vtkCameraActor()
cameraActor.SetCamera(di.get_vtk_camera())
cameraActor.SetWidthByHeightRatio(di.get_width_by_height_ratio())
renScenario.AddActor(sourceAo.actor)
renScenario.AddActor(surfAo.actor)
renScenario.AddActor(cameraActor)

# sensor output
renSensor = vtk.vtkRenderer()
renSensor.SetViewport(1.0 / 3, 0.0, 2.0 / 3, 1.0)
renSensor.SetInteractive(0)
renSensor.AddActor(diAo.actor)

# simulated sensor output
renSSensor = vtk.vtkRenderer()
renSSensor.SetViewport(2.0 / 3, 0.0, 3.0 / 3, 1.0)
renSSensor.SetInteractive(0)
renSSensor.AddActor(sdiAo.actor)

renWin.AddRenderer(renScenario)
renWin.AddRenderer(renSensor)
renWin.AddRenderer(renSSensor)

iren.Render()

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
    sdi.set_sensor_orientation(pos, lka)
    sdi.Modified()
    iren.Render()
    iren.Start()


