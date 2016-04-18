import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import logging
from timeit import default_timer as timer


class SourceEnvironmentTable(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkPolyData')
        self._floor = None
        self._table = None
        self._left_cup = None
        self._right_cup = None

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # floor
        self._floor = vtk.vtkCubeSource()
        self._floor.SetCenter(0, .05, 0)
        self._floor.SetXLength(10.0)
        self._floor.SetYLength(0.1)
        self._floor.SetZLength(10.0)

        # table
        table_leg_1 = vtk.vtkCubeSource()
        table_leg_1.SetCenter((1.0/2)-(.1/2), .75/2, (-.75/2)+(.1/2))
        table_leg_1.SetXLength(0.1)
        table_leg_1.SetYLength(0.75)
        table_leg_1.SetZLength(0.1)
        table_leg_2 = vtk.vtkCubeSource()
        table_leg_2.SetCenter((-1.0/2)+(.1/2), .75/2, (-.75/2)+(.1/2))
        table_leg_2.SetXLength(0.1)
        table_leg_2.SetYLength(0.75)
        table_leg_2.SetZLength(0.1)
        table_leg_3 = vtk.vtkCubeSource()
        table_leg_3.SetCenter((-1.0/2)+(.1/2), .75/2, (.75/2)-(.1/2))
        table_leg_3.SetXLength(0.1)
        table_leg_3.SetYLength(0.75)
        table_leg_3.SetZLength(0.1)
        table_leg_4 = vtk.vtkCubeSource()
        table_leg_4.SetCenter((1.0/2)-(.1/2), .75/2, (.75/2)-(.1/2))
        table_leg_4.SetXLength(0.1)
        table_leg_4.SetYLength(0.75)
        table_leg_4.SetZLength(0.1)
        table_top = vtk.vtkCubeSource()
        table_top.SetCenter(0.0, .75-(.1/2), 0.0)
        table_top.SetXLength(1.0)
        table_top.SetYLength(0.1)
        table_top.SetZLength(0.75)
        self._table = vtk.vtkAppendPolyData()
        self._table.AddInputConnection(table_leg_1.GetOutputPort())
        self._table.AddInputConnection(table_leg_2.GetOutputPort())
        self._table.AddInputConnection(table_leg_3.GetOutputPort())
        self._table.AddInputConnection(table_leg_4.GetOutputPort())
        self._table.AddInputConnection(table_top.GetOutputPort())

        # left cup
        self._left_cup = vtk.vtkCylinderSource()
        self._left_cup.SetCenter(-.75/4, .75+(.12/2), 0.0)
        self._left_cup.SetHeight(.12)
        self._left_cup.SetRadius(.06/2)

        # left cup
        self._right_cup = vtk.vtkCylinderSource()
        self._right_cup.SetCenter(.75/4, .75+(.12/2), 0.0)
        self._right_cup.SetHeight(.12)
        self._right_cup.SetRadius(.06/2)

        # append
        append = vtk.vtkAppendPolyData()
        append.AddInputConnection(self._floor.GetOutputPort())
        append.AddInputConnection(self._table.GetOutputPort())
        append.AddInputConnection(self._left_cup.GetOutputPort())
        append.AddInputConnection(self._right_cup.GetOutputPort())
        append.Update()

        # output
        info = outInfo.GetInformationObject(0)
        output = vtk.vtkPolyData.GetData(info)
        output.ShallowCopy(append.GetOutput())

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
