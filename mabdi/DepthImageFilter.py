import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np

from timeit import default_timer as timer

import logging


class DepthImageFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkImageData')
        self._ren = None
        self._renWin = None
        self._imageBounds = [0, 0, 0, 0]

    def SetRendererAndRenderWindow(self, renderer, render_window):
        if renderer != self._ren:
            self._ren = renderer
        if render_window != self._renWin:
            self._renWin = render_window
        self._initialize()
        self.Modified()

    def GetRenderer(self):
        return self._ren

    def GetRenderWindow(self):
        return self._renWin

    def _initialize(self):
        logging.debug('')
        viewport = self._ren.GetViewport()
        size = self._renWin.GetSize()
        self._imageBounds[0] = int(viewport[0] * size[0])
        self._imageBounds[1] = int(viewport[1] * size[1])
        self._imageBounds[2] = int(viewport[2] * size[0] + 0.5) - 1
        self._imageBounds[3] = int(viewport[3] * size[1] + 0.5) - 1
        logging.debug('Window Size {}, {}'.format(*size))

    def RequestInformation(self, request, inInfo, outInfo):
        logging.debug('')
        size = self._renWin.GetSize()
        extent = (0, size[0]-1, 0, size[1]-1, 0, 0)
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
        logging.debug('Execution time {:.4f} seconds'.format(end-start))

        return 1
