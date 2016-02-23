import vtk

import DepthImageFilter

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

# ren, renWin, iren - vtk rendering objects
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create cube
cube = vtk.vtkCubeSource()
cube.SetCenter(0, 0, 0)
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
ren.AddActor(cubeActor)

# set camera intrinsic params to mimic kinect
renWin.SetSize(640, 480)
ren.GetActiveCamera().SetViewAngle(60.0)
ren.GetActiveCamera().SetClippingRange(0.1, 10.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)
ren.GetActiveCamera().SetPosition(0.0, 0.0, 2.0)

# has to be initialized before filter is update
# not sure why
iren.Initialize()
iren.Render()

# dif (depth image filter)
# Filter that grabs the vtkRenderWindow and returns
# the depth image (in this case)
dif = DepthImageFilter.DepthImageFilter()
dif.SetRendererAndRenderWindow(ren, renWin)
dif.Update()

# print dif.GetOutputDataObject(0)


