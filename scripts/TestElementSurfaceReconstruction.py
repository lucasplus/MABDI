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

# depth image render objects
diro = mabdi.VTKRenderObjects()
diro.renWin.SetSize(640, 480)

# scenario render objects
sro = mabdi.VTKRenderObjects()

""" Set up render objects """

# depth image actor objects
diao = mabdi.VTKImageActorObjects()
diao.mapper.SetInputConnection(fdi.GetOutputPort())
diao.mapper.SetColorWindow(1.0)
diao.mapper.SetColorLevel(0.5)

# point cloud actor objects
pcao = mabdi.VTKPolyDataActorObjects()
pcao.mapper.SetInputConnection(fpc.GetOutputPort())

# point cloud, adjust color
pcao.actor.GetProperty().SetPointSize(2)
rgb = [0.0, 0.0, 0.0]
colors = vtk.vtkNamedColors()
colors.GetColorRGB("red", rgb)
pcao.actor.GetProperty().SetColor(rgb)

# source environment actor objects
sao = mabdi.VTKPolyDataActorObjects()
sao.mapper.SetInputConnection(source.GetOutputPort())
sao.actor.SetMapper(sao.mapper)

# add actors to respective renderers
diro.ren.AddActor(diao.actor)
sro.ren.AddActor(pcao.actor)
sro.ren.AddActor(sao.actor)

""" Initialize and do first render """

diro.iren.Initialize()
diro.iren.Render()

sro.iren.Initialize()
sro.iren.Render()

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
    diro.iren.Render()
    sro.iren.Render()
    sro.iren.Start()
    time.sleep(.1)
