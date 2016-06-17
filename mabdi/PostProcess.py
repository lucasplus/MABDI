import sys

import vtk
from vtk.util import numpy_support

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from timeit import default_timer as timer
import logging


class PostProcess(object):
    """
    Handle creating movies and figures
    """

    def __init__(self, movie=None,
                 scenario_render_window=None,
                 filter_classifier=None,
                 length_of_path=None,
                 file_prefix=None):
        """
        Create movies, plots, and stats of the MABDI execution
        :param scenario_render_window: vtkRenderWindow where the scenario view is rendered
        :param length_of_path: number of points in the path, for initialization purposes
        :param file_prefix: prefix to append to file name
        :param movie: dictionary with values
          * movie['scenario'] - default=True - whatever is on the scenario_render_window
          * movie['depth_images'] - default=True - depth images from FilterClassifier
          * movie['plots'] - default=False - number of elements
          * movie['fps'] - default=2 - frames per second
        :return:
        """

        # we will use this for any file we save
        self._file_prefix = file_prefix

        # movie dictionary defaults
        movie = {} if not movie else movie
        movie['scenario'] = True if 'scenario' not in movie else movie['scenario']
        movie['depth_images'] = True if 'depth_images' not in movie else movie['depth_images']
        movie['plots'] = False if 'plots' not in movie else movie['plots']
        movie['fps'] = 2 if 'fps' not in movie else movie['fps']
        self._movie = movie

        if movie['scenario'] and scenario_render_window:
            self._vtk_render_window = scenario_render_window
            self._ims_scenario = []
        else:
            logging.critical('Problem with movie[\'scenario\'] and scenario_render_window')
            sys.exit()

        if movie['depth_images'] and filter_classifier:
            self._filter_classifier = filter_classifier
            self._filter_classifier.set_postprocess(True)
            self._ims_d_images = []
        else:
            logging.critical('Problem with movie[\'depth_images\'] and filter_classifier')
            sys.exit()

        # initialize containers for images
        if length_of_path:
            self._ims_initialized = True
            self._count = -1
            dim = self._get_scenario_image().GetDimensions()
            self._ims_scenario = [np.zeros((dim[1], dim[0], 3)) for i in range(length_of_path)]
            self._ims_d_images = [(np.zeros((640, 480, 3)),
                                   np.zeros((640, 480, 3)),
                                   np.zeros((640, 480, 1))) for i in range(length_of_path)]
        else:
            self._ims_initialized = False
            self._count = None

        try:
            ffmpegwriter = animation.writers['ffmpeg']
        except KeyError:
            logging.critical('ffmpeg not found, please install')
            raise
        self._writer = ffmpegwriter(fps=movie['fps'])

    def collect_info(self):
        logging.info('')
        start = timer()

        i = 0
        if self._ims_initialized:
            self._count += 1
            i = self._count

        # scenario - get the image from the renderer
        inp = self._get_scenario_image()
        dim = inp.GetDimensions()
        im = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars()).reshape(dim[1], dim[0], 3)
        if self._ims_initialized:
            self._ims_scenario[i] = im
        else:
            self._ims_scenario.append(im)

        ims = self._filter_classifier.get_depth_images()
        if self._ims_initialized:
            self._ims_d_images[i] = ims
        else:
            self._ims_d_images.append(ims)

        end = timer()
        logging.info('PostProcess time {:.4f} seconds'.format(end - start))
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
            for i, (im_s, im_c) in enumerate(zip(self._ims_scenario, self._ims_d_images)):
                logging.debug('PostProcessing movie frame {} of {}'.format(i+1, len(self._ims_scenario)))
                ax1.imshow(im_s, origin='lower', interpolation='none')
                ax2.imshow(im_c[0], origin='lower', interpolation='none')
                ax3.imshow(im_c[1], origin='lower', interpolation='none')
                ax4.imshow(im_c[2], origin='lower', interpolation='none', cmap='Greys_r')
                self._writer.grab_frame()
        logging.info('Figure dpi {}, Figure pixel size {}'
                     .format(fig.dpi, fig.get_size_inches()*fig.dpi))

    def _get_scenario_image(self):
        window_to_image_filter = vtk.vtkWindowToImageFilter()
        window_to_image_filter.SetInput(self._vtk_render_window)
        window_to_image_filter.Update()
        return window_to_image_filter.GetOutput()
