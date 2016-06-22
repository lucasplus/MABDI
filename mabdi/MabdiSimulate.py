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

    def __init__(self,
                 mabdi_param=None,
                 sim_param=None,
                 output=None):
        """
        Initialize all the vtkPythonAlgorithms that make up MABDI
        :param sim_param:
          * sim_param['shape'] - default='line' - 'line' 'circle'
          * sim_param['length'] - default=20 - length of sim_param
        :param output:
          * output['movie'] - default=False - Create a movie with
          the scenario view, and depth images after the simulation runs.
        """

        start_time = time.strftime('%m-%d_%H-%M-%S_')
        self._file_prefix = '../output/' + start_time
        if not os.path.exists('../output/'):
            os.makedirs('../output/')

        """ Configuration parameters """

        mabdi_param = {} if not mabdi_param else mabdi_param
        mabdi_param.setdefault('depth_image_size', (640, 480))

        sim_param = {} if not sim_param else sim_param
        sim_param.setdefault('path_name', 'helix_table_ub')
        sim_param.setdefault('path_nsteps', 20)
        sim_param.setdefault('interactive', False)
        self._sim_param = sim_param

        output = {} if not output else output
        output.setdefault('movie', False)
        output.setdefault('movie_preflight', False)
        output.setdefault('movie_postflight', False)
        self._output = output

        """ Filters and sources (this block is basically the core of MABDI) """

        self.source = mabdi.SourceEnvironmentTable()
        self.di = mabdi.FilterDepthImage(offscreen=True,
                                         name='sensor',
                                         noise=False,
                                         depth_image_size=mabdi_param['depth_image_size'])
        self.sdi = mabdi.FilterDepthImage(offscreen=True,
                                          name='simulated sensor',
                                          depth_image_size=mabdi_param['depth_image_size'])
        self.classifier = mabdi.FilterClassifier()
        self.surf = mabdi.FilterDepthImageToSurface()
        self.mesh = mabdi.FilterWorldMesh(color=True)

        # get bounds of source

        self.di.set_polydata(self.source)

        self.sdi.set_polydata_empty()  # because the world mesh hasn't been initialized yet

        self.classifier.AddInputConnection(0, self.di.GetOutputPort())
        self.classifier.AddInputConnection(1, self.sdi.GetOutputPort())

        self.surf.SetInputConnection(self.classifier.GetOutputPort())

        self.mesh.SetInputConnection(self.surf.GetOutputPort())

        self.sdi.set_polydata(self.mesh)

        # get bounds of the source without the floor
        self.source.set_object_state(object_name='floor', state=False)
        self.source.Update()
        self.source_bounds = self.source.GetOutputDataObject(0).GetBounds()
        self.source.set_object_state(object_name='floor', state=True)
        self.source.Update()

        self.source.bounds, self.source.position, self.source.lookat = \
            self._find_bounds_and_observation_position_lookat(self.source)

        """ Sensor path """

        self.position, self.lookat = \
            self._create_sensor_path(name=sim_param['path_name'],
                                     nsteps=sim_param['path_nsteps'],
                                     bounds=self.source_bounds)

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
        renScenario.GetActiveCamera().SetPosition(self.source.position)
        renScenario.GetActiveCamera().SetFocalPoint(self.source.lookat)

        # surf
        renSurf = vtk.vtkRenderer()
        renSurf.SetBackground(eggshell)
        renSurf.SetViewport(1.0 / 2.0, 0.0, 2.0 / 2.0, 1.0)
        self._add_sensor_visualization(renSurf)
        renSurf.AddActor(sourceAo.actor)
        renSurf.AddActor(surfAo.actor)
        renSurf.GetActiveCamera().SetPosition(self.source.position)
        renSurf.GetActiveCamera().SetFocalPoint(self.source.lookat)

        self.renWin.AddRenderer(renScenario)
        self.renWin.AddRenderer(renSurf)

        self.iren.Initialize()

        return

    @staticmethod
    def _find_bounds_and_observation_position_lookat(vtk_algorithm):
        bounds = []
        if callable(vtk_algorithm.set_object_state):
            vtk_algorithm.set_object_state(object_name='floor', state=False)
            vtk_algorithm.Update()
            bounds = vtk_algorithm.GetOutputDataObject(0).GetBounds()
            vtk_algorithm.set_object_state(object_name='floor', state=True)
            vtk_algorithm.Update()
        else:
            bounds = vtk_algorithm.GetOutputDataObject(0).GetBounds()

        # all these values were found very empirically
        padc = (3.0, 5.0, 8.0)  # pad coefficient
        position = (padc[0] * bounds[1] + 4.0,
                    padc[1] * bounds[3],
                    padc[2] * bounds[5] * 2.0 + 3.0)
        lookat = (-padc[0] * bounds[1],
                  padc[1] * bounds[3] * -0.3,
                  -padc[2] * bounds[5])

        return bounds, position, lookat

    def _create_sensor_path(self, name=None, nsteps=None, bounds=None):
        """
        Create specific sensor paths as specified by path_name, Path names
        ending in "_ub" use the given bounds when calculating the path.
        :param name: Name of specific path
        :param name: Name of steps, although each path will define a default
        :param bounds: Bounds of thing to create a path around
        :return:
        """

        # reasonable default
        if not bounds:
            bounds = (-2.0, 2.0, 0.0, 2.0, -2.0, 2.0)

        b = bounds
        if name == 'helix_table_ub':
            if not nsteps: nsteps = 20
            xd = b[1] - b[0]
            zd = b[5] - b[4]
            xd += 3.0
            zd += 3.0
            position = self._create_path({'name': 'helix',
                                          'nsteps': nsteps,
                                          'helix_nspins': 2,
                                          'helix_x_diameter': xd,
                                          'helix_z_diameter': zd,
                                          'helix_y_start_end': (0.75, 1.25)})
            lookat = self._create_path({'name': 'line',
                                        'nsteps': nsteps,
                                        'line_start': (0.0, 0.4, 0.0),
                                        'line_end': (0.0, 0.6, 0.0)})
        elif name == 'helix_survey_ub':
            if not nsteps: nsteps = 20
            xd = b[1] - b[0]
            zd = b[5] - b[4]
            xd += 3.0
            zd += 3.0
            position = self._create_path({'name': 'helix',
                                          'nsteps': nsteps,
                                          'helix_nspins': 1,
                                          'helix_x_diameter': xd,
                                          'helix_z_diameter': zd + 0.5,
                                          'helix_y_start_end': (0.75, 1.5)})
            lookat = self._create_path({'name': 'line',
                                        'nsteps': nsteps,
                                        'line_start': (0.0, 0.1, 0.0),
                                        'line_end': (0.0, 0.3, 0.0)})

        return position, lookat

    @staticmethod
    def _create_path(path_param=None):
        """
        (nsteps, 3) = path.shape
        :param path_param: dictionary of parameters that describe the desired path
        :return: position and lookat
        """

        path_param = {} if not path_param else path_param
        path_param.setdefault('name', 'line')
        path_param.setdefault('nsteps', 20)

        path_param.setdefault('line_start', (-1.5, 1.0, 1.5))
        path_param.setdefault('line_end', (1.5, 1.0, 1.5))

        path_param.setdefault('helix_nspins', 1)
        path_param.setdefault('helix_x_diameter', 6.0)
        path_param.setdefault('helix_z_diameter', 6.0)
        path_param.setdefault('helix_y_start_end', (0.5, 1.5))

        t = np.linspace(0, 1, num=path_param['nsteps'])

        if path_param['name'] == 'line':
            p0 = path_param['line_start']
            p1 = path_param['line_end']
            path = np.vstack((p0[0] + (p1[0] - p0[0]) * t,
                              p0[1] + (p1[1] - p0[1]) * t,
                              p0[2] + (p1[2] - p0[2]) * t)).T
        elif path_param['name'] == 'helix':
            # http://mathworld.wolfram.com/Helix.html
            x_radius = path_param['helix_x_diameter'] / 2
            z_radius = path_param['helix_z_diameter'] / 2
            nspins = path_param['helix_nspins']
            yse = path_param['helix_y_start_end']
            path = np.vstack((x_radius * np.sin(t * np.pi * 2 * nspins),
                              yse[0] + (yse[1] - yse[0]) * t,
                              z_radius * np.cos(t * np.pi * 2 * nspins))).T

        return path

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

    def _create_survey_movie(self, survey_source=True, survey_mesh=False):
    #def _create_survey_movie(self):
        """
        Note: This method assumes the source is centered on the xz plane
        """

        sourceAo = mabdi.VTKPolyDataActorObjects(self.source)
        sourceAo.actor.GetProperty().SetColor(slate_grey_light)
        sourceAo.actor.GetProperty().SetSpecularColor(1, 1, 1)
        sourceAo.actor.GetProperty().SetSpecular(0.3)
        sourceAo.actor.GetProperty().SetSpecularPower(20)
        sourceAo.actor.GetProperty().SetAmbient(0.2)
        sourceAo.actor.GetProperty().SetDiffuse(0.8)
        # sourceAo.actor.GetProperty().SetOpacity(0.2)

        meshAo = mabdi.VTKPolyDataActorObjects(self.mesh)
        meshAo.actor.GetProperty().SetColor(salmon)
        meshAo.actor.GetProperty().SetColor(slate_grey_light)
        meshAo.actor.GetProperty().SetSpecularColor(1, 1, 1)
        meshAo.actor.GetProperty().SetSpecular(0.3)
        meshAo.actor.GetProperty().SetSpecularPower(20)
        meshAo.actor.GetProperty().SetAmbient(0.2)
        meshAo.actor.GetProperty().SetDiffuse(0.8)
        # meshAo.actor.GetProperty().SetOpacity(0.5)

        renWin = vtk.vtkRenderWindow()
        renWin.SetSize(640, 480)
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        ren = vtk.vtkRenderer()
        ren.SetBackground(eggshell)

        ren.AddActor(sourceAo.actor)

        renWin.AddRenderer(ren)

        iren.Initialize()

        cam = ren.GetActiveCamera()

        position, lookat = \
            self._create_sensor_path(name='helix_survey_ub', nsteps=3)

        movie = mabdi.RenderWindowToAvi(renWin, self._file_prefix, fps=30)

        if survey_mesh:
            ren.AddActor(meshAo.actor)
            sourceAo.actor.GetProperty().SetOpacity(0.2)
            # sourceAo.actor.VisibilityOff()

        for i, (pos, lka) in enumerate(zip(position, lookat)):
            cam.SetPosition(pos)
            cam.SetFocalPoint(lka)
            iren.Render()

        movie.save_movie()

        iren.GetRenderWindow().Finalize()
        iren.TerminateApp()
        del iren, ren, renWin

        return

    def run(self):
        logging.info('running simulation')

        # self.iren.Start()

        if self._output['movie_preflight']:
            self._create_survey_movie(survey_source=True, survey_mesh=False)

        if self._output['movie']:
            pp = mabdi.PostProcess(
                movie={'scenario': True,
                       'depth_images': True,
                       'plots': True,
                       'param_fps': 30},
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

            if self._output['movie']:
                pp.collect_info()

            if self._sim_param['interactive']:
                self.iren.Start()

            end = timer()
            logging.debug('END MAIN LOOP time {:.4f} seconds'.format(end - start))

        if self._output['movie']:
            pp.save_movie()

        if self._output['movie_postflight']:
            self._create_survey_movie(survey_source=True, survey_mesh=True)
            mabdi.MovieNamesList.write_movie_list(self._file_prefix)

        """ Exit gracefully """

        self.di.kill_render_window()
        self.sdi.kill_render_window()

        self.iren.GetRenderWindow().Finalize()
        self.iren.TerminateApp()

        del self.renWin, self.iren
