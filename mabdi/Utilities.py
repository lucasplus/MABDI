import vtk

from timeit import default_timer as timer
import logging

""" VTK container classes """


class VTKPolyDataActorObjects(object):

    def __init__(self, in_source):
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(in_source.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)


class VTKImageActorObjects(object):

    def __init__(self, in_source):
        self.mapper = vtk.vtkImageMapper()
        self.mapper.SetInputConnection(in_source.GetOutputPort())

        self.actor = vtk.vtkActor2D()
        self.actor.SetMapper(self.mapper)


""" Debug helper classes """


class DebugTimeVTKFilter(object):

    def __init__(self, in_filter):
        self._start = 0
        self._end = 0
        self._name = in_filter.GetClassName()

        in_filter.AddObserver('StartEvent', self.start_event_callback)
        in_filter.AddObserver('EndEvent', self.end_event_callback)

    def start_event_callback(self, obj, env):
        self._start = timer()

    def end_event_callback(self, obj, env):
        self._end = timer()
        logging.debug('{} execution time {:.4f} seconds'.format(
            self._name,
            self._end - self._start))






