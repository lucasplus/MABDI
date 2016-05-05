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

        self._points = vtk.vtkPoints()
        self._polys = vtk.vtkCellArray()
        self._polydata = vtk.vtkPolyData()
        self._polydata.SetPoints(self._points)
        self._polydata.SetPolys(self._polys)

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # input (vtkImageData)
        inp = vtk.vtkImageData.GetData(inInfo[0])

        # if the vtkImageData size has changed or this is the first time
        # save new size info and initialize containers
        if (self._sizex, self._sizey, self._viewport) != (inp.sizex, inp.sizey, inp.viewport):
            (self._sizex, self._sizey) = (inp.sizex, inp.sizey)
            self._viewport = inp.viewport
            self._init_containers()

        # add z values to viewport_pts based on incoming depth image
        self._viewport_pts[2, :] = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars())

        # project to world coordinates
        self._world_pts = np.dot(inp.tmat, self._viewport_pts)
        self._world_pts = self._world_pts / self._world_pts[3]

        # index to valid points
        valid_index = self._viewport_pts[2, :] < 1.0

        # update vtkPoints
        vtkarray = dsa.numpyTovtkDataArray(self._world_pts[0:3, :].T)
        self._points.SetData(vtkarray)

        # update output (vtkPolyData)
        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self._polydata)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1

    def _init_containers(self):
        logging.debug('Initializing arrays for projection calculation.')
        tstart = timer()

        # helper variables (width, height)
        (w, h) = (self._sizex, self._sizey)

        """ display points (list of all pixel coordinates) """

        self._display_pts = np.ones((2, w * h))
        self._display_pts[0, :], self._display_pts[1, :] = \
            zip(*[(j, i) for i in np.arange(h) for j in np.arange(w)])

        """ viewport points """
        # https://github.com/Kitware/VTK/blob/52d45496877b00852a08a5b9819d109c2fd9bfab/Rendering/Core/vtkCoordinate.h#L26

        self._viewport_pts = np.ones((4, self._display_pts.shape[1]))
        self._viewport_pts[0, :] = 2.0 * (self._display_pts[0, :] - w * self._viewport[0]) / \
            (w * (self._viewport[2] - self._viewport[0])) - 1.0
        self._viewport_pts[1, :] = 2.0 * (self._display_pts[1, :] - h * self._viewport[1]) / \
            (h * (self._viewport[3] - self._viewport[1])) - 1.0

        """ new world points (just initializing the container) """

        self._world_pts = np.ones(self._viewport_pts.shape)

        """ cells (list of triangles created by connecting neighbors in depth image space ) """

        # connectivity on the depth image is almost like a checkerboard pattern
        # except with two triangles in every checkerboard square
        nt = (2*w)*(h-1)  # number of triangles
        cells = np.zeros((3, nt), dtype=np.int)
        i = 0
        while i < (nt/2):
            if ((i+1) % w) != 0:  # if on the side of the image skip
                cells[:, 2*i] = (i, i+1, w+i)
                cells[:, 2*i+1] = (i+1, w+i+1, w+i)
            i += 1

        # remove columns with zeros (the ones we skipped in the while loop)
        index = np.where(cells.any(axis=0))[0]  # all columns that are non zero
        cells = cells[:, index]

        # turn our connectivity list into a vtk object (vtkCellArray)
        for tpt in cells.T:
            self._polys.InsertNextCell(3)
            self._polys.InsertCellPoint(tpt[0])
            self._polys.InsertCellPoint(tpt[1])
            self._polys.InsertCellPoint(tpt[2])
        self._polydata.SetPolys(self._polys)

        # time me
        tend = timer()
        logging.debug('Initializing arrays for projection calculation {:.4f} seconds'.format(tend - tstart))

