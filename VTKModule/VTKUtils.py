import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import vmtk.vmtkscripts as vmtk
import numpy as np
from VTKModule.VTKConvertor import VTKConvertor
from VTKModule.VTKReader import VTKReader
import os
import time


class VTKUtils:

    @classmethod
    def create_divider_plane(cls, clip_origin, normal):
        clipper_plane = vtk.vtkPlane()
        clipper_plane.SetOrigin(clip_origin[0], clip_origin[1], clip_origin[2])
        clipper_plane.SetNormal(normal[0], normal[1], normal[2])
        return clipper_plane

    @classmethod
    def get_divided_dataset(cls, clipper_plane, dataset):
        if isinstance(dataset, vtk.vtkSTLReader):
            artery_dataset = vtk.vtkClipPolyData()
            artery_dataset.SetInputConnection(dataset.GetOutputPort())
            artery_dataset.SetClipFunction(clipper_plane)
            try:
                artery_dataset.Update()
            except Exception as e:
                print(str(e))
                return
        else:
            artery_dataset = vtk.vtkClipDataSet()
            artery_dataset.SetInputData(dataset)
            artery_dataset.SetClipFunction(clipper_plane)
            try:
                artery_dataset.Update()
            except Exception as e:
                print(str(e))
                return

        return artery_dataset.GetOutput()

    @classmethod
    def calculate_centerline(cls, artery_surface):
        # Set up the vmtkCenterlinesNetwork object
        centerline_extractor = vmtk.vmtkCenterlinesNetwork()
        centerline_extractor.Surface = artery_surface
        try:
            centerline_extractor.Execute()
        except Exception as e:
            print(str(e))
            return
        return centerline_extractor.Centerlines

    @classmethod  # loading
    def get_smooth_centerline(cls, artery_surface):
        vmtk_centerline = cls.calculate_centerline(artery_surface)

        # Now, apply smoothing on the centerline
        centerline_smoothing = vmtk.vmtkCenterlineSmoothing()
        centerline_smoothing.Centerlines = vmtk_centerline
        try:
            centerline_smoothing.Execute()
        except Exception as e:
            print(str(e))
            return
        return centerline_smoothing.Centerlines

    @classmethod
    def get_polydata_cutter(cls, org_stl, pyvista_plane_stl):
        # Create an implicit function from plane_pyvista1_stl
        implicit_poly_data_distance = vtk.vtkImplicitPolyDataDistance()
        implicit_poly_data_distance.SetInput(pyvista_plane_stl)

        # Create a cutter to slice the dataset
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(implicit_poly_data_distance)
        cutter.SetInputData(org_stl)
        try:
            cutter.Update()
        except Exception as e:
            print(f"Warning: Connectivity failed! Error: {e}")

        return cutter.GetOutput()

    @classmethod
    def get_extracted_cells(cls, main_geometry, center, sphere_radius):
        sphere = vtk.vtkSphere()
        sphere.SetCenter(center)
        sphere.SetRadius(sphere_radius)

        extractor = vtk.vtkExtractGeometry()
        extractor.SetImplicitFunction(sphere)
        if isinstance(main_geometry, vtk.vtkUnstructuredGrid):
            extractor.SetInputData(main_geometry)
        else:
            extractor.SetInputData(main_geometry.GetOutput())

        try:
            extractor.Update()
        except Exception as e:
            print(str(e))
            return
        return extractor.GetOutput()

    @classmethod
    def apply_Delaunay2D(cls, surface_filter):
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(surface_filter)
        try:
            delaunay.Update()
        except Exception as e:
            print(str(e))
            return
        return delaunay.GetOutput()

    @classmethod
    def get_coords_and_connectivity(cls, polydata):
        points = polydata.GetPoints()
        lines = polydata.GetLines()
        # Convert points to a numpy array
        point_coords = np.array([points.GetPoint(i) for i in range(points.GetNumberOfPoints())])
        # Extract the connectivity information
        lines.InitTraversal()
        idList = vtk.vtkIdList()
        connectivity = []
        while lines.GetNextCell(idList):
            line = [idList.GetId(j) for j in range(idList.GetNumberOfIds())]
            connectivity.append(line)

        return point_coords, connectivity

    @classmethod
    def get_radius_list(cls, centerline_polydata):
        pointData = centerline_polydata.GetPointData()
        radiusArray = pointData.GetArray("MaximumInscribedSphereRadius")
        numPoints = centerline_polydata.GetNumberOfPoints()
        radius_list = []
        for i in range(numPoints):
            radius_list.append(radiusArray.GetValue(i))

        return radius_list

    @classmethod
    def get_radius_for_coord(cls, centerline_polydata, target_coord):
        point_coords, _ = cls.get_coords_and_connectivity(centerline_polydata)
        target_coord = np.array(target_coord)

        # Find the index of the target coordinate in the point coordinates array
        index = np.where((point_coords == target_coord).all(axis=1))[0]

        if len(index) > 0:
            radius = cls.get_radius_list(centerline_polydata)
            return radius[index[0]]
        else:
            raise ValueError("Coordinate not found in point data.")

    @classmethod
    def apply_taubin_smoothing(cls, input_file, output_file, num_iterations=300, pass_band=0.1):
        reader = cls.read_stl_file(input_file)

        # Apply Taubin Smoothing (Windowed Sinc Smoothing)
        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputConnection(reader.GetOutputPort())
        smoother.SetNumberOfIterations(num_iterations)
        smoother.SetPassBand(pass_band)
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()
        smoother.Update()

        # Write the smoothed mesh to output file
        writer = vtk.vtkOBJWriter() if output_file.endswith('.obj') else vtk.vtkSTLWriter()
        writer.SetFileName(output_file)
        writer.SetInputData(smoother.GetOutput())
        writer.Write()

    @classmethod
    def get_radius_by_point_id(cls, centerline_polydata, point_id):
        point_data = centerline_polydata.GetPointData()
        radius_array = point_data.GetArray("MaximumInscribedSphereRadius")
        if not radius_array:
            raise ValueError("Radius array 'MaximumInscribedSphereRadius' not found in point data.")

        return radius_array.GetValue(point_id)

    @classmethod
    def combine_stl_files(cls, surface_path, planes_dir, clipper_planes):
        main_surface = VTKReader.read_stl_file(surface_path)
        append_filter = vtk.vtkAppendPolyData()
        append_filter.AddInputData(main_surface.GetOutput())

        for k in clipper_planes:
            # Read each STL file
            plane_file_path = f"{planes_dir}{k}.stl"
            reader = vtk.vtkSTLReader()
            reader.SetFileName(plane_file_path)
            reader.Update()
            # Add the geometry to the append filter
            append_filter.AddInputData(reader.GetOutput())

        try:
            append_filter.Update()
        except Exception as e:
            print(str(e))
            return
        return append_filter.GetOutput()

    @classmethod
    def get_surface_from_volume(cls, vtk_dataset):
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputData(vtk_dataset)
        try:
            surface_filter.Update()
        except Exception as e:
            print(str(e))
            return
        return surface_filter

    @classmethod
    def calculate_ICP_matrix_registration(cls, target_output, pre_registration_data):
        icp = vtk.vtkIterativeClosestPointTransform()
        try:
            icp.SetSource(pre_registration_data)
            icp.SetTarget(target_output)
            icp.GetLandmarkTransform().SetModeToRigidBody()
            icp.SetMaximumNumberOfIterations(500)
            icp.StartByMatchingCentroidsOn()
            try:
                icp.Modified()
                icp.Update()
            except Exception as e:
                print(str(e))
                return
            icp_matrix_vtk = icp.GetMatrix()
        except Exception as e:
            raise ValueError("Error: calculate_ICP_matrix_registration,\n" + str(e))

        try:  # Create the transformed source
            transformed_source = vtk.vtkTransformFilter()
            transformed_source.SetInputData(pre_registration_data)
            transformed_source.SetTransform(icp)
            try:
                transformed_source.Update()
            except Exception as e:
                print(str(e))
                return
        except Exception as e:
            raise ValueError("Error: calculate_ICP_matrix_registration,\n" + str(e))

        icp_matrix_np = VTKConvertor.vtk_matrix_to_numpy(icp_matrix_vtk)

        return transformed_source.GetOutput(), icp_matrix_np

    @classmethod
    def apply_transformation_to_volume(cls, volume, transformation_matrix_np):
        rotation_matrix_np = transformation_matrix_np[:3, :3]
        rotated_flow_array = None

        flow_array = volume.GetPointData().GetArray("flow")
        if flow_array is not None:
            flow_data_np = vtk_to_numpy(flow_array)
            rotated_flow_data_np = np.dot(flow_data_np, rotation_matrix_np.T)
            rotated_flow_array = numpy_to_vtk(rotated_flow_data_np)
            rotated_flow_array.SetName("flow")

        vtk_matrix = VTKConvertor.numpy_array_to_vtk_matrix(transformation_matrix_np)
        transform = vtk.vtkTransform()
        transform.SetMatrix(vtk_matrix)

        transform_filter = vtk.vtkTransformFilter()
        transform_filter.SetInputData(volume)
        transform_filter.SetTransform(transform)
        try:
            transform_filter.Update()
        except Exception as e:
            print(str(e))
            return

        if flow_array is not None:
            transform_filter.GetOutput().GetPointData().AddArray(rotated_flow_array)
            transform_filter.GetOutput().GetPointData().SetActiveVectors("flow")

        return transform_filter.GetOutput()

    @classmethod
    def get_interpolator(cls, source_polydata, target, radius=0.001, sharpness=6, eccentricity=2):
        kernel = vtk.vtkEllipsoidalGaussianKernel()
        kernel.SetRadius(radius)
        kernel.SetSharpness(sharpness)
        kernel.SetEccentricity(eccentricity)

        interpolator = vtk.vtkPointInterpolator()
        interpolator.SetSourceData(source_polydata)
        interpolator.SetKernel(kernel)
        interpolator.SetNullPointsStrategyToClosestPoint()
        interpolator.SetInputData(target)
        try:
            interpolator.Update()
        except Exception as e:
            print(str(e))
            return
        return interpolator.GetOutput()

    @classmethod
    def get_polydata_normals(cls, dataset):
        normals_generator = vtk.vtkPolyDataNormals()
        normals_generator.SetInputConnection(dataset.GetOutputPort())
        normals_generator.ConsistencyOn()
        normals_generator.AutoOrientNormalsOn()
        normals_generator.Update()
        return normals_generator

    @classmethod
    def get_cell_size(cls, dataset):
        cell_sizes = vtk.vtkCellSizeFilter()
        cell_sizes.SetInputConnection(dataset.GetOutputPort())
        cell_sizes.SetComputeArea(True)
        cell_sizes.Update()
        return cell_sizes

    @classmethod
    def calculate_flow_rate(cls, vtk_dataset):
        surface_extractor = cls.get_surface_from_volume(vtk_dataset)
        polydata_normals = cls.get_polydata_normals(surface_extractor)
        cell_sizes = cls.get_cell_size(polydata_normals)

        normal_polydata = polydata_normals.GetOutput()
        normals_array = normal_polydata.GetPointData().GetNormals()

        for i in range(normals_array.GetNumberOfTuples()):
            normal = normals_array.GetTuple(i)
            if normal[2] < 0:
                adjusted_normal = (-normal[0], -normal[1], -normal[2])
                normals_array.SetTuple(i, adjusted_normal)

        normal_polydata.GetPointData().SetNormals(normals_array)
        areas = cell_sizes.GetOutput().GetCellData().GetArray("Area")
        flow_array = normal_polydata.GetPointData().GetArray("flow")

        # Compute flow rate contributions
        num_cells = normal_polydata.GetNumberOfCells()
        flow_rate_contributions = np.zeros(num_cells)
        for i in range(num_cells):
            cell = normal_polydata.GetCell(i)
            point_ids = cell.GetPointIds()
            cell_area = areas.GetValue(i)
            local_flow = np.zeros(3)

            # Average flow vectors at cell points
            for pid in range(point_ids.GetNumberOfIds()):
                local_flow += np.array(flow_array.GetTuple(point_ids.GetId(pid)))

            local_flow /= point_ids.GetNumberOfIds()

            # Use the first point's normal as an approximation
            normal_vector = np.array(normals_array.GetTuple(point_ids.GetId(0)))
            flow_rate_contributions[i] = np.dot(local_flow, normal_vector) * cell_area

        # Integrate flow rate over the surface
        integrated_flow_rate = np.sum(flow_rate_contributions)
        return integrated_flow_rate

    @classmethod
    def get_scaled_volume(cls, imaging_volume, scale_factor=0.001):
        original_flow_array = imaging_volume.GetPointData().GetArray("flow")
        if original_flow_array is not None:
            original_flowData = vtk_to_numpy(original_flow_array)

        transform = vtk.vtkTransform()

        scale_factors = [scale_factor, scale_factor, scale_factor]
        transform.Scale(scale_factors)

        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetInputData(imaging_volume)
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        if original_flow_array is not None:
            new_flow_array = numpy_to_vtk(original_flowData)
            new_flow_array.SetName("flow")
            transformFilter.GetOutput().GetPointData().AddArray(new_flow_array)
            transformFilter.GetOutput().GetPointData().SetActiveScalars("flow")

        return transformFilter.GetOutput()

    @classmethod
    def center_surface(cls, polydata, target):
        source_center = np.array(polydata.GetCenter())  # (Cx, Cy, Cz) of source
        target_center = np.array(target.GetCenter())  # (Cx, Cy, Cz) of target

        translation_vector = target_center - source_center  # Move source to match target
        transform = vtk.vtkTransform()
        transform.Translate(translation_vector)

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputData(polydata)
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        center_matrix_np = VTKConvertor.vtk_matrix_to_numpy(transform.GetMatrix())

        return transform_filter.GetOutput(), center_matrix_np

    @classmethod
    def compute_procrustes_matrix(cls, source, target):
        """
        Compute the transformation matrix using the Procrustes algorithm,
        which aligns two polydata surfaces based on their points.
        """
        procrustes = vtk.vtkProcrustesAlignmentFilter()
        procrustes.SetInputData(0, source)
        procrustes.SetInputData(1, target)
        procrustes.GetLandmarkTransform().SetModeToRigidBody()  # Rotation + translation only
        procrustes.Update()

        # Extract transformation matrix
        procrustes_matrix_vtk = procrustes.GetLandmarkTransform().GetMatrix()

        # Convert vtkMatrix4x4 to numpy array
        procrustes_matrix_np = np.array([[procrustes_matrix_vtk.GetElement(i, j) for j in range(4)] for i in range(4)])

        return procrustes_matrix_np

    @classmethod
    def get_cell_locator(cls, polydata):
        cell_locator = vtk.vtkCellLocator()
        cell_locator.SetDataSet(polydata)
        cell_locator.BuildLocator()

        return cell_locator