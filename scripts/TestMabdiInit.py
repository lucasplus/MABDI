import vtk
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np
import matplotlib.pyplot as plt

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
di = mabdi.FilterDepthImage(offscreen=True, name='sensor')
sdi = mabdi.FilterDepthImage(offscreen=True, name='simulated sensor')
classifier = mabdi.FilterClassifier()
surf = mabdi.FilterDepthImageToSurface()
mesh = mabdi.FilterWorldMesh(color=False)

sourceAo = mabdi.VTKPolyDataActorObjects(source)
sourceAo.actor.GetProperty().SetColor(slate_grey_light)
sourceAo.actor.GetProperty().SetOpacity(0.2)

di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects(di)
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

sdi.set_polydata_empty()  # because the world mesh hasn't been initialized yet
sdiAo = mabdi.VTKImageActorObjects(sdi)
sdiAo.mapper.SetColorWindow(1.0)
sdiAo.mapper.SetColorLevel(0.5)

classifier.AddInputConnection(0, di.GetOutputPort())
classifier.AddInputConnection(1, sdi.GetOutputPort())

surf.SetInputConnection(classifier.GetOutputPort())
surfAo = mabdi.VTKPolyDataActorObjects(surf)
surfAo.actor.GetProperty().SetColor(red)
surfAo.actor.GetProperty().SetOpacity(1.0)

mesh.SetInputConnection(surf.GetOutputPort())
meshAo = mabdi.VTKPolyDataActorObjects(mesh)
meshAo.actor.GetProperty().SetColor(salmon)
meshAo.actor.GetProperty().SetOpacity(0.5)
sdi.set_polydata(mesh)

""" Render objects """

renWin = vtk.vtkRenderWindow()
renWin.SetSize(640*2, 480*1)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renWinD = vtk.vtkRenderWindow()
renWinD.SetSize(640*2, 480*1)
irenD = vtk.vtkRenderWindowInteractor()
irenD.SetRenderWindow(renWinD)

# scenario
renScenario = vtk.vtkRenderer()
renScenario.SetBackground(eggshell)
renScenario.SetViewport(0.0 / 2.0, 0.0, 1.0 / 2.0, 1.0)
cameraActor = vtk.vtkCameraActor()
cameraActor.SetCamera(di.get_vtk_camera())
cameraActor.SetWidthByHeightRatio(di.get_width_by_height_ratio())
renScenario.AddActor(cameraActor)
renScenario.AddActor(sourceAo.actor)
renScenario.AddActor(surfAo.actor)
renScenario.AddActor(meshAo.actor)
renScenario.GetActiveCamera().SetPosition(2.0, 7.0, 8.0)
renScenario.GetActiveCamera().SetFocalPoint(0.0, 1.0, 0.0)

# surf
renSurf = vtk.vtkRenderer()
renSurf.SetBackground(eggshell)
renSurf.SetViewport(1.0 / 2.0, 0.0, 2.0 / 2.0, 1.0)
cameraActor = vtk.vtkCameraActor()
cameraActor.SetCamera(di.get_vtk_camera())
cameraActor.SetWidthByHeightRatio(di.get_width_by_height_ratio())
renSurf.AddActor(cameraActor)
renSurf.AddActor(sourceAo.actor)
renSurf.AddActor(surfAo.actor)
renSurf.GetActiveCamera().SetPosition(2.0, 7.0, 8.0)
renSurf.GetActiveCamera().SetFocalPoint(0.0, 1.0, 0.0)

# sensor output D
renSensor = vtk.vtkRenderer()
renSensor.SetViewport(0.0 / 2.0, 0.0, 1.0 / 2.0, 1.0)
renSensor.SetInteractive(0)
renSensor.AddActor(diAo.actor)

# simulated sensor output D
renSSensor = vtk.vtkRenderer()
renSSensor.SetViewport(1.0 / 2.0, 0.0, 2.0 / 2.0, 1.0)
renSSensor.SetInteractive(0)
renSSensor.AddActor(sdiAo.actor)

renWin.AddRenderer(renScenario)
renWin.AddRenderer(renSurf)

renWinD.AddRenderer(renSensor)
renWinD.AddRenderer(renSSensor)

iren.Initialize()
irenD.Initialize()

""" Move the sensor """

rang = np.arange(-40, 41, 5, dtype=float)
position = np.vstack((rang/10,
                      np.ones(len(rang)),
                      np.ones(len(rang))*1.5)).T
lookat = np.vstack((rang/15,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

iren.Start()

# wtm = mabdi.VTKWindowToMovie(renWin)

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

    print "irenD.Render()"
    irenD.Render()

    print "gm.grab_frame()"
    # wtm.grab_frame()

    # iren.Start()

    end = timer()
    logging.info('END LOOP time {:.4f} seconds'.format(end - start))

# wtm.save()

""" Exit gracefully """

di.kill_render_window()
sdi.kill_render_window()

iren.GetRenderWindow().Finalize()
irenD.GetRenderWindow().Finalize()
iren.TerminateApp()
irenD.TerminateApp()

del renWin, renWinD, iren, irenD


