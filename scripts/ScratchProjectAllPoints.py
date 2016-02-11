import vtk

from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np

import matplotlib.pyplot as plt

from timeit import default_timer as timer
import time

def CopyMatrix4x4(matrix):
    """
    Copies the elements of a vtkMatrix4x4 into a numpy array.

    :@type matrix: vtk.vtkMatrix4x4
    :@param matrix: The matrix to be copied into an array.
    :@rtype: numpy.ndarray
    """
    m = np.ones((4,4))
    for i in range(4):
        for j in range(4):
            m[i,j] = matrix.GetElement(i,j)
    return m


def project_pixel(display_pts):

    # things to know
    (sizex, sizey) = renWin.GetSize()
    viewport = ren.GetViewport()

    # update filter
    depth_image_filter.Update()
    depth_image_filter.Modified()

    # get depth image
    dfilter = dsa.WrapDataObject(depth_image_filter.GetOutput())
    image = numpy_support.vtk_to_numpy(dfilter.PointData['ImageScalars']).reshape((sizey, sizex))

    display_pts[2, :] = image.ravel()

    viewport_pts = np.ones((4, display_pts.shape[1]))
    viewport_pts[0,:] = 2.0 * (display_pts[0,:] - sizex*viewport[0]) / (sizex*(viewport[2]-viewport[0])) - 1.0
    viewport_pts[1,:] = 2.0 * (display_pts[1,:] - sizey*viewport[1]) / (sizey*(viewport[3]-viewport[1])) - 1.0
    viewport_pts[2,:] = display_pts[2,:]

    # transform matrix
    tmat = ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(
        ren.GetTiledAspectRatio(),
        0.0, 1.0)
    tmat.Invert()
    tmat = CopyMatrix4x4(tmat)

    # world point
    # world_pts = np.array(tmat.MultiplyPoint(viewport_pts))
    # world_pts = np.zeros(viewport_pts.shape)
    world_pts = np.dot(tmat, viewport_pts)
    world_pts = world_pts / world_pts[3]

    return world_pts[0:3, :]


def render_point_cloud(obj, env):
    start = timer()

    # things to know
    (sizex, sizey) = obj.GetSize()

    display_pts = np.ones((4, sizex*sizey))
    count = 0
    for i in np.arange(sizey):
        for j in np.arange(sizex):
            display_pts[0, count] = j
            display_pts[1, count] = i
            count += 1

    pc = project_pixel(display_pts)

    points.Reset()
    vertices.Reset()
    for i in np.arange(pc.shape[1]):
        pt_id = points.InsertNextPoint(pc[:, i])
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pt_id)
    polydata.SetPoints(points)
    polydata.SetVerts(vertices)
    polydata.Modified()
    mapper.Update()

    iren.Render()

    end = timer()
    print(end-start)


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
renWin.SetSize(300, 300)
ren.GetActiveCamera().SetViewAngle(60.0)
ren.GetActiveCamera().SetClippingRange(0.1, 10.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)
ren.GetActiveCamera().SetPosition(0.0, 0.0, 2.0)

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

# has to be initialized before filter is update
# not sure why
iren.Initialize()

# depth_image_filter that grabs the vtkRenderWindow and returns 
# the depth image (in this case)
depth_image_filter = vtk.vtkWindowToImageFilter()
depth_image_filter.SetInputBufferTypeToZBuffer()
depth_image_filter.SetInput(ren.GetVTKWindow())
depth_image_filter.Update()

# needed for first image in loop to be current
ren.Render()
depth_image_filter.Update()
depth_image_filter.Modified()

iren.AddObserver('UserEvent', render_point_cloud)

iren.Start()



# plt.imshow(image, origin='lower')
# plt.colorbar()
# plt.show()