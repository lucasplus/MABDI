
import vtk
import numpy as np
import time
import os

class _SimulateSensor(object):
    """Class to simulate the output of a kinect-like sensor
    - Caller is responsible for updating the actors"""

    def __init__(self):
        # initialize vtk objects

        # class to act as a c struct and contain a vtkRenderer and vtkRenderWindow
        class _VTK_Renderer_And_RenderWindow:
            renderer = vtk.vtkRenderer()
            window = vtk.vtkRenderWindow()

        # Renderer and RenderWindow rendering the POV of the sensor
        self._pov = _VTK_Renderer_And_RenderWindow()
        self._pov.window.AddRenderer(self._pov.renderer)
        self._pov.window.SetSize(640, 480)
        self._pov.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderer = self._pov.renderer

        # Renderer and RenderWindow for an image created by a vtkWindowToImageFilter
        # that gets the depth from the render window
        self._depth = _VTK_Renderer_And_RenderWindow()
        self._depth.window.AddRenderer(self._depth.renderer)
        self._depth.window.SetSize(640, 480)
        
        # filter that grabs the vtkRenderWindow and returns 
        # the depth image (in this case)
        self.filter = vtk.vtkWindowToImageFilter()
        self.filter.SetInputBufferTypeToZBuffer()
        self.filter.SetInput( self._pov.renderer.GetVTKWindow() )
        self.filter.Update()
        
        # take the output of the mapper and turn it into an actor that
        # can be rendered
        image_mapper = vtk.vtkImageMapper()
        image_mapper.SetInputConnection( self.filter.GetOutputPort() )
        image_mapper.SetColorWindow( 1.0 );
        image_mapper.SetColorLevel( 0.5 );
        image_actor = vtk.vtkActor2D()
        image_actor.SetMapper( image_mapper )
        self._depth.renderer.AddActor( image_actor )

        # add observer
        self._pov.window.AddObserver( 'RenderEvent' , self._callback_get_depth_image ) 

        # set camera intrinsic parameters 
        self._pov.renderer.GetActiveCamera().SetViewAngle( 60.0 );
        self._pov.renderer.GetActiveCamera().SetClippingRange( 0.5, 10.0 );

    def _callback_get_depth_image( self, obj, env ):
        self.filter.Modified()
        self._depth.window.Render()

    def move_camera( self, in_position, in_lookat ):
        # TODO: make sure in_position and in_lookat are the same size
        # TODO: make sure arguments are of size Nx3

        camera = self._pov.renderer.GetActiveCamera()

        for pos,lka in zip(in_position,in_lookat):
            camera.SetPosition( pos )
            camera.SetFocalPoint( lka )
            self._pov.window.Render()
            time.sleep(0.1)



