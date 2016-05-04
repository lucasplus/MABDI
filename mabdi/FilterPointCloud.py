import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

from MabdiUtilities import DebugTimeVTKFilter

import numpy as np

import matplotlib.pyplot as plt

from timeit import default_timer as timer
import logging


class FilterPointCloud(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkPolyData')

        self._sizex = []
        self._sizey = []
        self._viewport = []

        self._display_pts = []
        self._viewport_pts = []
        self._world_pts = []

        self._points = vtk.vtkPoints()
        self._polydata = vtk.vtkPolyData()
        self._polydata.SetPoints(self._points)
        self._vgf = vtk.vtkVertexGlyphFilter()
        DebugTimeVTKFilter(self._vgf)
        self._vgf.SetInputData(self._polydata)

    def get_valid_pts_index(self):
        tmp_valid_pts_index = self._viewport_pts[2, :] < 1.0
        return tmp_valid_pts_index

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # input to filter, vtkImageData
        inp = vtk.vtkImageData.GetData(inInfo[0])

        if (self._sizex, self._sizey, self._viewport) != (inp.sizex, inp.sizey, inp.viewport):
            logging.debug('Initializing arrays for projection calculation.')
            # save the new size and viewport
            (self._sizex, self._sizey) = (inp.sizex, inp.sizey)
            self._viewport = inp.viewport
            # new display points (list of all pixel coordinates)
            self._display_pts = np.ones((2, self._sizex * self._sizey))
            self._display_pts[0, :], self._display_pts[1, :] = \
                zip(*[(j, i) for i in np.arange(self._sizey) for j in np.arange(self._sizex)])
            # new viewport points
            self._viewport_pts = np.ones((4, self._display_pts.shape[1]))
            self._viewport_pts[0, :] = 2.0 * (self._display_pts[0, :] - self._sizex * self._viewport[0]) / (
                self._sizex * (self._viewport[2] - self._viewport[0])) - 1.0
            self._viewport_pts[1, :] = 2.0 * (self._display_pts[1, :] - self._sizey * self._viewport[1]) / (
                self._sizey * (self._viewport[3] - self._viewport[1])) - 1.0
            # new world points (of the right size)
            self._world_pts = np.ones(self._viewport_pts.shape)

        # update the viewport points
        self._viewport_pts[2, :] = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars())

        # project to world coordinates
        self._world_pts = np.dot(inp.tmat, self._viewport_pts)
        self._world_pts = self._world_pts / self._world_pts[3]

        # update polydata
        valid_pts_index = self._viewport_pts[2, :] < 1.0
        vtkarray = dsa.numpyTovtkDataArray(self._world_pts[0:3, valid_pts_index].T)
        self._points.SetData(vtkarray)
        self._polydata.SetPoints(self._points)
        self._vgf.Update()

        plt.imshow(valid_pts_index.reshape((480, 640)), origin='lower')
        plt.show()

        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self._vgf.GetOutput())

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
