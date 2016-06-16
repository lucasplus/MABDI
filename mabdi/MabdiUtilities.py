import vtk
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

from timeit import default_timer as timer
import logging

import numpy as np
import matplotlib
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

""" VTK container classes """


class VTKPolyDataActorObjects(object):

    def __init__(self, in_source):
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(in_source.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)


class VTKImageActorObjects(object):

    def __init__(self, in_source):
        self.mapper = vtk.vtkImageMapper()
        self.mapper.SetInputConnection(in_source.GetOutputPort())

        self.actor = vtk.vtkActor2D()
        self.actor.SetMapper(self.mapper)


""" Debug helper classes """


class DebugTimeVTKFilter(object):

    def __init__(self, in_filter):
        self._start = 0
        self._end = 0
        self._name = in_filter.GetClassName()

        in_filter.AddObserver('StartEvent', self.start_event_callback)
        in_filter.AddObserver('EndEvent', self.end_event_callback)

    def start_event_callback(self, obj, env):
        self._start = timer()

    def end_event_callback(self, obj, env):
        self._end = timer()
        logging.debug('{} execution time {:.4f} seconds'.format(
            self._name,
            self._end - self._start))


""" Visualize helpers """


class PostProcess(object):
    """
    Handle creating movies and figures
    """

    def __init__(self, vtk_render_window=None, length_of_path=None, file_prefix=None):

        self._vtk_render_window = vtk_render_window
        self._file_prefix = file_prefix

        self._ims_scenario = []
        self._ims_classifier = []

        # TODO check if user has ffmpeg
        ffmpegwriter = animation.writers['ffmpeg']
        self._writer = ffmpegwriter(fps=2)

        self._filter_classifier = []

        self._vtk_render_window.AddObserver('RenderEvent', self.collect_info_cb)

    def collect_info_cb(self, obj, ev):
        self.collect_info()

    def collect_info(self):
        logging.info('')
        start = timer()

        # get the image
        # have to crate a new instance of vtkWindowToImageFilter each time unfortunately
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self._vtk_render_window)
        window_to_image_filter.Update()
        inp = window_to_image_filter.GetOutput()

        # append it to instance memory
        im = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars()).reshape(480*1, 640*2, 3)
        self._ims_scenario.append(im)

        self._ims_classifier.append(self._filter_classifier.postprocess_function())

        end = timer()
        logging.info('PostProcess time {:.4f} seconds'.format(end - start))
        return

    def register_filter_classifier(self, filter_classifier):
        self._filter_classifier = filter_classifier
        self._filter_classifier.set_postprocess(True)
        return

    def save_movie(self):
        logging.info('Number of frames {}'.format(len(self._ims_scenario)))
        # http://matplotlib.org/examples/animation/moviewriter.html
        fig = plt.figure(frameon=False, figsize=(20*2, 10*2), dpi=100)
        ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=3)
        ax2 = plt.subplot2grid((2, 3), (1, 0))
        ax3 = plt.subplot2grid((2, 3), (1, 1))
        ax4 = plt.subplot2grid((2, 3), (1, 2))
        ax1.axis('off', frameon=False)
        ax2.axis('off', frameon=False)
        ax3.axis('off', frameon=False)
        ax4.axis('off', frameon=False)
        plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)  # adjust padding
        with self._writer.saving(fig, self._file_prefix + "movie.mp4", 100):
            for i, (im_s, im_c) in enumerate(zip(self._ims_scenario, self._ims_classifier)):
                logging.debug('PostProcessing movie frame {} of {}'.format(i+1, len(self._ims_scenario)))
                ax1.imshow(im_s, origin='lower', interpolation='none')
                ax2.imshow(im_c[0], origin='lower', interpolation='none')
                ax3.imshow(im_c[1], origin='lower', interpolation='none')
                ax4.imshow(im_c[2], origin='lower', interpolation='none', cmap='Greys_r')
                self._writer.grab_frame()
        logging.info('Figure dpi {}, Figure pixel size {}'
                     .format(fig.dpi, fig.get_size_inches()*fig.dpi))



