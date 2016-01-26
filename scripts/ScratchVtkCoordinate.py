import vtk

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


def render_point_cloud(obj, env):
    pixel_index = obj.GetEventPosition()
    iren.GetPicker().Pick(pixel_index[0], pixel_index[1], 0,ren)
    xyz = iren.GetPicker().GetPickPosition()

    # render the picked point
    source = vtk.vtkSphereSource()
    source.SetCenter(xyz)
    source.SetRadius(0.05)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # assign actor to the renderer
    ren.AddActor(actor)
    iren.Render()
    print(pixel_index)
    print(xyz)
    print("")

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
