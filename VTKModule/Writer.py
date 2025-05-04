import vtk
import os
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import pandas as pd


class Writer:
    @classmethod
    def write_stl(cls, surface, first_line_desc, last_line_desc, file_name_path):
        try:
            stlWriter = vtk.vtkSTLWriter()
            # file_name_path.replace('/', '//')
            stlWriter.SetFileName(file_name_path)
            stlWriter.SetFileTypeToASCII()
            if isinstance(surface, vtk.vtkSTLReader):
                stlWriter.SetInputData(surface.GetOutput())
            else:
                stlWriter.SetInputData(surface)

            stlWriter.Write()
        except Exception as e:
            error_message = str(e)
            print(error_message)
            return
        with open(file_name_path, 'r') as file:
            lines = file.readlines()

        lines[0] = first_line_desc
        lines[-1] = last_line_desc
        with open(file_name_path, 'w') as file:
            file.writelines(lines)

    @classmethod
    def write_natural_scale_surface(cls, input_file_path, scale_factor=0.001):
        parts = input_file_path.split('\\')
        file_name = parts[-1]
        parts[-1] = ""
        parts = ['natural_scale' if part == 'imaging_scale' else part for part in parts]
        natural_scale_path = '\\'.join(parts)
        if not os.path.exists(natural_scale_path):
            os.makedirs(natural_scale_path)
        with open(input_file_path, 'r') as file:
            lines = file.readlines()

        for i in range(len(lines)):
            if lines[i].strip().startswith('vertex'):
                parts = lines[i].strip().split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                x_scaled, y_scaled, z_scaled = x * scale_factor, y * scale_factor, z * scale_factor
                lines[i] = f"vertex {x_scaled} {y_scaled} {z_scaled}\n"

        with open(natural_scale_path + file_name, 'w') as file:
            file.writelines(lines)

    @classmethod
    def write_xml_polydata(cls, centerline, vtp_file_path):
        centerline_writer = vtk.vtkXMLPolyDataWriter()
        centerline_writer.SetFileName(vtp_file_path)
        centerline_writer.SetInputData(centerline)
        centerline_writer.Write()

    @classmethod
    def write_pyvista_plane(cls, plane, plane_explainer, plane_file_path):
        plane_file_path = f"{plane_file_path}{plane_explainer}_plane.stl"
        plane.save(plane_file_path, binary=False)
        with open(plane_file_path, 'r+') as file:
            lines = file.readlines()
            lines[0] = f'solid {plane_explainer}\n'
            lines[-1] = f'endsolid {plane_explainer}\n'
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    @classmethod
    def write_clipped_surface(cls, surface, clipped_path):
        surface.save(clipped_path, binary=False)
        with open(clipped_path, 'r') as file:
            lines = file.readlines()
        lines[0] = 'solid artery\n'
        lines[-1] = 'endsolid artery\n'
        with open(clipped_path, 'w') as file:
            file.writelines(lines)

    @classmethod
    def write_surface_intersection(cls, mesh, intersection_name_path, explainer):
        connected_mesh = mesh.connectivity(extraction_mode='largest')
        connected_mesh.save(intersection_name_path, binary=False)
        with open(intersection_name_path, 'r') as file:
            lines = file.readlines()
        lines[0] = "solid " + explainer + '\n'
        lines[-1] = "endsolid " + explainer + '\n'
        with open(intersection_name_path, 'w') as file:
            file.writelines(lines)

    @classmethod
    def write_polydata(cls, centerline_polydata, centerline_pathName):
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(centerline_pathName)
        writer.SetInputData(centerline_polydata)
        writer.SetFileTypeToASCII()
        writer.Write()

    @classmethod
    def write_UnstructuredGrid(cls, unstructured_grid, pathName):
        writer = vtk.vtkUnstructuredGridWriter()
        writer.SetFileName(pathName)
        writer.SetInputData(unstructured_grid)
        writer.Write()

    @classmethod
    def write_natural_scale_volume(cls, pathName, scale_factor=0.001):
        parts = pathName.split('\\')
        file_name = parts[-1]
        parts[-1] = ""
        parts = ['natural_scale' if part == 'imaging_scale' else part for part in parts]
        natural_scale_path = '\\'.join(parts)
        if not os.path.exists(natural_scale_path):
            os.makedirs(natural_scale_path)

        reader = vtk.vtkDataSetReader()
        reader.SetFileName(pathName)
        reader.Update()

        original_flow_array = reader.GetOutput().GetPointData().GetArray("flow")
        if original_flow_array is not None:
            original_flowData = vtk_to_numpy(original_flow_array)

        transform = vtk.vtkTransform()

        scale_factors = [scale_factor, scale_factor, scale_factor]
        transform.Scale(scale_factors)

        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetInputData(reader.GetOutput())
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        if original_flow_array is not None:
            new_flow_array = numpy_to_vtk(original_flowData)
            new_flow_array.SetName("flow")
            transformFilter.GetOutput().GetPointData().AddArray(new_flow_array)
            transformFilter.GetOutput().GetPointData().SetActiveScalars("flow")

        writer = vtk.vtkDataSetWriter()
        writer.SetInputData(transformFilter.GetOutput())
        writer.SetFileName(natural_scale_path + file_name)
        writer.Write()

    @classmethod
    def write_bounds_text(cls, clipped_path, bounds_criteria_parameter):
        vtk_clipped_reader = vtk.vtkSTLReader()
        vtk_clipped_reader.SetFileName(clipped_path)
        vtk_clipped_reader.Update()

        bounds = vtk_clipped_reader.GetOutput().GetBounds()
        min_x, max_x, min_y, max_y, min_z, max_z = bounds

        scale_factor = 0.001
        parts = clipped_path.split('\\')
        parts[-1] = 'bounds.txt'
        parts = ['natural_scale' if part == 'imaging_scale' else part for part in parts]
        natural_scale_path = '\\'.join(parts)

        with open(natural_scale_path, 'w') as file1:
            file1.write(f"xmin  {round((min_x - bounds_criteria_parameter * abs(min_x)) * scale_factor, 4)};\n")
            file1.write(f"xmax  {round((max_x + bounds_criteria_parameter * abs(max_x)) * scale_factor, 4)};\n")
            file1.write(f"ymin  {round((min_y - bounds_criteria_parameter * abs(min_y)) * scale_factor, 4)};\n")
            file1.write(f"ymax  {round((max_y + bounds_criteria_parameter * abs(max_y)) * scale_factor, 4)};\n")
            file1.write(f"zmin  {round((min_z - bounds_criteria_parameter * abs(min_z)) * scale_factor, 4)};\n")
            file1.write(f"zmax  {round((max_z + bounds_criteria_parameter * abs(max_z)) * scale_factor, 4)};\n")

    @classmethod
    def write_point_text(cls, point, dir):
        x = point.get_x()
        y = point.get_y()
        z = point.get_z()

        scale_factor = 0.001
        parts = dir.split('\\')
        # parts[-1] = 'bifurcation_point.txt'
        parts = ['natural_scale' if part == 'imaging_scale' else part for part in parts]
        natural_scale_path = '\\'.join(parts)
        if not os.path.exists(natural_scale_path):
            os.makedirs(natural_scale_path)
        with open(natural_scale_path + 'bifurcation_point.txt', 'w') as file:
            file.write(f"x_bif  {x * scale_factor};\n")
            file.write(f"y_bif  {y * scale_factor};\n")
            file.write(f"z_bif  {z * scale_factor};\n")

    @classmethod
    def write_vtk_dataset(cls, vtk_dataset, path_name):
        writer = vtk.vtkDataSetWriter()
        writer.SetInputData(vtk_dataset)
        writer.SetFileName(path_name)
        writer.Write()

    @classmethod
    def write_U_file(cls, polydata_pathName, to_write_path_U, coeff=1):
        polydata_reader = vtk.vtkPolyDataReader()
        polydata_reader.SetFileName(polydata_pathName)
        polydata_reader.Update()
        points = polydata_reader.GetOutput().GetPoints()
        vectors = polydata_reader.GetOutput().GetPointData().GetVectors("flow")

        data = []

        for i in range(points.GetNumberOfPoints()):
            x, y, z = points.GetPoint(i)
            flow = vectors.GetTuple(i)
            data.append(
                [round(x, 6), round(y, 6), round(z, 6), round(flow[0], 6), round(flow[1], 6), round(flow[2], 6)])

        df = pd.DataFrame(data, columns=['x', 'y', 'z', 'flow_0', 'flow_1', 'flow_2'])

        selected_u_columns = df.iloc[:, 3:6] * coeff
        formatted_u_data = selected_u_columns.apply(lambda x: '(' + ' '.join(x.astype(str)) + ')', axis=1)
        final_u_data = f" {len(formatted_u_data)}\n(\n" + '\n'.join(formatted_u_data) + "\n)"

        if not os.path.exists(to_write_path_U):
            os.makedirs(to_write_path_U)
        with open(to_write_path_U + '/U', 'w') as file:
            file.write(final_u_data)

    @classmethod
    def write_Points_file(cls, polydata_path, to_write_path, coeff=1):
        polydata_reader = vtk.vtkPolyDataReader()
        polydata_reader.SetFileName(polydata_path)
        polydata_reader.Update()
        points = polydata_reader.GetOutput().GetPoints()
        vectors = polydata_reader.GetOutput().GetPointData().GetVectors("flow")

        data = []
        for i in range(points.GetNumberOfPoints()):
            x, y, z = points.GetPoint(i)
            flow = vectors.GetTuple(i)
            data.append(
                [round(x, 6), round(y, 6), round(z, 6), round(flow[0], 6), round(flow[1], 6), round(flow[2], 6)])

        df = pd.DataFrame(data, columns=['x', 'y', 'z', 'flow_0', 'flow_1', 'flow_2'])
        selected_points_columns = df.iloc[:, 0:3]
        multiplied_points = selected_points_columns * coeff

        # Format the multiplied data into the desired string format
        formatted_points_data = multiplied_points.apply(lambda x: '(' + ' '.join(x.astype(str)) + ')', axis=1)
        final_points_data = f"{len(formatted_points_data)}\n(\n" + '\n'.join(formatted_points_data) + "\n)"

        if not os.path.exists(to_write_path):
            os.makedirs(to_write_path)
        with open(to_write_path + "points", 'w') as file:
            file.write(final_points_data)

    @classmethod
    def write_new_flow_rate(cls, ica_dict, eca_dict, scaled_flow_rate_dir, last_time_parameter, last_time_dir):
        with open(scaled_flow_rate_dir + "ica.txt", "w") as file1:
            file1.write("(\n")
            for key1, value1 in ica_dict.items():
                file1.write(f"({key1 * last_time_parameter}\t{value1})\n")
            file1.write(")")

        with open(scaled_flow_rate_dir + "eca.txt", "w") as file2:
            file2.write("(\n")
            for key2, value2 in eca_dict.items():
                file2.write(f"({key2 * last_time_parameter}\t{value2})\n")
            file2.write(")")

        cls.repeat_flow_rate_output(scaled_flow_rate_dir + "ica.txt", last_time_parameter, last_time_dir)
        cls.repeat_flow_rate_output(scaled_flow_rate_dir + "eca.txt", last_time_parameter, last_time_dir)

    @classmethod
    def repeat_flow_rate_output(cls, file_pathName, coefficient, last_time_dir):
        with open(file_pathName, 'r') as file:
            lines = file.readlines()

        data_points = []
        for line in lines[1:-1]:
            line = line.strip('()\n')
            first, second = line.split()
            data_points.append((float(first), float(second)))

        parts = file_pathName.split('\\')
        file_name = parts[-1]
        parts[-1] = ""
        file_dir = '\\'.join(parts)

        with open(file_dir + "new" + file_name, 'w') as file:
            file.write('(\n')
            original_length = len(data_points)
            for i in range(3 * original_length):
                first = coefficient * i
                second = data_points[i % original_length][1]
                file.write(f'({first}\t{second})\n')
            file.write(')\n')

        cls.write_last_time(file_dir + "new" + file_name, last_time_dir)

    @classmethod
    def write_last_time(cls, input_namePath, output_dir):
        with open(input_namePath, 'r') as file:
            lines = file.readlines()

        last_line = lines[-2]  # Second to last line contains the data
        last_time_value = float(last_line.strip('()\n').split()[0])
        with open(output_dir + "last_time.txt", 'w') as output_file:
            output_file.write(f"Last_time  {last_time_value};\n")

    @classmethod
    def write_vtk_stl(cls, surface, pathName):
        stl_writer = vtk.vtkSTLWriter()
        stl_writer.SetFileName(pathName)
        stl_writer.SetInputData(surface)
        stl_writer.SetFileTypeToASCII()  # Save as ASCII STL
        stl_writer.Write()