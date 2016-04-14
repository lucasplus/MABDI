import vtk
import mabdi

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

# ren, renWin, iren - vtk rendering objects
scene = mabdi.VTKRenderObjects()
scene.renWin.AddRenderer(scene.ren)
scene.iren.SetRenderWindow(scene.renWin)

# create cube
cube = vtk.vtkCubeSource()
cube.SetCenter(0, 0, 0)
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
scene.ren.AddActor(cubeActor)

# set camera intrinsic params to mimic kinect
scene.renWin.SetSize(640, 480)
scene.ren.GetActiveCamera().SetViewAngle(60.0)
scene.ren.GetActiveCamera().SetClippingRange(0.1, 10.0)
scene.iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)
scene.ren.GetActiveCamera().SetPosition(0.0, 0.0, 2.0)

# has to be initialized before filter is update
# not sure why
scene.iren.Initialize()
scene.iren.Render()

# dif (depth image filter)
# Filter that gets the depth image
dif = mabdi.FilterDepthImage()
dif.SetRendererAndRenderWindow(scene.ren, scene.renWin)
dif.Update()

# show output of the filter
image = mabdi.VTKRenderObjects()
image.renWin.AddRenderer(image.ren)
imageMapper = vtk.vtkImageMapper()
imageMapper.SetInputConnection(dif.GetOutputPort())
imageMapper.SetColorWindow(1.0)
imageMapper.SetColorLevel(0.5)
imageActor = vtk.vtkActor2D()
imageActor.SetMapper(imageMapper)
image.ren.AddActor(imageActor)
image.renWin.Render()


def user_event_callback(obj, env):
    logging.debug('')
    dif.Modified()
    image.renWin.Render()
scene.iren.AddObserver('UserEvent', user_event_callback)

# render the depth image

# print dif.GetOutputDataObject(0)

scene.iren.Start()

