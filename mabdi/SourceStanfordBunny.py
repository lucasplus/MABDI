import os

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import logging
from timeit import default_timer as timer


class SourceStandfordBunny(VTKPythonAlgorithmBase):
    """
    Custom vtk filter for creating and controlling an environment called "standford bunny"
    # http://graphics.stanford.edu/data/3Dscanrep/
    The standford bunny environment can consist of multiple bunnies
    """

    def __init__(self, nbunnies=1):

        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkPolyData')

        self._bunny_ply_file = os.path.join(os.path.dirname(__file__),
                                            'stanford_bunny.ply')

        self._nbunnies = nbunnies

        dis = 1.5
        ytrans = -0.2
        if nbunnies is 1:
            trans = [(0.0, ytrans, 0.0)]
        elif nbunnies is 2:
            trans = [(-dis, ytrans, 0.0),
                     (dis, ytrans, 0.0)]
        elif nbunnies is 3:
            trans = [(-dis, ytrans, 0.0),
                     (0.0, ytrans, 0.0),
                     (dis, ytrans, 0.0)]
        elif nbunnies is 4:
            trans = [(-dis, ytrans, 0.0),
                     (0.0, ytrans, dis),
                     (dis, ytrans, 0.0),
                     (0.0, ytrans, -dis)]

        self.objects = {'bunny_' + str(x): True for x in range(nbunnies)}
        self._polydata = {'bunny_'+str(x): vtk.vtkTransformPolyDataFilter() for x in range(nbunnies)}
        self._keys = self.objects.keys()
        for i, (key, tfilter) in enumerate(self._polydata.iteritems()):
            reader = vtk.vtkPLYReader()
            reader.SetFileName(self._bunny_ply_file)
            transform = vtk.vtkTransform()
            # transform.Scale(10.0, 10.0, 10.0)
            transform.Translate(trans[i])
            tfilter.SetInputConnection(reader.GetOutputPort())
            tfilter.SetTransform(transform)

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

        # bunny
        # reader = vtk.vtkPLYReader()
        # reader.SetFileName(self._bunny_ply_file)
        # transform = vtk.vtkTransform()
        # transform.Scale(10.0, 10.0, 10.0)
        # tf = vtk.vtkTransformPolyDataFilter()
        # tf.SetInputConnection(reader.GetOutputPort())
        # tf.SetTransform(transform)
        for i, (key, tfilter) in enumerate(self._polydata.iteritems()):
            if self.objects[key]:
                append.AddInputConnection(tfilter.GetOutputPort())

        append.Update()

        # output
        info = outInfo.GetInformationObject(0)
        output = vtk.vtkPolyData.GetData(info)
        output.ShallowCopy(append.GetOutput())

        end = timer()
        logging.info('Execution time {:.4f} seconds'.format(end - start))

        return 1

    def set_object_state(self, object_id='default', state='default'):
        """
        Add or remove objects from the environment.
        :param object_id: Name of object to change the state of.
        :param state: Have the object in the environment?
        """
        if state == 'default' or object_id == 'default':
            return 1

        if object_id == 'floor':
            self._floor = state
            self.Modified()
            return

        keys = self.objects.keys()
        self.objects[keys[object_id]] = state
        self.Modified()
