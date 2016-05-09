import sys

import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

from timeit import default_timer as timer
import logging


class FilterClassifier(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=2, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkImageData')

        self._f, (self._ax1, self._ax2, self._ax3) = plt.subplots(1, 3, sharex=False, sharey=True)
        self._f.show()

    def RequestInformation(self, request, inInfo, outInfo):
        logging.debug('')

        # input images dimensions
        info = inInfo[0].GetInformationObject(0)
        ue1 = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())
        info = inInfo[1].GetInformationObject(0)
        ue2 = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())
        if ue1 != ue2:
            logging.warning('Input images have different dimensions. {} {}'.format(ue1, ue2))

        extent = ue1
        info = outInfo.GetInformationObject(0)
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                 extent, len(extent))

        return 1

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        # in images
        inp1 = vtk.vtkImageData.GetData(inInfo[0])
        inp2 = vtk.vtkImageData.GetData(inInfo[1])
        im1 = numpy_support.vtk_to_numpy(inp1.GetPointData().GetScalars()).reshape(480, 640)
        im2 = numpy_support.vtk_to_numpy(inp2.GetPointData().GetScalars()).reshape(480, 640)

        difim = im1 - im2

        self._ax1.imshow(im1, origin='lower', interpolation='none')
        self._ax2.imshow(im2, origin='lower', interpolation='none')
        self._ax3.imshow(difim, origin='lower', interpolation='none')
        plt.draw()

        info = outInfo.GetInformationObject(0)
        ue = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())

        out = vtk.vtkImageData.GetData(outInfo)
        out.DeepCopy(inp1)
        out.SetExtent(ue)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
