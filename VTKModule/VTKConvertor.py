import vtk
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk


class VTKConvertor:
    @classmethod
    def vtk_to_numpy_points(cls, polydata):
        points = polydata.GetPoints()
        return vtk_to_numpy(points.GetData())

    @classmethod
    def numpy_to_vtk_polydata(cls, points, org_polydata):
        vtk_points = vtk.vtkPoints()
        try:
            vtk_points.SetData(numpy_to_vtk(points))
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(vtk_points)
            polydata.SetPolys(org_polydata.GetPolys())
            return polydata
        except Exception as e:
            print("Error has occurred in numpy_to_vtk_polydata()")
            print(str(e))
            return None

    @classmethod
    def vtk_matrix_to_numpy(cls, vtk_matrix):
        """Convert a vtkMatrix4x4 to a NumPy array."""
        numpy_matrix = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):
                numpy_matrix[i, j] = vtk_matrix.GetElement(i, j)
        return numpy_matrix

    @classmethod
    def numpy_array_to_vtk_matrix(cls, numpy_array):
        """Convert a NumPy array to a vtkMatrix4x4."""
        if numpy_array.shape != (4, 4):
            raise ValueError("numpy_array must be a 4x4 matrix.")

        vtk_matrix = vtk.vtkMatrix4x4()
        for i in range(4):
            for j in range(4):
                vtk_matrix.SetElement(i, j, numpy_array[i, j])
        return vtk_matrix
