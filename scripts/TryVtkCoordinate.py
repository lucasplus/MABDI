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

# mapper
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())

# actor
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)

# assign actor to the renderer
ren.AddActor(cubeActor)


def render_point_cloud(obj, env):
    pixel_index = obj.GetEventPosition()
    coordinate = vtk.vtkCoordinate()
    coordinate.SetCoordinateSystemToDisplay()
    coordinate.SetValue(pixel_index[0], pixel_index[1])
    xyz = coordinate.GetComputedWorldValue(ren)
    # create source
    source = vtk.vtkSphereSource()
    source.SetCenter(xyz)
    source.SetRadius(0.1)

    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # assign actor to the renderer
    ren.AddActor(actor)
    ren.Render()
    print(pixel_index)
    print(xyz)

iren.AddObserver('UserEvent', render_point_cloud)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
