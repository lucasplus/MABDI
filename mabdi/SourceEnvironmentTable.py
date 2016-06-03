import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import logging
from timeit import default_timer as timer


class SourceEnvironmentTable(VTKPythonAlgorithmBase):
    """
    Custom vtk filter for creating and controlling an environment called "table"

    The table environment consists of a floor, table, and 2 cups.
    """

    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkPolyData')
        self._floor = None
        self._table = None
        self._left_cup = None
        self._right_cup = None

        self._floor_flag = True
        self._table_flag = True
        self._left_cup_flag = True
        self._right_cup_flag = True

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        append = vtk.vtkAppendPolyData()

        # floor
        if self._floor_flag:
            self._floor = vtk.vtkCubeSource()
            self._floor.SetCenter(0, .05, 0)
            self._floor.SetXLength(10.0)
            self._floor.SetYLength(0.1)
            self._floor.SetZLength(10.0)
            append.AddInputConnection(self._floor.GetOutputPort())

        # table
        if self._table_flag:
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
            append.AddInputConnection(self._table.GetOutputPort())

        # left cup
        if self._left_cup_flag:
            self._left_cup = vtk.vtkCylinderSource()
            self._left_cup.SetCenter(-.75/4, .75+(.12/2), 0.0)
            self._left_cup.SetHeight(.12)
            self._left_cup.SetRadius(.06/2)
            append.AddInputConnection(self._left_cup.GetOutputPort())

        # right cup
        if self._right_cup_flag:
            self._right_cup = vtk.vtkCylinderSource()
            self._right_cup.SetCenter(.75/4, .75+(.12/2), 0.0)
            self._right_cup.SetHeight(.12)
            self._right_cup.SetRadius(.06/2)
            append.AddInputConnection(self._right_cup.GetOutputPort())

        append.Update()

        # output
        info = outInfo.GetInformationObject(0)
        output = vtk.vtkPolyData.GetData(info)
        output.ShallowCopy(append.GetOutput())

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1

    def set_object_state(self, object_name='default', state='default'):
        """
        Add or remove objects from the environment.
        :param object_name: Name of object to change the state of.
        :param state: Have the object in the environment?
        """
        if state == 'default' or object_name == 'default':
            return 1

        if object_name == 'floor':
            self._floor_flag = state
        elif object_name == 'table':
            self._table_flag = state
        elif object_name == 'left_cup':
            self._left_cup_flag = state
        elif object_name == 'right_cup':
            self._right_cup_flag = state
        else:
            return 1

        self.Modified()

