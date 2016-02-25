import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg

import logging


class ClassifierFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=2, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkImageData')

    def RequestInformation(self, request, inInfo, outInfo):
        logging.debug('')
        extent = (0, 639, 0, 479, 0, 0)
        info = outInfo.GetInformationObject(0)
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
                 extent, len(extent))
        return 1

    def RequestData(self, request, inInfo, outInfo):
        logging.debug('')
        start = timer()

        inImageData = vtk.vtkImageData.GetData(inInfo[0])

        out = vtk.vtkImageData.GetData(outInfo)
        out.DeepCopy(inImageData)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1
