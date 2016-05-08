import vtk
from vtk.util.colors import eggshell, slate_grey_light, red
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import mabdi

import numpy as np

import matplotlib.pyplot as plt

import time

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(module)s @ %(funcName)s: %(message)s")

"""
Script to test FilterDepthImageToSurface
"""

""" Filters and sources """

source = mabdi.SourceEnvironmentTable()
source.Update()
sourceAo = mabdi.VTKPolyDataActorObjects(source)
sourceAo.actor.GetProperty().SetColor(slate_grey_light)
sourceAo.actor.GetProperty().SetOpacity(0.5)

di = mabdi.FilterDepthImage(offscreen=True)
di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects(di)
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

surf = mabdi.FilterDepthImageToSurface()
surf.SetInputConnection(di.GetOutputPort())
surfAo = mabdi.VTKPolyDataActorObjects(surf)
surfAo.actor.GetProperty().SetPointSize(1.5)
surfAo.actor.GetProperty().SetColor(red)

""" Render objects """

renWin = vtk.vtkRenderWindow()
renWin.SetSize(640*3, 480*1)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# scenario
renSc = vtk.vtkRenderer()
renSc.SetBackground(eggshell)
renSc.SetViewport(0.0, 0.0, 1.0/3, 1.0)
renSc.AddActor(sourceAo.actor)
renSc.AddActor(surfAo.actor)
cameraActor = vtk.vtkCameraActor()
cameraActor.SetCamera(di.get_vtk_camera())
cameraActor.SetWidthByHeightRatio(di.get_width_by_height_ratio())
renSc.AddActor(cameraActor)

# sensor output
renSo = vtk.vtkRenderer()
renSo.SetViewport(1.0/3, 0.0, 2.0/3, 1.0)
renSo.SetInteractive(0)
renSo.AddActor(diAo.actor)

renWin.AddRenderer(renSc)
renWin.AddRenderer(renSo)

iren.Render()

""" Move the sensor """

rang = np.arange(-40, 41, dtype=float)
position = np.vstack((rang/20,
                      np.ones(len(rang)),
                      np.ones(len(rang))*2)).T
lookat = np.vstack((rang/40,
                    np.ones(len(rang))*.5,
                    np.zeros(len(rang)))).T

for i, (pos, lka) in enumerate(zip(position, lookat)):
    di.set_sensor_orientation(pos, lka)
    di.Modified()
    iren.Render()
    iren.Start()



