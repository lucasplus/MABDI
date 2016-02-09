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

def project_pixel(p_x, p_y, p_z):
    win_size = renWin.GetSize()

    ren.SetDisplayPoint(p_x,p_y,p_z)
    ren.DisplayToView()
    view_point = ren.GetViewPoint()
    ren.ViewToWorld()
    world_point = ren.GetWorldPoint()

    tmp = np.zeros((4, 1))

    (npl, fpl) = ren.GetActiveCamera().GetClippingRange()

    cam_pos = ren.GetActiveCamera().GetPosition()

    fovy = ren.GetActiveCamera().GetViewAngle()
    iv1 = 2*npl*fpl
    iv2 = npl+fpl
    iv3 = fpl-npl

    tmp[0] = float(p_x) / win_size[0]
    tmp[1] = float(p_y) / win_size[1]
    #tmp[0] = p_x
    #tmp[1] = p_y
    tmp[2] = p_z
    # tmp[2] = (-iv1+iv2*p_z+iv3*p_z) / (2.0*p_z*iv3)
    tmp[3] = 1.0

    tmp = tmp*2 - 1
    tmp[2] = p_z

    T = ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(
        ren.GetTiledAspectRatio(),
        0, 1)
    T0 = ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(win_size[0]/win_size[1],npl,fpl)
    T1 = ren.GetActiveCamera().GetProjectionTransformMatrix(win_size[0]/win_size[1],npl,fpl)
    T2 = ren.GetActiveCamera().GetProjectionTransformMatrix(ren)
    #T = CopyMatrix4x4(T)
    #Tinv = np.linalg.inv(T)
    T.Invert()


    # xyz = np.dot(Tinv, tmp)
    xyz = np.array(T.MultiplyPoint(tmp))
    xyz = xyz / xyz[3]

    return xyz


def render_point_cloud(obj, env):
    # get the world coordinate
    pixel_index = obj.GetEventPosition()
    pixel_index = (150, 150)
    iren.GetPicker().Pick(pixel_index[0], pixel_index[1], 0, ren)
    xyz = iren.GetPicker().GetPickPosition()

    # do it the hard way and compare
    z = ren.GetZ(pixel_index[0], pixel_index[1])
    h_xyz = project_pixel(pixel_index[0], pixel_index[1], z)

    # render the picked point
    source = vtk.vtkSphereSource()
    source.SetCenter(xyz)
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

