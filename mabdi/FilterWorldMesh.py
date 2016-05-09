import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

from MabdiUtilities import DebugTimeVTKFilter

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

from timeit import default_timer as timer
import logging


class FilterWorldMesh(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkPolyData')

        self._worldmesh = vtk.vtkAppendPolyData()
        self._cleared = False

    def clear_world_mesh(self):
        del self._worldmesh
        self._worldmesh = vtk.vtkAppendPolyData()
        self._cleared = True
        return 1

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # input polydata
        # have to make a copy otherwise polys will not show up in the render
        # even though GetNumberOfCells() says they should be there
        # ugly if statement is so that clear_world_mesh() works properly
        # Has something to do with the input to FilterWorldMesh is also a
        # function of it's output. I need to draw it out.
        tmp = vtk.vtkPolyData.GetData(inInfo[0])
        inp = vtk.vtkPolyData()
        if not self._cleared:
            inp.ShallowCopy(tmp)
        else:
            self._cleared = False

        # add to world mesh
        self._worldmesh.AddInputData(inp)
        self._worldmesh.Update()

        logging.info('Number of cells: in = {} total = {}'
                     .format(inp.GetNumberOfCells(),
                             self._worldmesh.GetOutput().GetNumberOfCells()))

        # output world mesh
        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self._worldmesh.GetOutput())

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
