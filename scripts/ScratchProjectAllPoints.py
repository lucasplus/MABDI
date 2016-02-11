import vtk
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg
from vtk.util import numpy_support
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import time

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
"""
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
"""

iren.Initialize()
renWin.Render()
renWin.Render()

# depth_image_filter that grabs the vtkRenderWindow and returns 
# the depth image (in this case)
depth_image_filter = vtk.vtkWindowToImageFilter()
depth_image_filter.SetInputBufferTypeToZBuffer()
depth_image_filter.SetInput(ren.GetVTKWindow())
depth_image_filter.Update()

dfilter = dsa.WrapDataObject(depth_image_filter.GetOutput())
image = numpy_support.vtk_to_numpy(dfilter.PointData['ImageScalars']).reshape(300, 300)
dfig = plt.imshow(image)
plt.colorbar()
time.sleep(.01)
plt.show()


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
    start = timer()

    (sizex, sizey) = obj.GetSize()
    d_pts = np.ones((4, sizex*sizey))

    """
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
    polydata.Modified()
    mapper.Update()
    """

    iren.Render()
    depth_image_filter.Update()
    depth_image_filter.Modified()

    dfilter = dsa.WrapDataObject(depth_image_filter.GetOutput())
    image = numpy_support.vtk_to_numpy(dfilter.PointData['ImageScalars']).reshape(sizey, sizex)
    plt.imshow(image, origin='lower')
    plt.colorbar()
    plt.show()

    end = timer()
    print(end-start)

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor

iren.Start()
