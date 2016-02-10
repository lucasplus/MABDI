import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
from timeit import default_timer as timer

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
ren.GetActiveCamera().SetClippingRange(0.1, 10.0)
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

# depth_image_filter that grabs the vtkRenderWindow and returns 
# the depth image (in this case)
# depth_image_filter = vtk.vtkWindowToImageFilter()
# depth_image_filter.SetInputBufferTypeToZBuffer()
# depth_image_filter.SetInput(ren.GetVTKWindow())
# depth_image_filter.Update()


def project_pixel(d_x, d_y, d_z):

    # display to viewport value
    ren.SetDisplayPoint(d_x, d_y, d_z)
    ren.DisplayToView()
    v_p = ren.GetViewPoint()

    # transform matrix
    tmat = ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(
        ren.GetTiledAspectRatio(),
        0.0, 1.0)
    tmat.Invert()

    # world point
    w_p = np.array(tmat.MultiplyPoint(v_p + (1.0,)))
    w_p = w_p / w_p[3]

    return w_p[0:3]


def render_point_cloud(obj, env):

    # (sizex, sizey) = obj.GetSize()
    # d_p = np.ones(4, sizex*sizey)

    start = timer()

    points.Reset()
    vertices.Reset()
    for x in np.arange(obj.GetSize()[0]):
        for y in np.arange(obj.GetSize()[1]):
            z = ren.GetZ(x, y)
            xyz = project_pixel(x, y, z)
            pt_id = points.InsertNextPoint(xyz)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pt_id)
    polydata.SetPoints(points)
    polydata.SetVerts(vertices)

    end = timer()

    polydata.Modified()
    mapper.Update()

    iren.Render()

    print(end-start)

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
