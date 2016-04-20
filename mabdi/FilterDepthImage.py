import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np

from timeit import default_timer as timer
import logging


class FilterDepthImage(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkImageData')
        self._ren = vtk.vtkRenderer()
        self._renWin = vtk.vtkRenderWindow()
        self._iren = vtk.vtkRenderWindowInteractor()

        self._renWin.AddRenderer(self._ren)
        self._iren.SetRenderWindow(self._renWin)

        # kinect intrinsic parameters
        # https://msdn.microsoft.com/en-us/library/hh438998.aspx
        self._renWin.SetSize(640, 480)
        self._ren.GetActiveCamera().SetViewAngle(60.0)
        self._ren.GetActiveCamera().SetClippingRange(0.8, 4.0)
        self._iren.GetInteractorStyle().SetAutoAdjustCameraClippingRange(0)
        self._ren.GetActiveCamera().SetPosition(0.0, 0.5, 2.0)
        self._ren.GetActiveCamera().SetFocalPoint(0.0, 0.5, 0.0)

        self._imageBounds = [0, 0, 0, 0]

        self._initialize()

    def _initialize(self):
        logging.debug('')
        viewport = self._ren.GetViewport()
        size = self._renWin.GetSize()
        self._imageBounds[0] = int(viewport[0] * size[0])
        self._imageBounds[1] = int(viewport[1] * size[1])
        self._imageBounds[2] = int(viewport[2] * size[0] + 0.5) - 1
        self._imageBounds[3] = int(viewport[3] * size[1] + 0.5) - 1
        logging.debug('Window Size {}, {}'.format(*size))

    def set_polydata(self, in_polydata):
        logging.debug('')
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(in_polydata.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self._ren.AddActor(actor)

        self._iren.Initialize()
        self._iren.Render()

    def set_sensor_orientation(self, in_position, in_lookat):
        logging.debug('')
        logging.debug('position{} lookat{}'.format(in_position, in_lookat))
        self._ren.GetActiveCamera().SetPosition(in_position)
        self._ren.GetActiveCamera().SetFocalPoint(in_lookat)
        self._iren.Render()

    def RequestInformation(self, request, inInfo, outInfo):
        logging.debug('')
        size = self._renWin.GetSize()
        extent = (0, size[0] - 1, 0, size[1] - 1, 0, 0)
        info = outInfo.GetInformationObject(0)
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                 extent, len(extent))
        return 1

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        info = outInfo.GetInformationObject(0)
        ue = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())

        vfa = vtk.vtkFloatArray()
        ib = self._imageBounds
        self._renWin.GetZbufferData(ib[0], ib[1], ib[2], ib[3], vfa)

        out = vtk.vtkImageData.GetData(outInfo)
        out.GetPointData().SetScalars(vfa)
        out.SetExtent(ue)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1


"""
    def GetRenderer(self):
        return self._ren

    def GetRenderWindow(self):
        return self._renWin
"""