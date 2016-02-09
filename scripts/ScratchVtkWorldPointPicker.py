import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np


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


# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create cube
cube = vtk.vtkCubeSource()
cube.SetCenter(0, 0, 0)

# mapper
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())

# actor
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)

# assign actor to the renderer
ren.AddActor(cubeActor)

# world point picker
picker = vtk.vtkWorldPointPicker()
iren.SetPicker(picker)

# set camera intrinsic params to mimic kinect
ren.GetActiveCamera().SetViewAngle(60.0)
ren.GetActiveCamera().SetClippingRange(0.1, 10.0)
iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)
ren.GetActiveCamera().SetPosition(0.0, 0.0, 2.0)


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
    # get the world coordinate
    pixel_index = obj.GetEventPosition()
    # pixel_index = (160, 150)
    iren.GetPicker().Pick(pixel_index[0], pixel_index[1], 0, ren)
    xyz = iren.GetPicker().GetPickPosition()

    # do it the hard way and compare
    z = ren.GetZ(pixel_index[0], pixel_index[1])
    h_xyz = project_pixel(pixel_index[0], pixel_index[1], z)

    # render the picked point
    source = vtk.vtkSphereSource()
    source.SetCenter(h_xyz)
    source.SetRadius(0.02)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    rgb = [0.0, 0.0, 0.0]
    colors = vtk.vtkNamedColors()
    colors.GetColorRGB("red", rgb)
    actor.GetProperty().SetColor(rgb)

    # assign actor to the renderer
    ren.AddActor(actor)
    iren.Render()
    print(pixel_index)
    print(xyz)
    print(h_xyz)
    print("")

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()

