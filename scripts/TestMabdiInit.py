import vtk
from vtk.util.colors import *
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
Script to test the simulated sensor output generated from rendering
the output of the surface reconstruction
Render Window top row
- [Scenario] renScenario; Interactive
- [Sensor] renSensor; Not Interactive
Render Window bottom row
- [Mesh] renMesh; Interactive
- [Simulated Sensor] renSSensor; Not Interactive
"""

""" Filters and sources """

source = mabdi.SourceEnvironmentTable()
source.Update()
sourceAo = mabdi.VTKPolyDataActorObjects()
sourceAo.mapper.SetInputConnection(source.GetOutputPort())
sourceAo.actor.SetMapper(sourceAo.mapper)
sourceAo.actor.GetProperty().SetColor(slate_grey_light)
sourceAo.actor.GetProperty().SetOpacity(0.5)

di = mabdi.FilterDepthImage(offscreen=True)
di.set_polydata(source)
diAo = mabdi.VTKImageActorObjects()
diAo.mapper.SetInputConnection(di.GetOutputPort())
diAo.mapper.SetColorWindow(1.0)
diAo.mapper.SetColorLevel(0.5)

surf = mabdi.FilterDepthImageToSurface()
surf.SetInputConnection(di.GetOutputPort())
surfAo = mabdi.VTKPolyDataActorObjects()
surfAo.mapper.SetInputConnection(surf.GetOutputPort())
surfAo.actor.GetProperty().SetPointSize(1.5)
surfAo.actor.GetProperty().SetColor(red)

