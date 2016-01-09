
import os
import vtk
import time

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
    - _SimulateSensor.py - Will have it's own vtk objects and return a set of depth images
      - how best to name internal classes PEP8?
    - set_environment()
    - get_sensor_measurments()
    - The first pass at this will not implement object addition and removal"""

    def __init__(self,environment_directory):
        # vtk rendering objects we will need
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        
        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderWindow.SetSize(640, 480)
        self.renderWindow.Start() # works without it

        resources_dir = os.path.join(
            os.path.dirname( __file__ ), 
            'simulated_scenario_files')

        environment_directory = os.path.join(
            resources_dir,
            'environments',
            'table_with_cups')

        print(resources_dir)
        print(environment_directory)

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
            reader.SetFileName(os.path.join(in_environment_directory,file))
            # mapper the reader data into polygon data
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection( reader.GetOutputPort() )
            # asign the data to an actor that we can control
            actor = vtk.vtkActor()
            actor.SetMapper( mapper )
            # Add the actors to the renderer, set the background and size
            self.renderer.AddActor(actor)

        camera = self.renderer.GetActiveCamera()
        # camera.SetPosition(0,1,10)
        print camera.GetPosition()

        for i in range(-40,40):
            camera.SetFocalPoint(i/20.0,1,0)
            camera.SetPosition(i/10.0,1,10)
            self.renderWindow.Render()
            time.sleep(0.1)
            
        return out_environment_objects

