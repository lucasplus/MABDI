import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

from MabdiUtilities import DebugTimeVTKFilter

import numpy as np

from itertools import compress

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
        self._cells = []

        self._points = vtk.vtkPoints()
        self._polys = vtk.vtkCellArray()
        self._polydata = vtk.vtkPolyData()
        self._polydata.SetPoints(self._points)
        self._polydata.SetPolys(self._polys)
        #self._vgf = vtk.vtkVertexGlyphFilter()
        #DebugTimeVTKFilter(self._vgf)
        #self._vgf.SetInputData(self._polydata)

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
            (w, h) = (self._sizex, self._sizey)  # helper variables (width, height)
            # new display points (list of all pixel coordinates)
            self._display_pts = np.ones((2, w * h))
            self._display_pts[0, :], self._display_pts[1, :] = \
                zip(*[(j, i) for i in np.arange(h) for j in np.arange(w)])
            # new viewport points
            self._viewport_pts = np.ones((4, self._display_pts.shape[1]))
            self._viewport_pts[0, :] = 2.0 * (self._display_pts[0, :] - w * self._viewport[0]) / \
                (w * (self._viewport[2] - self._viewport[0])) - 1.0
            self._viewport_pts[1, :] = 2.0 * (self._display_pts[1, :] - h * self._viewport[1]) / \
                (h * (self._viewport[3] - self._viewport[1])) - 1.0
            # new world points (of the right size)
            self._world_pts = np.ones(self._viewport_pts.shape)
            # cells (list of predefined connectivity )
            nt = (2*w)*(h-1)  # number of triangles
            cells = np.zeros((3, nt), dtype=np.int)
            i = 0
            while i < (nt/2):
                if ((i+1) % w) != 0:
                    cells[:, 2*i] = (i, i+1, w+i)
                    cells[:, 2*i+1] = (i+1, w+i+1, w+i)
                i += 1
            index = np.where(cells.any(axis=0))[0]
            self._cells = cells[:, index]

        # update the viewport points
        self._viewport_pts[2, :] = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars())

        # project to world coordinates
        tstart = timer()
        self._world_pts = np.dot(inp.tmat, self._viewport_pts)
        self._world_pts = self._world_pts / self._world_pts[3]
        tend = timer()
        logging.debug('Project points {:.4f} seconds'.format(tend - tstart))

        # update polydata
        valid_index = self._viewport_pts[2, :] < 1.0

        tstart = timer()
        # points = vtk.vtkPoints()
        # triangles = vtk.vtkCellArray()
        tend = timer()
        logging.debug('Initialize vtk objects {:.4f} seconds'.format(tend - tstart))

        # http://stackoverflow.com/a/21448251/4068274
        tstart = timer()
        for i in list(compress(xrange(len(valid_index)), valid_index)):
            self._points.InsertPoint(i, *self._world_pts[0:3, i])
        tend = timer()
        logging.debug('Points loop {:.4f} seconds'.format(tend - tstart))

        tstart = timer()
        for i in np.arange(self._cells.shape[1]):
            (tpt1, tpt2, tpt3) = self._cells[:, i]  # triangle points
            if valid_index[tpt1] and valid_index[tpt2] and valid_index[tpt3]:
                self._polys.InsertNextCell(3)
                self._polys.InsertCellPoint(tpt1)
                self._polys.InsertCellPoint(tpt2)
                self._polys.InsertCellPoint(tpt3)
        tend = timer()
        logging.debug('Polys loop {:.4f} seconds'.format(tend - tstart))

        plt.imshow(valid_index.reshape((self._sizey, self._sizex)), origin='lower')
        plt.show()

        tstart = timer()
        # self._polydata.SetPoints(points)
        # self._polydata.SetPolys(triangles)

        out = vtk.vtkPolyData.GetData(outInfo)
        # out.ShallowCopy(self._vgf.GetOutput())
        out.ShallowCopy(self._polydata)
        tend = timer()
        logging.debug('The rest {:.4f} seconds'.format(tend - tstart))

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1

"""
valid_pts_index = self._viewport_pts[2, :] < 1.0
vtkarray = dsa.numpyTovtkDataArray(self._world_pts[0:3, valid_pts_index].T)
self._points.SetData(vtkarray)
self._polydata.SetPoints(self._points)
self._vgf.Update()
"""