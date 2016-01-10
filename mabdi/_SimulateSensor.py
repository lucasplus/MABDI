
import vtk
import numpy as np
import time

class _SimulateSensor(object):
    """Class to simulate the output of a kinect-like sensor
    - Caller is responsible for updating the actors"""

    def __init__(self):
        # initialize vtk objects
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.AddRenderer(self.renderer)
        # configure vtk objects
        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderWindow.SetSize(640, 480)
        self.renderWindow.Start() # works without it

    def move_camera( self, in_position, in_lookat ):
        # TODO: make sure in_position and in_lookat are the same size
        # TODO: make sure arguments are of size Nx3

        camera = self.renderer.GetActiveCamera()

        for pos,lka in zip(in_position,in_lookat):
            camera.SetPosition( pos )
            camera.SetFocalPoint( lka )
            self.renderWindow.Render()
            time.sleep(0.1)

        # return super(_SimulateSensor, self).__init__(*args, **kwargs)


