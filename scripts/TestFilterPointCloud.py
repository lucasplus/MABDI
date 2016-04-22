import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np

import time

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

"""
Script to test FilterPointCloud
"""

""" Filters and sources """

source = mabdi.SourceEnvironmentTable()
source.Update()

fdi = mabdi.FilterDepthImage()
fdi.set_polydata(source)

fpc = mabdi.FilterPointCloud()
fpc.SetInputConnection(fdi.GetOutputPort())

""" Render objects """

ren1 = vtk.vtkRenderer()
renWin1 = vtk.vtkRenderWindow()
iren1 = vtk.vtkRenderWindowInteractor()
renWin1.AddRenderer(ren1)
iren1.SetRenderWindow(renWin1)

ren2 = vtk.vtkRenderer()
renWin2 = vtk.vtkRenderWindow()
iren2 = vtk.vtkRenderWindowInteractor()
renWin2.AddRenderer(ren2)
iren2.SetRenderWindow(renWin2)

""" Set up render objects """

# for displaying depth image
renWin1.SetSize(640, 480)
imageMapper = vtk.vtkImageMapper()
imageMapper.SetInputConnection(fdi.GetOutputPort())
imageMapper.SetColorWindow(1.0)
imageMapper.SetColorLevel(0.5)
imageActor = vtk.vtkActor2D()
imageActor.SetMapper(imageMapper)
ren1.AddActor(imageActor)

iren1.Initialize()
iren1.Render()

# for displaying the point cloud
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(fpc.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(2)
rgb = [0.0, 0.0, 0.0]
colors = vtk.vtkNamedColors()
colors.GetColorRGB("red", rgb)
actor.GetProperty().SetColor(rgb)
ren2.AddActor(actor)

emapper = vtk.vtkPolyDataMapper()
emapper.SetInputConnection(source.GetOutputPort())
eactor = vtk.vtkActor()
eactor.SetMapper(emapper)
ren2.AddActor(eactor)

iren2.Initialize()
iren2.Render()

""" Move the sensor """

rang = np.arange(-40, 41, dtype=float)
position = np.vstack((rang/20,
                      np.ones(len(rang)),
                      np.ones(len(rang))*2)).T
lookat = np.vstack((rang/40,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

for i, (pos, lka) in enumerate(zip(position, lookat)):
    fdi.set_sensor_orientation(pos, lka)
    fdi.Modified()
    iren1.Render()
    iren2.Render()
    iren2.Start()
    time.sleep(.1)


