import vtk


class VTKRenderObjects(object):

    def __init__(self):
        self.ren = vtk.vtkRenderer()
        self.renWin = vtk.vtkRenderWindow()
        self.iren = vtk.vtkRenderWindowInteractor()

        self.renWin.AddRenderer(self.ren)
        self.iren.SetRenderWindow(self.renWin)


class VTKPolyDataActorObjects(object):

    def __init__(self):
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()

        self.actor.SetMapper(self.mapper)


class VTKImageActorObjects(object):

    def __init__(self):
        self.mapper = vtk.vtkImageMapper()
        self.actor = vtk.vtkActor2D()

        self.actor.SetMapper(self.mapper)
