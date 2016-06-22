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

        self._objects = {'table': True,
                         'left_cup': True,
                         'right_cup': True}

        self._polydata = {'table': None,
                          'left_cup': None,
                          'right_cup': None}

        self._floor = True
        self._floor_polydata = None

    def RequestData(self, request, inInfo, outInfo):
        logging.info('')
        start = timer()

        append = vtk.vtkAppendPolyData()

        # floor
        if self._floor:
            self._floor_polydata = vtk.vtkCubeSource()
            self._floor_polydata.SetCenter(0, .05, 0)
            self._floor_polydata.SetXLength(10.0)
            self._floor_polydata.SetYLength(0.1)
            self._floor_polydata.SetZLength(10.0)
            append.AddInputConnection(self._floor_polydata.GetOutputPort())

        # table
        if self._objects['table']:
            table_leg_1 = vtk.vtkCubeSource()
            table_leg_1.SetCenter((1.0 / 2) - (.1 / 2), .75 / 2, (-.75 / 2) + (.1 / 2))
            table_leg_1.SetXLength(0.1)
            table_leg_1.SetYLength(0.75)
            table_leg_1.SetZLength(0.1)
            table_leg_2 = vtk.vtkCubeSource()
            table_leg_2.SetCenter((-1.0 / 2) + (.1 / 2), .75 / 2, (-.75 / 2) + (.1 / 2))
            table_leg_2.SetXLength(0.1)
            table_leg_2.SetYLength(0.75)
            table_leg_2.SetZLength(0.1)
            table_leg_3 = vtk.vtkCubeSource()
            table_leg_3.SetCenter((-1.0 / 2) + (.1 / 2), .75 / 2, (.75 / 2) - (.1 / 2))
            table_leg_3.SetXLength(0.1)
            table_leg_3.SetYLength(0.75)
            table_leg_3.SetZLength(0.1)
            table_leg_4 = vtk.vtkCubeSource()
            table_leg_4.SetCenter((1.0 / 2) - (.1 / 2), .75 / 2, (.75 / 2) - (.1 / 2))
            table_leg_4.SetXLength(0.1)
            table_leg_4.SetYLength(0.75)
            table_leg_4.SetZLength(0.1)
            table_top = vtk.vtkCubeSource()
            table_top.SetCenter(0.0, .75 - (.1 / 2), 0.0)
            table_top.SetXLength(1.0)
            table_top.SetYLength(0.1)
            table_top.SetZLength(0.75)
            self._polydata['table'] = vtk.vtkAppendPolyData()
            self._polydata['table'].AddInputConnection(table_leg_1.GetOutputPort())
            self._polydata['table'].AddInputConnection(table_leg_2.GetOutputPort())
            self._polydata['table'].AddInputConnection(table_leg_3.GetOutputPort())
            self._polydata['table'].AddInputConnection(table_leg_4.GetOutputPort())
            self._polydata['table'].AddInputConnection(table_top.GetOutputPort())
            append.AddInputConnection(self._polydata['table'].GetOutputPort())

        # left cup
        if self._objects['left_cup']:
            self._polydata['left_cup'] = vtk.vtkCylinderSource()
            self._polydata['left_cup'].SetCenter(-.75 / 4, .75 + (.12 / 2), 0.0)
            self._polydata['left_cup'].SetHeight(.12)
            self._polydata['left_cup'].SetRadius(.06 / 2)
            append.AddInputConnection(self._polydata['left_cup'].GetOutputPort())

        # right cup
        if self._objects['right_cup']:
            self._polydata['right_cup'] = vtk.vtkCylinderSource()
            self._polydata['right_cup'].SetCenter(.75 / 4, .75 + (.12 / 2), 0.0)
            self._polydata['right_cup'].SetHeight(.12)
            self._polydata['right_cup'].SetRadius(.06 / 2)
            append.AddInputConnection(self._polydata['right_cup'].GetOutputPort())

        append.Update()

        # output
        info = outInfo.GetInformationObject(0)
        output = vtk.vtkPolyData.GetData(info)
        output.ShallowCopy(append.GetOutput())

        end = timer()
        logging.info('Execution time {:.4f} seconds'.format(end - start))

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
            self._floor = state
        elif object_name in self._objects:
            self._objects[object_name] = state
        else:
            return 1

        self.Modified()
