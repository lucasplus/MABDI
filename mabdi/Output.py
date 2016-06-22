import sys
import ntpath

from itertools import cycle

import vtk
from vtk.util import numpy_support

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from timeit import default_timer as timer
import logging


class MovieNamesList(object):
    movie_names = []

    @staticmethod
    def write_movie_list(file_prefix):
        logging.info('Writing txt files with all movies that were made.')

        filename = file_prefix + 'movie_name_list.txt'
        filenamebn = ntpath.basename(filename)
        myfile = open(filename, 'w')

        for name in MovieNamesList.movie_names:
            basename = ntpath.basename(name)
            myfile.write('file ' + '\'' + basename + '\'' + '\n')

        myfile.write('\n')
        myfile.write('Command: \n')
        video_name = ntpath.basename(file_prefix) + 'movies_combined.avi'
        myfile.write('ffmpeg -f concat -i ' + filenamebn + ' -c copy ' + video_name)

        myfile.close()


class RenderWindowToAvi(object):
    ntimes = 0

    def __init__(self, render_window, file_prefix, fps=2):

        self._movie_name = file_prefix + \
                           'movie_' + str(RenderWindowToAvi.ntimes) + '.avi'
        MovieNamesList.movie_names.append(self._movie_name)
        RenderWindowToAvi.ntimes += 1

        self._render_window = render_window
        render_window.AddObserver('RenderEvent', self._render_cb)

        self._ims = []

        try:
            ffmpegwriter = animation.writers['ffmpeg']
        except KeyError:
            logging.critical('ffmpeg not found, please install')
            raise
        self._writer = ffmpegwriter(fps=fps)

    def _render_cb(self, obj, env):
        im = get_image_from_render_window(vtk_render_window=self._render_window)
        self._ims.append(im)

    def save_movie(self):
        logging.info('Number of frames {}'.format(len(self._ims)))

        fig = plt.figure(frameon=False, figsize=(40, 20), dpi=100)
        ax = plt.imshow(self._ims[0], origin='lower', interpolation='none')
        plt.axis('off', frameon=False)
        plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)

        with self._writer.saving(fig, self._movie_name, 100):
            for i, im in enumerate(self._ims):
                start = timer()
                ax.set_data(im)
                self._writer.grab_frame()
                end = timer()
                logging.debug('Processed movie frame {} of {}, {} seconds'
                              .format(i + 1, len(self._ims), end - start))


