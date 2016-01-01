#!/usr/bin/env python

import vtk
import os

# where am I?
print(os.getcwd())
print(os.path.abspath("util/stl/environment/table"))

# read in the stl files
reader = vtk.vtkSTLReader()
reader.SetFileName("util/stl/environment/table.stl")

# mapper the reader data into polygon data
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection( reader.GetOutputPort() )

# asign the data to an actor that we can control
actor = vtk.vtkActor()
actor.SetMapper( mapper )

# Create the graphics structure. The renderer renders into the render
# window. The render window interactor captures mouse events and will
# perform appropriate camera or actor manipulation depending on the
# nature of the events.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.SetBackground(0.1, 0.2, 0.4)
renWin.SetSize(200, 200)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

iren.Start()