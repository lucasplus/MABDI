
import os
import vtk

class SimulateScenario(object):
    """ Simulate a Scenario. 
    A scenario has:
    Objects (user defined)
    - Defined by stl files from a user provided directory.
    - Can be added or removed from the scenario.
    Sensor Path (user defined)
    - List of locations given by the user.
    Sensor
    - Simulated by this class and is the main output of doing the simulation.
    - A kinect-like depth sensor. 
    TODO
    - The first pass at this will not implement object addition and removal"""

    def __init__(self,environment_directory):
        # vtk rendering objects we will need
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.renderWindow)
        
        self.environment_objects = self.__init_objects(environment_directory)

    def __init_objects(self,in_environment_directory):
        """ Initialize objects from directory path containing stl files.
        Only grab stl files and return the file name without the extension."""
        
        # TODO: checks to make sure directory is valid
        # TODO: clean slate if not being run from __init__

        # grab files with the stl extension from given directory
        environment_files = filter(
            lambda file: os.path.splitext( file )[1] == ".stl" ,
            os.listdir( in_environment_directory )) 

        # strip the file extension and give me just the name of the file
        out_environment_objects = map(
            lambda file: os.path.splitext( file )[0],
            environment_files)
        
        # add the objects to the renderer
        for file in environment_files:
            # read in the stl files
            reader = vtk.vtkSTLReader()
            reader.SetFileName(in_environment_directory + file)
            # mapper the reader data into polygon data
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection( reader.GetOutputPort() )
            # asign the data to an actor that we can control
            actor = vtk.vtkActor()
            actor.SetMapper( mapper )
            # Add the actors to the renderer, set the background and size
            self.renderer.AddActor(actor)

        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderWindow.SetSize(640, 480)
        self.interactor.Initialize()
        self.interactor.Render()

        camera = self.renderer.GetActiveCamera()


        return out_environment_objects

