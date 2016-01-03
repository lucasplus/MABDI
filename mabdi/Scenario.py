
import os
import vtk

class Scenario(object):
    """description of class"""

    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.renderWindow)

    def setup(self,environment_directory):
        # grab all stl files out of the directory
        environment_files = os.listdir( environment_directory )
        environment_files = filter(
            lambda file: os.path.splitext( file )[1] == ".stl" ,
            environment_files) 
        print(environment_files)