class PostProcess(object):
    """
    Handle creating movies and figures
    """

    def __init__(self, movie=None,
                 scenario_render_window=None,
                 filter_classifier=None,
                 length_of_path=None,
                 global_mesh=None,
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
          * movie['param_fps'] - default=2 - frames per second
        :return:
        """

        # we will use this for any file we save
        self._movie_name = file_prefix + 'pp_movie.avi'
        MovieNamesList.movie_names.append(self._movie_name)

        if length_of_path:
            self._np = length_of_path

        # movie dictionary defaults
        movie = {} if not movie else movie
        movie.setdefault('scenario', True)
        movie.setdefault('depth_images', True)
        movie.setdefault('plots', False)
        movie.setdefault('param_fps', 2)
        self._movie = movie

        if self._movie['scenario']:
            if scenario_render_window:
                self._vtk_render_window = scenario_render_window
                self._ims_scenario = []
            else:
                logging.critical('Need scenario_render_window for movie[\'scenario\'] option.')
                sys.exit()

        if self._movie['depth_images']:
            if filter_classifier:
                self._filter_classifier = filter_classifier
                self._filter_classifier.set_postprocess(True)
                self._ims_d_images = []
            else:
                logging.critical('Need filter_classifier for movie[\'depth_images\'] option.')
                sys.exit()

        if self._movie['plots']:
            if global_mesh:
                self._global_mesh = global_mesh
                self._global_mesh_nc = []
            else:
                logging.critical('Need global_mesh for movie[\'plots\'] option.')
                sys.exit()

        try:
            ffmpegwriter = animation.writers['ffmpeg']
        except KeyError:
            logging.critical('ffmpeg not found, please install')
            raise
        self._writer = ffmpegwriter(fps=movie['param_fps'])

    def collect_info(self):
        logging.info('')
        start = timer()

        # scenario - get the image from the renderer
        if self._movie['scenario']:
            im = get_image_from_render_window(vtk_render_window=self._vtk_render_window)
            self._ims_scenario.append(im)

        # depth images
        if self._movie['depth_images']:
            ims = self._filter_classifier.get_depth_images()
            self._ims_d_images.append(ims)

        if self._movie['plots']:
            self._global_mesh_nc.append(
                self._global_mesh.GetOutputDataObject(0).GetNumberOfCells())

        end = timer()
        logging.info('PostProcess time {:.4f} seconds'.format(end - start))
        return

    def save_movie(self):
        logging.info('Number of frames {}'.format(len(self._ims_scenario)))
        # http://matplotlib.org/examples/animation/moviewriter.html

        # figure number of rows
        # fnr = sum((self._movie['scenario'],  # to go back to old layout uncomment
        #            self._movie['depth_images'],
        #            self._movie['plots']))
        fnr = sum((self._movie['scenario'],  # to go back to old layout uncomment
                   self._movie['depth_images']))

        fig = plt.figure(frameon=False, figsize=(40, 10 * fnr), dpi=100)

        axs, rn = [], 0  # list of axes, row number
        if self._movie['scenario']:
            # handle = plt.subplot2grid((fnr, 3), (rn, 0), colspan=3)  # to go back to old layout uncomment
            handle = plt.subplot2grid((fnr, 3), (rn, 0), colspan=2)
            handle.axis('off', frameon=False)
            tmp = handle.imshow(self._ims_scenario[0], origin='lower', interpolation='none')
            axs.append(tmp)
        if self._movie['depth_images']:
            rn += 1
            handle = [plt.subplot2grid((fnr, 3), (rn, 0)),
                      plt.subplot2grid((fnr, 3), (rn, 1)),
                      plt.subplot2grid((fnr, 3), (rn, 2))]
            for i, hand in enumerate(handle):
                hand.axis('off', frameon=False)
                if i is not 2:
                    tmp = hand.imshow(self._ims_d_images[1][i], origin='lower', interpolation='none')
                else:
                    tmp = hand.imshow(self._ims_d_images[1][i], origin='lower', interpolation='none', cmap='Greys_r')
                axs.append(tmp)
        if self._movie['plots']:
            rn += 1
            # axs.append(plt.subplot2grid((fnr, 3), (rn, 0)))  # to go back to old layout uncomment
            axs.append(plt.subplot2grid((fnr, 3), (0, 2)))
            ax = axs[-1]

            ax.plot(np.arange(1, len(self._global_mesh_nc)+1), np.array(self._global_mesh_nc))
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            ax.clear()
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

            plt.title('Size of global mesh')
            plt.xlabel('iteration')
            plt.ylabel('number of elements')
            plt.grid(True)

            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
                item.set_fontsize(15)
            for item in (ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(10)
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # adjust padding
        if self._movie['plots']:
            pad = 5.08
        else:
            pad = 0.0
        plt.tight_layout(pad=pad, h_pad=0.0, w_pad=0.0)

        with self._writer.saving(fig, self._movie_name, 100):
            for i, (im_s, im_d) in enumerate(zip(self._ims_scenario, self._ims_d_images)):
                start = timer()

                axscy = cycle(axs)
                if self._movie['scenario']:
                    axscy.next().set_data(im_s)
                if self._movie['depth_images']:
                    axscy.next().set_data(im_d[0])
                    axscy.next().set_data(im_d[1])
                    axscy.next().set_data(im_d[2])
                if self._movie['plots']:
                    axscy.next().plot(np.arange(1, i + 1 + 1),
                                      np.array(self._global_mesh_nc[0:i + 1]),
                                      '-*', color='b',
                                      markersize=10, markerfacecolor='g')

                self._writer.grab_frame()

                end = timer()
                logging.debug('Processed movie frame {} of {}, {} seconds'
                              .format(i + 1, len(self._ims_scenario), end - start))

        logging.info('Figure dpi {}, Figure pixel size {}'
                     .format(fig.dpi, fig.get_size_inches() * fig.dpi))

        del self._ims_scenario, self._ims_d_images


def get_image_from_render_window(vtk_render_window):
    """
    Get a screenshot of the given vtkRenderWindow in the form a numpy array
    :param vtk_render_window: The render window
    :return: numpy array of size (width, height, 3)
    """
    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(vtk_render_window)
    window_to_image_filter.Update()
    vtkim = window_to_image_filter.GetOutput()
    dim = vtkim.GetDimensions()
    return numpy_support.vtk_to_numpy(vtkim.GetPointData().GetScalars()).reshape(dim[1], dim[0], 3)
