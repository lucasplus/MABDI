
import vtk
from vtk.util import numpy_support
import numpy as np
import time
import sys
import os

class _SimulateSensor(object):
    """Class to simulate the output of a kinect-like sensor
    - pov - Point of View of the simulated sensor
    - depth - mechanics for getting the depth image from the pov of the sensor
    - observer - maybe in the future 
    - Caller is responsible for updating the actors"""

    def __init__(self):
        # initialize vtk objects

        # class to act as a c struct and contain a vtkRenderer and vtkRenderWindow
        class _VTK_Renderer_And_RenderWindow:
            renderer = vtk.vtkRenderer()
            window = vtk.vtkRenderWindow()

        # POV of the sensor
        self._pov = _VTK_Renderer_And_RenderWindow()
        self._pov.window.AddRenderer(self._pov.renderer)
        self._pov.window.SetSize(640, 480)
        self._pov.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderer = self._pov.renderer # unprivatize this for the user TODO maybe decorator

        # Depth output of the sensor
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

        # set camera intrinsic parameters 
        self._pov.renderer.GetActiveCamera().SetViewAngle( 60.0 );
        self._pov.renderer.GetActiveCamera().SetClippingRange( 0.5, 10.0 );

    def move_camera( self, in_position, in_lookat ):
        # TODO: make sure in_position and in_lookat are the same size
        # TODO: make sure arguments are of size Nx3

        # TODO: execption here I think
        if in_position.shape != in_lookat.shape:
            sys.exit("check move_camera input arguments")
        if in_position.shape[1] != 3 or in_lookat.shape[1] != 3:
            sys.exit("check move_camera input arguments")

        camera = self._pov.renderer.GetActiveCamera()

        ot_images = np.zeros( (480,640,in_position.shape[0]) )
        for i, (pos,lka) in enumerate( zip(in_position,in_lookat) ):
            camera.SetPosition( pos )
            camera.SetFocalPoint( lka )
            # print(i)
            self._pov.window.Render()
            self.filter.Modified()
            self._depth.window.Render()
            image = self.filter.GetOutput()
            ot_images[:,:,i] = numpy_support.vtk_to_numpy( image.GetPointData().GetScalars() ).reshape(480,640)
            
            time.sleep(0.1)

        self._pov.window.Finalize()
        self._depth.window.Finalize()
        return ot_images



