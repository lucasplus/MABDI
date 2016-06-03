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


class VTKWindowToMovie(object):

    def __init__(self, vtk_render_window):

        self._vtk_render_window = vtk_render_window

        self._ims = []

        ffmpegwriter = animation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                        comment='Movie support!')
        self._writer = ffmpegwriter(fps=1, metadata=metadata)

    def grab_frame(self):
        logging.debug('')
        start = timer()

        # get the image
        # have to crate a new instance of vtkWindowToImageFilter each time unfortunately
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self._vtk_render_window)
        window_to_image_filter.Update()
        inp = window_to_image_filter.GetOutput()

        # append it to instance memory
        im = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars()).reshape(480*1, 640*2, 3)
        self._ims.append(im)

        end = timer()
        logging.debug('VTKWindowToMovie time {:.4f} seconds'.format(end - start))

    def save(self):
        # http://matplotlib.org/examples/animation/moviewriter.html
        fig = plt.figure(figsize=(16, 6), dpi=100)
        with self._writer.saving(fig, "writer_test.mp4", 100):
            for i, im in enumerate(self._ims):
                logging.info('VTKWindowToMovie {} of {}'.format(i+1, len(self._ims)))
                plt.imshow(im, origin='lower', interpolation='none')
                plt.axis('off')
                self._writer.grab_frame()
        print fig.dpi
        print fig.get_size_inches()*fig.dpi


