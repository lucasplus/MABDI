import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.util.colors import eggshell, slate_grey_light, red, yellow, salmon
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

from MabdiUtilities import DebugTimeVTKFilter

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

from itertools import cycle

from timeit import default_timer as timer
import logging


class FilterWorldMesh(VTKPythonAlgorithmBase):
    def __init__(self, color=False):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkPolyData',
                                        nOutputPorts=1, outputType='vtkPolyData')

        self._color = color

        self._worldmesh = vtk.vtkAppendPolyData()

        # colormap for changing polydata on every iteration
        # http://matplotlib.org/examples/color/colormaps_reference.html
        if self._color:
            gist_rainbow_r = plt.cm.get_cmap(name='gist_rainbow_r')
            mycm = gist_rainbow_r(range(160, 260, 5))[:, 0:3]
            self._colorcycle = cycle(mycm)

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # input polydata
        # have to make a copy otherwise polys will not show up in the render
        # even though GetNumberOfCells() says they should be there
        tmp = vtk.vtkPolyData.GetData(inInfo[0])
        inp = vtk.vtkPolyData()
        inp.ShallowCopy(tmp)

        # change color of all cells
        if self._color:
            ncells = inp.GetNumberOfCells()
            c = self._colorcycle.next()
            vtkarray = dsa.numpyTovtkDataArray(np.tile(c, (ncells, 1)))
            inp.GetCellData().SetScalars(vtkarray)

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
