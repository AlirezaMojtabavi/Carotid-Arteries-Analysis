import vtk
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk


class VTKReader:
    @classmethod
    def get_arteries_polydata_from_nifti(cls, nifti_file_path):
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(nifti_file_path)
        try:
            reader.Update()
        except Exception as e:
            print(str(e))
            return

        marchingCubes = vtk.vtkMarchingCubes()
        marchingCubes.SetInputConnection(reader.GetOutputPort())
        marchingCubes.SetValue(0, 1)  # Use the specified label
        try:
            marchingCubes.Update()
        except Exception as e:
            print(str(e))
            return

        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(marchingCubes.GetOutputPort())
        smoother.SetNumberOfIterations(15)
        smoother.SetRelaxationFactor(0.05)
        smoother.FeatureEdgeSmoothingOff()
        smoother.BoundarySmoothingOn()
        try:
            smoother.Update()
        except Exception as e:
            print(str(e))
            return

        return smoother.GetOutput()

    @classmethod
    def extract_volume_by_flow(cls, full_domain_pathName):
        print("Extracting flow data")
        # start_time = time.time()
        full_domain_reader = vtk.vtkDataSetReader()
        full_domain_reader.SetFileName(full_domain_pathName)
        full_domain_reader.ReadAllScalarsOn()
        try:
            full_domain_reader.Update()
        except Exception as e:
            print(str(e))
            return

        full_domain_output = full_domain_reader.GetOutput()

        # Extract flow data and compute magnitude
        flow_array = full_domain_output.GetPointData().GetArray("flow")
        flowData = vtk_to_numpy(flow_array)
        magflow = np.linalg.norm(flowData, axis=1)
        filteredIndices = np.where(magflow > 0.0000001)[0]

        # Map filtered points
        originalPoints = vtk_to_numpy(full_domain_output.GetPoints().GetData())
        filteredPoints = originalPoints[filteredIndices]

        # Set VTK points in one operation
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(filteredPoints))

        # Create an unstructured grid
        carotid_arteries_grid = vtk.vtkUnstructuredGrid()
        carotid_arteries_grid.SetPoints(points)

        # Add filtered flow data
        filteredFlowData = flowData[filteredIndices]
        flowDataVTK = numpy_to_vtk(filteredFlowData)
        flowDataVTK.SetName("flow")
        carotid_arteries_grid.GetPointData().AddArray(flowDataVTK)

        # Index mapping
        index_mapping = {old_index: new_index for new_index, old_index in enumerate(filteredIndices)}

        # Iterate over cells (keep your current logic for cell filtering)
        for cell_id in range(full_domain_output.GetNumberOfCells()):
            cell = full_domain_output.GetCell(cell_id)
            pointIds = cell.GetPointIds()
            new_point_ids = []
            valid_cell = True
            for i in range(pointIds.GetNumberOfIds()):
                original_index = pointIds.GetId(i)
                if original_index in index_mapping:
                    new_point_ids.append(index_mapping[original_index])
                else:
                    valid_cell = False
                    break
            if valid_cell:
                carotid_arteries_grid.InsertNextCell(cell.GetCellType(), len(new_point_ids), new_point_ids)

        return carotid_arteries_grid, full_domain_output

    @classmethod
    def read_stl_file(cls, input_file_path):
        stlReader = vtk.vtkSTLReader()
        stlReader.SetFileName(input_file_path)
        try:
            stlReader.Update()
        except Exception as e:
            print(str(e))
            return
        return stlReader

    @classmethod
    def read_vtk_polydata(cls, input_file_path):
        PolyDataReader = vtk.vtkPolyDataReader()
        PolyDataReader.SetFileName(input_file_path)
        try:
            PolyDataReader.Update()
        except Exception as e:
            print(str(e))
            return
        return PolyDataReader.GetOutput()

    @classmethod
    def read_vtk_UnstructuredGrid(cls, input_file_path):
        gridReader = vtk.vtkUnstructuredGridReader()
        gridReader.SetFileName(input_file_path)
        try:
            gridReader.Update()
        except Exception as e:
            print(str(e))
            return
        return gridReader.GetOutput()

    @classmethod
    def read_XMLUnstructuredGrid(cls, file_path):
        vtu_reader = vtk.vtkXMLUnstructuredGridReader()
        vtu_reader.SetFileName(file_path)
        try:
            vtu_reader.Update()
        except Exception as e:
            print(str(e))
            return
        return vtu_reader

    @classmethod
    def read_XMLPolydata(cls, file_path):
        vtp_reader = vtk.vtkXMLPolyDataReader()
        vtp_reader.SetFileName(file_path)
        try:
            vtp_reader.Update()
        except Exception as e:
            print(str(e))
            return
        return vtp_reader

    @classmethod
    def read_vtk_dataset(cls, file_path):
        vtk_reader = vtk.vtkDataSetReader()
        vtk_reader.SetFileName(file_path)
        try:
            vtk_reader.Update()
        except Exception as e:
            print(str(e))
            return
        return vtk_reader
