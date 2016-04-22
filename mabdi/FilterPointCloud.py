import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np

from timeit import default_timer as timer
import logging


class FilterPointCloud(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkPolyData')

        self.__sizex = []
        self.__sizey = []

        self.__display_pts = []
        self.__viewport_pts = []
        self.__world_pts = []
        self.__polydata = vtk.vtkPolyData()

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # all the depth values
        inp = vtk.vtkImageData.GetData(inInfo[0])
        depth = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars())

        """ START _initialize_containers """

        # save the new size
        (self.__sizex, self.__sizey) = (inp.sizex, inp.sizey)
        # new display points
        self.__display_pts = np.ones((2, self.__sizex * self.__sizey))
        count = 0
        for i in np.arange(self.__sizey):
            for j in np.arange(self.__sizex):
                self.__display_pts[0, count] = j
                self.__display_pts[1, count] = i
                count += 1
        # new viewport points
        viewport = inp.viewport
        self.__viewport_pts = np.ones((4, self.__display_pts.shape[1]))
        self.__viewport_pts[0, :] = 2.0 * (self.__display_pts[0, :] - self.__sizex * viewport[0]) / (
            self.__sizex * (viewport[2] - viewport[0])) - 1.0
        self.__viewport_pts[1, :] = 2.0 * (self.__display_pts[1, :] - self.__sizey * viewport[1]) / (
            self.__sizey * (viewport[3] - viewport[1])) - 1.0
        # new world points (of the right size)
        self.__world_pts = np.ones(self.__viewport_pts.shape)
        # initialize vtkPolyData
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for i in np.arange(self.__world_pts.shape[1]):
            pt_id = points.InsertNextPoint(self.__world_pts[0:3, i])
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pt_id)
        self.__polydata.SetPoints(points)
        self.__polydata.SetVerts(vertices)

        """ END _initialize_containers """

        # update the viewport points, check to see if render window size has changed
        self.__viewport_pts[2, :] = depth

        # project to world coordinates
        self.__world_pts = np.dot(inp.tmat, self.__viewport_pts)
        self.__world_pts = self.__world_pts / self.__world_pts[3]

        # update polydata
        points = vtk.vtkPoints()
        vtkarray = dsa.numpyTovtkDataArray(self.__world_pts[0:3, :].T)
        points.SetData(vtkarray)
        self.__polydata.SetPoints(points)
        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self.__polydata)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
