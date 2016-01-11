
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
        self.ren_win.Render()



        # directory where simulated scenario files are located
        dir_simulated_scenario = os.path.join(
            os.path.dirname( __file__ ), 
            'simulated_scenario_files')

        # directory that contains a folder for each environment
        self._dir_environments = os.path.join(
            dir_simulated_scenario,
            'environments')

        dir = os.path.normpath( os.path.join( self._dir_environments, 'table_with_cups' ) )

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
            # asign the data to an actor that we can control
            actor = vtk.vtkActor()
            actor.SetMapper( mapper )
            # Add the actors to the renderer, set the background and size
            self.renderer.AddActor(actor)

        self.renderer.ResetCamera()
        self.ren_win.Render()

        # Renderer and RenderWindow for an image created by a vtkWindowToImageFilter
        # that gets the depth from the render window
        self.d_renderer = vtk.vtkRenderer()
        self.d_ren_win = vtk.vtkRenderWindow()
        self.d_ren_win.AddRenderer(self.d_renderer)
        
        self.filter = vtk.vtkWindowToImageFilter()
        self.filter.SetInputBufferTypeToZBuffer()
        self.filter.SetInput( self.renderer.GetVTKWindow() )
        self.filter.Update()
        
        writer = vtk.vtkTIFFWriter()
        writer.SetInputConnection( self.filter.GetOutputPort() )
        writer.SetFileName("hai.tif")

        self.ren_win.Render()
        writer.Write()

        self.image_mapper = vtk.vtkImageMapper()
        self.image_mapper.SetInputConnection( self.filter.GetOutputPort() )
        self.image_mapper.SetColorWindow( 1.0 );
        self.image_mapper.SetColorLevel( 0.5 );
        self.image_actor = vtk.vtkActor2D()
        self.image_actor.SetMapper( self.image_mapper )

        self.d_renderer.AddActor( self.image_actor )

        self.ren_win.Render()
        self.d_ren_win.Start()
        self.filter.Modified()
        self.d_ren_win.Render()

        # add observer
        self.ren_win.AddObserver( 'RenderEvent' , self.myCallback ) 

    def myCallback( self, obj, env ):
        print("I rendered")
        #self.filter.Modified()
        #self.d_ren_win.Render()

    def move_camera( self, in_position, in_lookat ):
        # TODO: make sure in_position and in_lookat are the same size
        # TODO: make sure arguments are of size Nx3

        camera = self.renderer.GetActiveCamera()

        for pos,lka in zip(in_position,in_lookat):
            camera.SetPosition( pos )
            camera.SetFocalPoint( lka )
            self.ren_win.Render()
            time.sleep(0.1)

        self.filter.Modified()
        print(self.d_ren_win)
        self.d_ren_win.Render()

        # return super(_SimulateSensor, self).__init__(*args, **kwargs)


