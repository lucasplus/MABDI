import vtk
from vtk.util.colors import *

import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

"""
Script to test SourceEnvironmentTable
    SourceEnvironmentTable creates vtkPolyData based on an environment
    with a floor, table, and two cups. Also, methods to add and
    remove these objects.
"""

source = mabdi.SourceEnvironmentTable()
source.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(source.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()

renWin.AddRenderer(ren)
ren.Render()
iren.SetRenderWindow(renWin)

ren.AddActor(actor)


def user_event_callback(obj, env):
    logging.debug('')

    # toggle state
    if not hasattr(user_event_callback, "state"):
        user_event_callback.state = True  # it doesn't exist yet, so initialize it
    user_event_callback.state = not user_event_callback.state

    source.set_object_state(object_name='floor',
                            state=not user_event_callback.state)
    source.set_object_state(object_name='table',
                            state=user_event_callback.state)
    source.set_object_state(object_name='left_cup',
                            state=not user_event_callback.state)
    source.set_object_state(object_name='right_cup',
                            state=user_event_callback.state)

    source.Modified()
    iren.Render()
iren.AddObserver('UserEvent', user_event_callback)

iren.Initialize()
iren.Start()
