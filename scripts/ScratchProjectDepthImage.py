import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa

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

# world point picker
picker = vtk.vtkWorldPointPicker()
iren.SetPicker(picker)

# set camera intrinsic params to mimic kinect
ren.GetActiveCamera().SetViewAngle(60.0)
ren.GetActiveCamera().SetClippingRange(0.5, 10.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)

# vtk objects for the point cloud
points = vtk.vtkPoints()
vertices = vtk.vtkCellArray()
polydata = vtk.vtkPolyData()
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(2)
rgb = [0.0, 0.0, 0.0]
colors = vtk.vtkNamedColors()
colors.GetColorRGB("red", rgb)
actor.GetProperty().SetColor(rgb)

ren.AddActor(actor)


def render_point_cloud(obj, env):
    this_polydata = mapper.GetInput()
    points.Reset()
    vertices.Reset()
    for x in np.arange(obj.GetSize()[0]):
        for y in np.arange(obj.GetSize()[1]):
            iren.GetPicker().Pick(x, y, 0, ren)
            xyz = iren.GetPicker().GetPickPosition()
            pt_id = points.InsertNextPoint(xyz)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pt_id)
    this_polydata.SetPoints(points)
    this_polydata.SetVerts(vertices)

    this_polydata.Modified()
    mapper.Update()

    iren.Render()

    print("rendered")

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
