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

        """ Configuration parameters """

        mabdi_param = {} if not mabdi_param else mabdi_param
        mabdi_param.setdefault('depth_image_size', (640, 480))
        mabdi_param.setdefault('farplane_threshold', 1.0)  # see FilterDepthImageToSurface
        mabdi_param.setdefault('convolution_threshold', 0.01)  # see FilterDepthImageToSurface
        mabdi_param.setdefault('classifier_threshold', 0.01)  # see FilterClassifier

        sim_param = {} if not sim_param else sim_param
        sim_param.setdefault('environment_name', 'table')
        sim_param.setdefault('stanford_bunny_nbunnies', 1)
        sim_param.setdefault('dynamic_environment', [(-1, -1)])  # values that won't do anything, (frame_number, object_id)
        sim_param.setdefault('dynamic_environment_init_state', None)
        sim_param.setdefault('path_name', 'helix_table_ub')
        sim_param.setdefault('path_nsteps', 20)
        sim_param.setdefault('noise', False)  # you can also specify a number instead of a bool, default is 0.002
        sim_param.setdefault('interactive', False)
        self._sim_param = sim_param

        output = {} if not output else output
        output.setdefault('folder_name', None)
        output.setdefault('movie', False)
        output.setdefault('movie_fps', 3)
        output.setdefault('movie_savefig_at_frame', ())
        output.setdefault('source_obs_position', None)
        output.setdefault('source_obs_lookat', None)
        output.setdefault('movie_preflight', False)
        output.setdefault('movie_postflight', False)
        output.setdefault('preflight_nsteps', 30)
        output.setdefault('postflight_nsteps', 30)
        output.setdefault('preflight_fps', 3)
        output.setdefault('postflight_fps', 3)
        output.setdefault('path_flight', 'helix_survey_ub')
        output.setdefault('save_global_mesh', False)
        self._output = output

        self._file_prefix = mabdi.get_file_prefix(output['folder_name'])

        """ Filters and sources (this block is basically the core of MABDI) """

        if sim_param['environment_name'] is 'table':
            self.source = mabdi.SourceEnvironmentTable()
        elif sim_param['environment_name'] is 'stanford_bunny':
            self.source = mabdi.SourceStandfordBunny(sim_param['stanford_bunny_nbunnies'])
        self.di = mabdi.FilterDepthImage(offscreen=True,
                                         name='sensor',
                                         noise=sim_param['noise'],
                                         depth_image_size=mabdi_param['depth_image_size'])
        self.sdi = mabdi.FilterDepthImage(offscreen=True,
                                          name='simulated sensor',
                                          depth_image_size=mabdi_param['depth_image_size'])
        self.classifier = mabdi.FilterClassifier()
        self.surf = mabdi.FilterDepthImageToSurface(
            param_farplane_threshold=mabdi_param['farplane_threshold'],
            param_convolution_threshold=mabdi_param['convolution_threshold'])
        self.mesh = mabdi.FilterWorldMesh(color=True)

        self.di.set_polydata(self.source)

        self.sdi.set_polydata_empty()  # because the world mesh hasn't been initialized yet

        self.classifier.AddInputConnection(0, self.di.GetOutputPort())
        self.classifier.AddInputConnection(1, self.sdi.GetOutputPort())

        self.surf.SetInputConnection(self.classifier.GetOutputPort())

        self.mesh.SetInputConnection(self.surf.GetOutputPort())

        self.sdi.set_polydata(self.mesh)

        # get bounds of the source without the floor
        self.source.bounds, self.source.position, self.source.lookat = \
            self._find_bounds_and_observation_position_lookat(self.source)
        if output['source_obs_position']:
            self.source.position = output['source_obs_position']
        if output['source_obs_lookat']:
            self.source.lookat = output['source_obs_lookat']

        """ Sensor path """

        self.position, self.lookat = \
            mabdi.SensorPath.create_sensor_path(name=sim_param['path_name'],
                                                nsteps=sim_param['path_nsteps'],
                                                bounds=self.source.bounds)

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
            vtk_algorithm.set_object_state(object_id='floor', state=False)
            vtk_algorithm.Update()
            bounds = vtk_algorithm.GetOutputDataObject(0).GetBounds()
            vtk_algorithm.set_object_state(object_id='floor', state=True)
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

    def _create_survey_movie(self,
                             survey_source=True,
                             survey_mesh=False,
                             nsteps=None,
                             fps=2):
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
            mabdi.SensorPath.create_sensor_path(name=self._output['path_flight'],
                                                nsteps=nsteps)

        if survey_mesh:
            ren.AddActor(meshAo.actor)
            sourceAo.actor.GetProperty().SetOpacity(0.2)
            # sourceAo.actor.VisibilityOff()

        # iren.Start()
        movie = mabdi.RenderWindowToAvi(renWin, self._file_prefix, fps=fps, savefig_at_frame=self._output['movie_savefig_at_frame'])
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
        logging.info('')

        # self.iren.Start()

        if self._output['movie_preflight']:
            self._create_survey_movie(survey_source=True,
                                      survey_mesh=False,
                                      nsteps=self._output['preflight_nsteps'],
                                      fps=self._output['preflight_fps'])

        if self._output['movie']:
            pp = mabdi.PostProcess(
                movie={'scenario': True,
                       'depth_images': True,
                       'plots': True,
                       'param_fps': self._output['movie_fps']},
                scenario_render_window=self.renWin,
                filter_classifier=self.classifier,
                length_of_path=len(self.position),
                global_mesh=self.mesh,
                file_prefix=self._file_prefix,
                savefig_at_frame=self._output['movie_savefig_at_frame'])

        # if a dynamic environment, set the initial state
        deintst = self._sim_param['dynamic_environment_init_state']
        if deintst:
            for i, obj_state in enumerate(deintst):
                self.source.set_object_state(object_id=i, state=obj_state)
            self.source.Update()
        # dynamic environment controls
        de = self._sim_param['dynamic_environment']  # dynamic environment
        defn, deobjn = zip(*de)  # frame number, objnumber

        for i, (pos, lka) in enumerate(zip(self.position, self.lookat)):
            logging.debug('START MAIN LOOP')
            start = timer()

            self.di.set_sensor_orientation(pos, lka)
            self.sdi.set_sensor_orientation(pos, lka)

            if i in defn:
                ind = defn.index(i)
                self.source.set_object_state(object_id=deobjn[ind], state=True)
                self.source.Update()

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
            self.iren.Start()
            end = timer()
            logging.debug('END MAIN LOOP time {:.4f} seconds'.format(end - start))

        if self._output['movie']:
            pp.save_movie()

        if self._output['movie_postflight']:
            self._create_survey_movie(survey_source=True,
                                      survey_mesh=True,
                                      nsteps=self._output['postflight_nsteps'],
                                      fps=self._output['postflight_fps'])
            # mabdi.MovieNamesList.write_movie_list(self._file_prefix) # has a bug

        if self._output['save_global_mesh']:
            plywriter = vtk.vtkPLYWriter()
            plywriter.SetFileName(self._file_prefix + 'global_mesh.ply')
            plywriter.SetInputConnection(self.mesh.GetOutputPort())
            plywriter.Write()

        pp.save_plots()

        """ Exit gracefully """

        self.di.kill_render_window()
        self.sdi.kill_render_window()

        self.iren.GetRenderWindow().Finalize()
        self.iren.TerminateApp()

        del self.renWin, self.iren
