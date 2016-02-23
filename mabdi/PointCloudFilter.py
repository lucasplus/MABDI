import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as alg
import numpy as np


class PointCloudFilter(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
                                        nInputPorts=1, inputType='vtkImageData',
                                        nOutputPorts=1, outputType='vtkPolyData')
        self.__ren = []
        self.__renWin = []

        self.__sizex = []
        self.__sizey = []

        self.__display_pts = []
        self.__viewport_pts = []
        self.__world_pts = []
        self.__polydata = vtk.vtkPolyData()

    def SetRendererAndRenderWindow(self, renderer, render_window):
        if renderer != self.__ren:
            self.__ren = renderer
        if render_window != self.__renWin:
            self.__renWin = render_window
        self.Modified()
        self.__initialize_containers()

    def GetRenderer(self):
        return self.__ren

    def GetRenderWindow(self):
        return self.__renWin

    def __initialize_containers(self):
        # save the new size
        (self.__sizex, self.__sizey) = self.__renWin.GetSize()
        # new display points
        self.__display_pts = np.ones((2, self.__sizex * self.__sizey))
        count = 0
        for i in np.arange(self.__sizey):
            for j in np.arange(self.__sizex):
                self.__display_pts[0, count] = j
                self.__display_pts[1, count] = i
                count += 1
        # new viewport points
        viewport = self.__ren.GetViewport()
        self.__viewport_pts = np.ones((4, self.__display_pts.shape[1]))
        self.__viewport_pts[0, :] = 2.0 * (self.__display_pts[0, :] - self.__sizex * viewport[0]) / (
            self.__sizex * (viewport[2] - viewport[0])) - 1.0
        self.__viewport_pts[1, :] = 2.0 * (self.__display_pts[1, :] - self.__sizey * viewport[1]) / (
            self.__sizey * (viewport[3] - viewport[1])) - 1.0
        # new world points (of the right size)
        self.__world_pts = np.ones(self.__viewport_pts.shape)
        # initialize vtkPolyData
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for i in np.arange(self.__world_pts.shape[1]):
            pt_id = points.InsertNextPoint(self.__world_pts[0:3, i])
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pt_id)
        self.__polydata.SetPoints(points)
        self.__polydata.SetVerts(vertices)

    def RequestData(self, request, inInfo, outInfo):
        print 'PointCloudFilter RequestData'

        # all the depth values
        inp = dsa.WrapDataObject(vtk.vtkImageData.GetData(inInfo[0]))
        depth = numpy_support.vtk_to_numpy(inp.PointData['ImageScalars'])

        # update the viewport points, check to see if render window size has changed
        self.__viewport_pts[2, :] = depth

        # transformation matrix, viewport coordinates -> world coordinates
        tmat = self.__ren.GetActiveCamera().GetCompositeProjectionTransformMatrix(
            self.__ren.GetTiledAspectRatio(),
            0.0, 1.0)
        tmat.Invert()
        tmat = self.__vtkmatrix_to_numpy(tmat)

        # project to world coordinates
        self.__world_pts = np.dot(tmat, self.__viewport_pts)
        self.__world_pts = self.__world_pts / self.__world_pts[3]

        # update polydata
        points = vtk.vtkPoints()
        vtkarray = dsa.numpyTovtkDataArray(self.__world_pts[0:3, :].T)
        points.SetData(vtkarray)
        self.__polydata.SetPoints(points)
        out = vtk.vtkPolyData.GetData(outInfo)
        out.ShallowCopy(self.__polydata)

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

