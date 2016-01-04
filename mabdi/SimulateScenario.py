
import os
import vtk

class SimulateScenario(object):
    """Simulate a Scenario. 
    A scenario has:
    Objects (user defined)
    - Defined by stl files from a user provided directory.
    - Can be added or removed from the scenario.
    Sensor Path (user defined)
    - List of locations given by the user.
    Sensor
    - Simulated by this class and is the main output of doing the simulation.
    - A kinect-like depth sensor. """

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

