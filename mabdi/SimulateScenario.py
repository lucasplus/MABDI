
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
    - _SimulateSensor.py - Will have it's own vtk objects and return a set of depth images
      - how best to name internal classes PEP8?
    - set_environment()
    - get_sensor_measurments()
    - The first pass at this will not implement object addition and removal"""

    def __init__(self):

        # in the future there may be more environments, 
        # right now there is only one
        in_environment = 'table_with_cups'
        
        self.sensor = _SimulateSensor()

        dir_simulated_scenario = os.path.join(
            os.path.dirname( __file__ ), 
            'simulated_scenario_files')

        dir_environments = os.path.join(
            dir_simulated_scenario,
            'environments',
            in_environment)

        self.objects = self.set_up_renderer(dir_environments)

    def set_up_renderer( self, in_dir ):
        """ Initialize objects from directory path containing stl files.
        Only grab stl files and return the file name without the extension."""
        
        # TODO: checks to make sure directory is valid
        # TODO: clean slate if not being run from __init__

        in_dir = os.path.normpath( in_dir )

        # grab files with the stl extension from given directory
        files = filter(
            lambda file: os.path.splitext( file )[1] == ".stl" ,
            os.listdir( in_dir )) 

        # strip the file extension and give me just the name of the file
        objects = map(
            lambda file: os.path.splitext( file )[0],
            files)
        
        # add the objects to the renderer
        for file in files:
            # read in the stl files
            reader = vtk.vtkSTLReader()
            reader.SetFileName(os.path.join(in_dir,file))
            # mapper the reader data into polygon data
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection( reader.GetOutputPort() )
            # asign the data to an actor that we can control
            actor = vtk.vtkActor()
            actor.SetMapper( mapper )
            # Add the actors to the renderer, set the background and size
            self.sensor.renderer.AddActor(actor)
        
        rang = np.arange(-40,41,5,dtype=float)
        
        pos = np.vstack(( rang/20, 
                          np.ones(len(rang)), 
                          np.ones(len(rang))*10 )).T
        
        lka = np.vstack(( rang/10, 
                          np.ones(len(rang)), 
                          np.zeros(len(rang)) )).T

        self.sensor.move_camera( pos, lka )
            
        return objects

