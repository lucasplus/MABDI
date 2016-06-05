
import vtk
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np

import logging
from timeit import default_timer as timer


class MabdiSimulate(object):
    """
    Simulate MABDI working in a defined environment with the sensor
    following a defined path.

    Flags for describing the environment, path, and visualization
    """
    def __init__(self):
        """
        Initialize all the vtkPythonAlgorithms that make up MABDI
        """

        """ Filters and sources """

        self.source = mabdi.SourceEnvironmentTable()
        self.di = mabdi.FilterDepthImage(offscreen=True, name='sensor')
        self.sdi = mabdi.FilterDepthImage(offscreen=True, name='simulated sensor')
        self.classifier = mabdi.FilterClassifier(visualize=False)
        self.surf = mabdi.FilterDepthImageToSurface()
        self.mesh = mabdi.FilterWorldMesh(color=False)

        self.di.set_polydata(self.source)

        self.sdi.set_polydata_empty()  # because the world mesh hasn't been initialized yet

        self.classifier.AddInputConnection(0, self.di.GetOutputPort())
        self.classifier.AddInputConnection(1, self.sdi.GetOutputPort())

        self.surf.SetInputConnection(self.classifier.GetOutputPort())

        self.mesh.SetInputConnection(self.surf.GetOutputPort())

        self.sdi.set_polydata(self.mesh)

        """ Actor objects """

        sourceAo = mabdi.VTKPolyDataActorObjects(self.source)
        sourceAo.actor.GetProperty().SetColor(slate_grey_light)
        sourceAo.actor.GetProperty().SetOpacity(0.2)

        diAo = mabdi.VTKImageActorObjects(self.di)
        diAo.mapper.SetColorWindow(1.0)
        diAo.mapper.SetColorLevel(0.5)

        sdiAo = mabdi.VTKImageActorObjects(self.sdi)
        sdiAo.mapper.SetColorWindow(1.0)
        sdiAo.mapper.SetColorLevel(0.5)

        surfAo = mabdi.VTKPolyDataActorObjects(self.surf)
        surfAo.actor.GetProperty().SetColor(red)
        surfAo.actor.GetProperty().SetOpacity(1.0)

        meshAo = mabdi.VTKPolyDataActorObjects(self.mesh)
        meshAo.actor.GetProperty().SetColor(salmon)
        meshAo.actor.GetProperty().SetOpacity(0.5)

        """ Render objects """

        self.renWin = vtk.vtkRenderWindow()
        self.renWin.SetSize(640*2, 480*1)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.renWinD = vtk.vtkRenderWindow()
        self.renWinD.SetSize(640*2, 480*1)
        self.irenD = vtk.vtkRenderWindowInteractor()
        self.irenD.SetRenderWindow(self.renWinD)

        # scenario
        renScenario = vtk.vtkRenderer()
        renScenario.SetBackground(eggshell)
        renScenario.SetViewport(0.0 / 2.0, 0.0, 1.0 / 2.0, 1.0)
        cameraActor = vtk.vtkCameraActor()
        cameraActor.SetCamera(self.di.get_vtk_camera())
        cameraActor.SetWidthByHeightRatio(self.di.get_width_by_height_ratio())
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
        cameraActor.SetCamera(self.di.get_vtk_camera())
        cameraActor.SetWidthByHeightRatio(self.di.get_width_by_height_ratio())
        renSurf.AddActor(cameraActor)
        renSurf.AddActor(sourceAo.actor)
        renSurf.AddActor(surfAo.actor)
        renSurf.GetActiveCamera().SetPosition(2.0, 7.0, 8.0)
        renSurf.GetActiveCamera().SetFocalPoint(0.0, 1.0, 0.0)

        # sensor out
        renSensor = vtk.vtkRenderer()
        renSensor.SetViewport(0.0 / 2.0, 0.0, 1.0 / 2.0, 1.0)
        renSensor.SetInteractive(0)
        renSensor.AddActor(diAo.actor)

        # simulated sensor output D
        renSSensor = vtk.vtkRenderer()
        renSSensor.SetViewport(1.0 / 2.0, 0.0, 2.0 / 2.0, 1.0)
        renSSensor.SetInteractive(0)
        renSSensor.AddActor(sdiAo.actor)

        self.renWin.AddRenderer(renScenario)
        self.renWin.AddRenderer(renSurf)

        self.renWinD.AddRenderer(renSensor)
        self.renWinD.AddRenderer(renSSensor)

        self.iren.Initialize()
        self.irenD.Initialize()

        return

    def run(self):
        logging.info('running simulation')

        rang = np.arange(-40, 41, 5, dtype=float)
        position = np.vstack((rang/10,
                              np.ones(len(rang)),
                              np.ones(len(rang))*1.5)).T
        lookat = np.vstack((rang/15,
                            np.ones(len(rang))*.5,
                            np.zeros(len(rang)))).T

        self.iren.Start()

        # wtm = mabdi.VTKWindowToMovie(renWin)

        for i, (pos, lka) in enumerate(zip(position, lookat)):
            logging.debug('START LOOP')
            start = timer()

            self.di.set_sensor_orientation(pos, lka)
            self.sdi.set_sensor_orientation(pos, lka)

            logging.debug('di.Modified()')
            self.di.Modified()

            logging.debug('sdi.Modified()')
            self.sdi.Modified()

            logging.debug('classifier.Update()')
            self.classifier.Update()

            logging.debug('mesh.Update()')
            self.mesh.Update()

            logging.debug('iren.Render()')
            self.iren.Render()

            logging.debug('irenD.Render()')
            self.irenD.Render()

            # logging.debug('wtm.grab_frame()')
            # wtm.grab_frame()

            # iren.Start()

            end = timer()
            logging.debug('END LOOP time {:.4f} seconds'.format(end - start))

        # wtm.save()

        """ Exit gracefully """

        self.di.kill_render_window()
        self.sdi.kill_render_window()

        self.iren.GetRenderWindow().Finalize()
        self.irenD.GetRenderWindow().Finalize()
        self.iren.TerminateApp()
        self.irenD.TerminateApp()

        del self.renWin, self.renWinD, self.iren, self.irenD

