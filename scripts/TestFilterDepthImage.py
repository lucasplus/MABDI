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
Script to test FilterDepthImage
    FilterDepthImage takes vtkPolyData from SourceEnvironmentTable
    and creates a vtkImage. As well, FilterDepthImage gives us control
    of the sensor location in the environment. This script shows the
    vtkImage and also moves the sensor along a straight line.
"""

source = mabdi.SourceEnvironmentTable()
source.Update()

dif = mabdi.FilterDepthImage()
dif.set_polydata(source)

# show output of the filter

ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()
renWin.AddRenderer(ren)
iren.SetRenderWindow(renWin)

renWin.SetSize(640, 480)
imageMapper = vtk.vtkImageMapper()
imageMapper.SetInputConnection(dif.GetOutputPort())
imageMapper.SetColorWindow(1.0)
imageMapper.SetColorLevel(0.5)
imageActor = vtk.vtkActor2D()
imageActor.SetMapper(imageMapper)
ren.AddActor(imageActor)

iren.Initialize()
iren.Render()

rang = np.arange(-40, 41, dtype=float)
position = np.vstack((rang/20,
                      np.ones(len(rang)),
                      np.ones(len(rang))*2)).T
lookat = np.vstack((rang/40,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

image = dif.GetOutputDataObject(0)
print image.GetInformation()

for i, (pos, lka) in enumerate(zip(position, lookat)):
    dif.set_sensor_orientation(pos, lka)
    dif.Modified()
    iren.Render()
    time.sleep(.1)




