import vtk
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np

from timeit import default_timer as timer
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
sourceAo.actor.GetProperty().SetOpacity(0.2)

di = mabdi.FilterDepthImage(offscreen=True, name='sensor')
di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects(di)
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

surf = mabdi.FilterDepthImageToSurface()
surf.SetInputConnection(di.GetOutputPort())
surfAo = mabdi.VTKPolyDataActorObjects(surf)
surfAo.actor.GetProperty().SetPointSize(1.5)
surfAo.actor.GetProperty().SetColor(red)
surfAo.actor.GetProperty().SetOpacity(1.0)

mesh = mabdi.FilterWorldMesh()
mesh.SetInputConnection(surf.GetOutputPort())
meshAo = mabdi.VTKPolyDataActorObjects(mesh)
meshAo.actor.GetProperty().SetColor(salmon)
meshAo.actor.GetProperty().SetOpacity(0.2)

sdi = mabdi.FilterDepthImage(offscreen=False, name='simulated sensor')
sdi.set_polydata(mesh)
sdiAo = mabdi.VTKImageActorObjects(sdi)
sdiAo.mapper.SetColorWindow(1.0)
sdiAo.mapper.SetColorLevel(0.5)

classifier = mabdi.FilterClassifier()
classifier.AddInputConnection(0, di.GetOutputPort())
classifier.AddInputConnection(1, sdi.GetOutputPort())
classifier.Update()

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
renScenario.AddActor(cameraActor)
renScenario.AddActor(sourceAo.actor)
renScenario.AddActor(surfAo.actor)
renScenario.AddActor(meshAo.actor)

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
# renWin.AddRenderer(renSensor)
# renWin.AddRenderer(renSSensor)

iren.Initialize()

""" Move the sensor """

rang = np.arange(-40, 41, 2, dtype=float)
position = np.vstack((rang/20,
                      np.ones(len(rang)),
                      np.ones(len(rang))*2)).T
lookat = np.vstack((rang/40,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

# mesh.clear_world_mesh()
# mesh.Update()
# sdi.UpdateInformation()
for i, (pos, lka) in enumerate(zip(position, lookat)):
    logging.info('START LOOP')
    start = timer()

    di.set_sensor_orientation(pos, lka)
    sdi.set_sensor_orientation(pos, lka)

    print "di.Modified()"
    di.Modified()

    print "sdi.Modified()"
    sdi.Modified()

    print "classifier.Update()"
    classifier.Update()

    print "mesh.Update()"
    mesh.Update()

    print "iren.Render()"
    iren.Render()

    iren.Start()

    end = timer()
    logging.info('END LOOP time {:.4f} seconds'.format(end - start))

