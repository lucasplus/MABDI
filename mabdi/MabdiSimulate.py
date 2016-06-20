import os

import vtk
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon, blue, hot_pink
from vtk.util import numpy_support

import mabdi

import numpy as np

import logging
from timeit import default_timer as timer

import time


class MabdiSimulate(object):
    """
    Simulate MABDI working in a defined environment with the sensor
    following a defined path.

    Flags for describing the environment, path, and visualization
    """

    def __init__(self, path=None, postprocess=None, interactive=False):
        """
        Initialize all the vtkPythonAlgorithms that make up MABDI
        :param path:
          * path['shape'] - default='line' - 'line' 'circle'
          * path['length'] - default=20 - length of path
        :param postprocess:
          * postprocess['movie'] - default=False - Create a movie with
          the scenario view, and depth images after the simulation runs.
        """

        start_time = time.strftime('%m-%d_%H-%M-%S_')
        self._file_prefix = '../output/' + start_time
        if not os.path.exists('../output/'):
            os.makedirs('../output/')

        """ Configuration parameters """

        path = {} if not path else path
        path['shape'] = 'line' if 'shape' not in path else path['shape']
        path['length'] = 20 if 'length' not in path else path['length']

        postprocess = {} if not postprocess else postprocess
        postprocess['movie'] = False if 'movie' not in postprocess else postprocess['movie']
        self._postprocess = postprocess

        self._interactive = interactive

        """ Sensor path """

        self.position, self.lookat = \
            self._create_sensor_path(path['shape'], path['length'])

        """ Filters and sources (this block is basically the core of MABDI) """

        self.source = mabdi.SourceEnvironmentTable()
        self.di = mabdi.FilterDepthImage(offscreen=True, name='sensor', noise=True)
        self.sdi = mabdi.FilterDepthImage(offscreen=True, name='simulated sensor')
        self.classifier = mabdi.FilterClassifier()
        self.surf = mabdi.FilterDepthImageToSurface()
        self.mesh = mabdi.FilterWorldMesh(color=True)

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

        surfAo = mabdi.VTKPolyDataActorObjects(self.surf)
        surfAo.actor.GetProperty().SetColor(red)
        surfAo.actor.GetProperty().SetOpacity(1.0)

        meshAo = mabdi.VTKPolyDataActorObjects(self.mesh)
        meshAo.actor.GetProperty().SetColor(salmon)
        meshAo.actor.GetProperty().SetOpacity(0.5)

        """ Render objects """

        self.renWin = vtk.vtkRenderWindow()
        self.renWin.SetSize(640 * 2, 480 * 1)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        # scenario
        renScenario = vtk.vtkRenderer()
        renScenario.SetBackground(eggshell)
        renScenario.SetViewport(0.0 / 2.0, 0.0, 1.0 / 2.0, 1.0)
        self._add_sensor_visualization(renScenario)
        renScenario.AddActor(sourceAo.actor)
        renScenario.AddActor(surfAo.actor)
        renScenario.AddActor(meshAo.actor)
        renScenario.GetActiveCamera().SetPosition(2.0, 7.0, 8.0)
        renScenario.GetActiveCamera().SetFocalPoint(0.0, 1.0, 0.0)

        # surf
        renSurf = vtk.vtkRenderer()
        renSurf.SetBackground(eggshell)
        renSurf.SetViewport(1.0 / 2.0, 0.0, 2.0 / 2.0, 1.0)
        self._add_sensor_visualization(renSurf)
        renSurf.AddActor(sourceAo.actor)
        renSurf.AddActor(surfAo.actor)
        renSurf.GetActiveCamera().SetPosition(2.0, 7.0, 8.0)
        renSurf.GetActiveCamera().SetFocalPoint(0.0, 1.0, 0.0)

        self.renWin.AddRenderer(renScenario)
        self.renWin.AddRenderer(renSurf)

        self.iren.Initialize()

        return

    def _create_sensor_path(self, pname, nsteps):

        rang = np.linspace(0, 1, num=nsteps)
        if pname == 'line':
            length = 3
            position = np.vstack((length * (2 * rang - 1),
                                  np.ones(len(rang)),
                                  1.5 * np.ones(len(rang)))).T
            lookat = np.vstack((length * (2 * rang - 1),
                                .5 * np.ones(len(rang)),
                                np.zeros(len(rang)))).T
        elif pname == 'circle':
            radius = 3
            nspins = 2
            position = np.vstack((radius * np.sin(rang * np.pi * 2 * nspins),
                                  np.ones(len(rang)),
                                  radius * np.cos(rang * np.pi * 2 * nspins))).T
            lookat = np.vstack((np.zeros(len(rang)),
                                np.ones(len(rang)) * .5,
                                np.zeros(len(rang)))).T

        return position, lookat

    def _add_sensor_visualization(self, vtk_renderer):
        """
        Add visualization specific to the sensor
        :param vtk_renderer: The vtkRenderer where the actors will be added.
        """

        """ Frustum of the sensor """

        cameraActor = vtk.vtkCameraActor()
        cameraActor.SetCamera(self.di.get_vtk_camera())
        cameraActor.SetWidthByHeightRatio(self.di.get_width_by_height_ratio())
        cameraActor.GetProperty().SetColor(blue)

        """ Path of the sensor """

        npts = self.position.shape[0]

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(npts)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(npts)
        for i, pos in enumerate(self.position):
            points.SetPoint(i, pos)
            lines.InsertCellPoint(i)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)

        polymapper = vtk.vtkPolyDataMapper()
        polymapper.SetInputData(polydata)
        polymapper.Update()

        actor = vtk.vtkActor()
        actor.SetMapper(polymapper)
        actor.GetProperty().SetColor(blue)
        actor.GetProperty().SetOpacity(0.5)

        ball = vtk.vtkSphereSource()
        ball.SetRadius(0.02)
        ball.SetThetaResolution(12)
        ball.SetPhiResolution(12)
        balls = vtk.vtkGlyph3D()
        balls.SetInputData(polydata)
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

        """ Add to the given renderer """

        vtk_renderer.AddActor(spcActor)
        vtk_renderer.AddActor(cameraActor)
        vtk_renderer.AddActor(actor)

    def run(self):
        logging.info('running simulation')

        self.iren.Start()

        if self._postprocess['movie']:
            pp = mabdi.PostProcess(
                movie={'scenario': True,
                       'depth_images': True,
                       'plots': True},
                scenario_render_window=self.renWin,
                filter_classifier=self.classifier,
                length_of_path=len(self.position),
                global_mesh=self.mesh,
                file_prefix=self._file_prefix)

        for i, (pos, lka) in enumerate(zip(self.position, self.lookat)):
            logging.debug('START MAIN LOOP')
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

            if self._postprocess['movie']:
                pp.collect_info()

            if self._interactive:
                self.iren.Start()

            end = timer()
            logging.debug('END MAIN LOOP time {:.4f} seconds'.format(end - start))

        if self._postprocess['movie']:
            pp.save_movie()

        """ Exit gracefully """

        self.di.kill_render_window()
        self.sdi.kill_render_window()

        self.iren.GetRenderWindow().Finalize()
        self.iren.TerminateApp()

        del self.renWin, self.iren
