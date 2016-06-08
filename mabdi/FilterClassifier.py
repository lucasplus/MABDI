import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import numpy as np
import matplotlib.pyplot as plt

from timeit import default_timer as timer
import logging


class FilterClassifier(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=2, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkImageData')

        self._postprocess = []
        self._postprocess_im1 = []
        self._postprocess_im2 = []
        self._postprocess_difim = []

    def set_postprocess(self, do_postprocess):
        self._postprocess = do_postprocess

    def postprocess_function(self):
        return self._postprocess_im1

    def RequestInformation(self, request, inInfo, outInfo):
        logging.info('')

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
        logging.info('')
        start = timer()

        # in images (vtkImageData)
        inp1 = vtk.vtkImageData.GetData(inInfo[0])
        inp2 = vtk.vtkImageData.GetData(inInfo[1])

        # convert to numpy arrays
        dim = inp1.GetDimensions()
        im1 = numpy_support.vtk_to_numpy(inp1.GetPointData().GetScalars())\
            .reshape((dim[1], dim[0]))
        dim = inp1.GetDimensions()
        im2 = numpy_support.vtk_to_numpy(inp2.GetPointData().GetScalars())\
            .reshape((dim[1], dim[0]))

        # difference in the images
        # im1 is assumed to be from the actual sensor
        # im2 is what we expect to see based on the world mesh
        # Anywhere the difference is small through those measurements away
        # by setting them to one. By doing this FilterDepthImageToSurface
        # will assume they lie on the clipping plane and will remove them
        difim = abs(im1 - im2) < 0.01
        if self._postprocess:
            self._postprocess_im1 = im1.copy()
        imout = im1
        imout[difim] = 1.0

        info = outInfo.GetInformationObject(0)
        ue = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())

        # output vtkImageData
        out = vtk.vtkImageData.GetData(outInfo)
        out.SetExtent(ue)
        (out.sizex, out.sizey, out.tmat, out.viewport) = \
            (inp1.sizex, inp1.sizey, inp1.tmat, inp1.viewport)
        out.GetPointData().SetScalars(
            numpy_support.numpy_to_vtk(imout.reshape(-1)))

        end = timer()
        logging.info('Execution time {:.4f} seconds'.format(end - start))

        return 1
