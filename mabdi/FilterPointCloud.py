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

        self._sizex = []
        self._sizey = []
        self._viewport = []

        self._display_pts = []
        self._viewport_pts = []
        self._world_pts = []
        self._polydata = vtk.vtkPolyData()

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # input to filter, vtkImageData
        inp = vtk.vtkImageData.GetData(inInfo[0])

        if (self._sizex, self._sizey, self._viewport) != (inp.sizex, inp.sizey, inp.viewport):
            print "hi"
            # save the new size and viewport
            (self._sizex, self._sizey) = (inp.sizex, inp.sizey)
            self._viewport = inp.viewport
            # new display points
            self._display_pts = np.ones((2, self._sizex * self._sizey))
            count = 0
            for i in np.arange(self._sizey):
                for j in np.arange(self._sizex):
                    self._display_pts[0, count] = j
                    self._display_pts[1, count] = i
                    count += 1
            # new viewport points
            self._viewport_pts = np.ones((4, self._display_pts.shape[1]))
            self._viewport_pts[0, :] = 2.0 * (self._display_pts[0, :] - self._sizex * self._viewport[0]) / (
                self._sizex * (self._viewport[2] - self._viewport[0])) - 1.0
            self._viewport_pts[1, :] = 2.0 * (self._display_pts[1, :] - self._sizey * self._viewport[1]) / (
                self._sizey * (self._viewport[3] - self._viewport[1])) - 1.0
            # new world points (of the right size)
            self._world_pts = np.ones(self._viewport_pts.shape)
            # initialize vtkPolyData
            points = vtk.vtkPoints()
            vertices = vtk.vtkCellArray()
            for i in np.arange(self._world_pts.shape[1]):
                pt_id = points.InsertNextPoint(self._world_pts[0:3, i])
                vertices.InsertNextCell(1)
                vertices.InsertCellPoint(pt_id)
            self._polydata.SetPoints(points)
            self._polydata.SetVerts(vertices)

        # update the viewport points
        self._viewport_pts[2, :] = numpy_support.vtk_to_numpy(inp.GetPointData().GetScalars())

        # project to world coordinates
        self._world_pts = np.dot(inp.tmat, self._viewport_pts)
        self._world_pts = self._world_pts / self._world_pts[3]

        # update polydata
        points = vtk.vtkPoints()
        vtkarray = dsa.numpyTovtkDataArray(self._world_pts[0:3, :].T)
        points.SetData(vtkarray)
        self._polydata.SetPoints(points)
        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self._polydata)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
