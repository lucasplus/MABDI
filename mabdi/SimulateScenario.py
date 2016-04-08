
import os
import vtk
import numpy as np

from _SimulateSensor import _SimulateSensor

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
    - how best to name internal classes PEP8?
    - set_environment()
    - get_sensor_measurments()
    - The first pass at this will not implement object addition and removal
    - show_environment() """

    def __init__( self, load_default=False ):
        
        # c-like structure containing items related to the sensor
        # sensor
        #   path
        #     position
        #     lookat
        self.sensor = _SimulateSensor()
        class _struct_sensor_path:
            position = []
            lookat = []
        self.sensor.path = _struct_sensor_path()

        # directory where simulated scenario files are located
        dir_simulated_scenario = os.path.join(
            os.path.dirname( __file__ ), 
            'simulated_scenario_files')

        # directory that contains a folder for each environment
        self._dir_environments = os.path.join(
            dir_simulated_scenario,
            'environments')

        # list of folders in the environments directory
        # each folder is expected to hold .stl files corresponding 
        # to a specific environment
        self.list_of_environments = \
            [ env for env in os.listdir(self._dir_environments)
              if os.path.isdir( os.path.join(self._dir_environments,env) ) ]

        # load the default environment if requested
        # right now the default environment is the first one because there is only one
        if load_default: 
            self.list_of_objects = self.set_environment( self.list_of_environments[0] )
            self.set_sensor_path()

    def set_environment( self, in_env ):
        """ Environment is defined by a set of stl files.
        Arguments:
          in_env - name of folder containing the stl files and also the name of the environment
        Return:
          objects - list of the object names. Defined to be the names of the stl files """
        
        # TODO: checks to make sure directory is valid
        # TODO: clean slate if not being run from __init__

        dir = os.path.normpath( os.path.join( self._dir_environments, in_env ) )

        # grab files with the stl extension from given directory
        files = filter(
            lambda file: os.path.splitext( file )[1] == ".stl" ,
            os.listdir( dir )) 

        # strip the file extension and give me just the name of the file
        objects = map(
            lambda file: os.path.splitext( file )[0],
            files)
        
        # add the objects to the renderer
        for file in files:
            # read in the stl files
            reader = vtk.vtkSTLReader()
            reader.SetFileName(os.path.join(dir,file))
            # mapper the reader data into polygon data
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection( reader.GetOutputPort() )
            # assign the data to an actor that we can control
            actor = vtk.vtkActor()
            actor.SetMapper( mapper )
            # Add the actors to the renderer, set the background and size
            self.sensor.renderer.AddActor(actor)

        return objects

    def set_sensor_path(self):
        
        rang = np.arange(-40,41,dtype=float)
        
        pos = np.vstack(( rang/20, 
                          np.ones(len(rang)), 
                          np.ones(len(rang))*5 )).T
        
        lka = np.vstack(( rang/10, 
                          np.ones(len(rang)), 
                          np.zeros(len(rang)) )).T

        self.sensor.path.position = pos
        self.sensor.path.lookat   = lka

    def run(self):
        return self.sensor.move_camera( 
            self.sensor.path.position, self.sensor.path.lookat )
            
        

