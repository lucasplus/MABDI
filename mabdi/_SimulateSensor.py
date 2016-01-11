
import vtk
import numpy as np
import time
import os

class _SimulateSensor(object):
    """Class to simulate the output of a kinect-like sensor
    - Caller is responsible for updating the actors"""

    def __init__(self):
        # initialize vtk objects

        # Renderer and RenderWindow rendering the POV of the sensor
        self.renderer = vtk.vtkRenderer()
        self.ren_win = vtk.vtkRenderWindow()
        self.ren_win.AddRenderer(self.renderer)
        # configure 
        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.ren_win.SetSize(640, 480)
        self.ren_win.Start() # works without it

        # Renderer and RenderWindow for an image created by a vtkWindowToImageFilter
        # that gets the depth from the render window
        self.d_renderer = vtk.vtkRenderer()
        self.d_ren_win = vtk.vtkRenderWindow()
        self.d_ren_win.AddRenderer(self.d_renderer)
        self.d_ren_win.SetSize(640, 480)
        
        # filter that grabs the vtkRenderWindow and returns 
        # the depth image (in this case)
        self.filter = vtk.vtkWindowToImageFilter()
        self.filter.SetInputBufferTypeToZBuffer()
        self.filter.SetInput( self.renderer.GetVTKWindow() )
        self.filter.Update()
        
        # take the output of the mapper and turn it into an actor that
        # can be rendered
        self.image_mapper = vtk.vtkImageMapper()
        self.image_mapper.SetInputConnection( self.filter.GetOutputPort() )
        self.image_mapper.SetColorWindow( 1.0 );
        self.image_mapper.SetColorLevel( 0.5 );
        self.image_actor = vtk.vtkActor2D()
        self.image_actor.SetMapper( self.image_mapper )
        self.d_renderer.AddActor( self.image_actor )

        # add observer
        self.ren_win.AddObserver( 'RenderEvent' , self._callback_get_depth_image ) 

        # set camera intrinsic parameters 
        self.renderer.GetActiveCamera().SetViewAngle( 60.0 );
        self.renderer.GetActiveCamera().SetClippingRange( 0.5, 10.0 );

    def _callback_get_depth_image( self, obj, env ):
        print("I rendered")
        self.filter.Modified()
        self.d_ren_win.Render()

    def move_camera( self, in_position, in_lookat ):
        # TODO: make sure in_position and in_lookat are the same size
        # TODO: make sure arguments are of size Nx3

        camera = self.renderer.GetActiveCamera()

        for pos,lka in zip(in_position,in_lookat):
            camera.SetPosition( pos )
            camera.SetFocalPoint( lka )
            self.ren_win.Render()
            time.sleep(0.1)



