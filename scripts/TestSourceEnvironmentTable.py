import vtk
import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")


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
    source.set_object_state(object_name='table', state=False)
    source.Modified()
    ren.Render()
iren.AddObserver('UserEvent', user_event_callback)

iren.Initialize()
iren.Start()
