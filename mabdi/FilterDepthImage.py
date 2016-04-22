import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg
from vtk.util import keys

import numpy as np

from timeit import default_timer as timer
import logging


class FilterDepthImage(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=0,
                                        nOutputPorts=1, outputType='vtkImageData')
        # vtk render objects
        self._ren = vtk.vtkRenderer()
        self._renWin = vtk.vtkRenderWindow()
        self._iren = vtk.vtkRenderWindowInteractor()

        # wire them up
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

        # calculate image bounds
        self._imageBounds = [0, 0, 0, 0]
        viewport = self._ren.GetViewport()
        size = self._renWin.GetSize()
        self._imageBounds[0] = int(viewport[0] * size[0])
        self._imageBounds[1] = int(viewport[1] * size[1])
        self._imageBounds[2] = int(viewport[2] * size[0] + 0.5) - 1
        self._imageBounds[3] = int(viewport[3] * size[1] + 0.5) - 1

    def set_polydata(self, in_polydata):
        """Set vtkPolyData that defines the environment."""
        logging.debug('')

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(in_polydata.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self._ren.AddActor(actor)

        self._iren.Initialize()
        self._iren.Render()

    def set_sensor_orientation(self, in_position, in_lookat):
        """
        :param in_position: Position of sensor in world coordinates.
        :param in_lookat: Where the sensor is looking in world coordinates.
        """
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

        # get current extent
        info = outInfo.GetInformationObject(0)
        ue = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())

        # get the depth values
        vfa = vtk.vtkFloatArray()
        ib = self._imageBounds
        self._renWin.GetZbufferData(ib[0], ib[1], ib[2], ib[3], vfa)

        # pack the depth values into the output vtkImageData
        out = vtk.vtkImageData.GetData(outInfo)
        out.GetPointData().SetScalars(vfa)
        out.SetExtent(ue)

        # append meta data to the vtkImageData containing intrinsic parameters
        out.viewport = self._ren.GetViewport()
        out.sizex = self._renWin.GetSize()[0]
        out.sizey = self._renWin.GetSize()[1]

        vtktmat = self._ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(
            self._ren.GetTiledAspectRatio(),
            0.0, 1.0)
        vtktmat.Invert()
        out.tmat = self.__vtkmatrix_to_numpy(vtktmat)

        end = timer()
        logging.debug('Execution time {:.4f} seconds'.format(end - start))

        return 1

    def __vtkmatrix_to_numpy(self, matrix):
        """
        Copies the elements of a vtkMatrix4x4 into a numpy array.

        :type matrix: vtk.vtkMatrix4x4
        :param matrix: The matrix to be copied into an array.
        :rtype: numpy.ndarray
        """
        m = np.ones((4, 4))
        for i in range(4):
            for j in range(4):
                m[i, j] = matrix.GetElement(i, j)
        return m
