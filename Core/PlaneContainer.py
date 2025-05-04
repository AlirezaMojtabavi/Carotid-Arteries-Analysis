import pyvista as pv
from VTKModule.VTKUtils import VTKUtils as vtkUtl
from VTKModule.VTKReader import VTKReader as vtkRdr
from Core.Plane import Plane
from VTKModule.Writer import Writer
import numpy as np
from collections import OrderedDict
import os
import time


class PlaneContainer:
    def __init__(self):
        self.clipper_planes = OrderedDict()
        self.cut_planes = OrderedDict()
        self.flow_rate_dict = OrderedDict()

    @classmethod
    def get_divider_plane(cls, clip_origin, normal):
        clipper_plane = vtkUtl.create_divider_plane(clip_origin, normal)
        return clipper_plane

    @classmethod
    def divide_dataset(cls, divider_plane, smooth_arteries_polydata):
        artery_surface = vtkUtl.get_divided_dataset(divider_plane, smooth_arteries_polydata)
        return artery_surface

    def create_clipper_planes(self, clipper_points, clipper_vectors, planes_path, pyvista_plane_size_1):  # *
        for k in clipper_points:
            if clipper_points[k].get_radius() < 1.1:
                i_size = pyvista_plane_size_1
                j_size = pyvista_plane_size_1
            elif k == "cca":
                i_size = clipper_points[k].get_radius() * 4
                j_size = clipper_points[k].get_radius() * 4
            else:
                i_size = clipper_points[k].get_radius() * 3.5
                j_size = clipper_points[k].get_radius() * 3.5

            center_point_coords = [clipper_points[k].get_x(), clipper_points[k].get_y(), clipper_points[k].get_z()]
            pyvista_plane = pv.Plane(center=center_point_coords, direction=clipper_vectors[k], i_size=i_size,
                                     j_size=j_size)

            self.clipper_planes[k] = Plane(clipper_points[k], clipper_vectors[k], pyvista_plane)

            plane_file_path = f"{planes_path}{k}_plane.stl"
            pyvista_plane.save(plane_file_path, binary=False)

            with open(plane_file_path, 'r+') as file:
                lines = file.readlines()
                lines[0] = f'solid {k}\n'
                lines[-1] = f'endsolid {k}\n'
                file.seek(0)
                file.writelines(lines)
                file.truncate()

            Writer.write_natural_scale_surface(plane_file_path)

    def clip_surface(self, clipped_surface, clipper_points, artery_path, geometry_dir, sphere_radius_coef):
        i = 0
        final_result = None

        for k in self.clipper_planes:
            center = np.array([clipper_points[k].get_x(), clipper_points[k].get_y(), clipper_points[k].get_z()])
            distances = np.linalg.norm(clipped_surface.points - center, axis=1)
            if clipper_points[k].get_radius() < 1.4 and k != "ica" and k != "eca":
                sphere_radius = 7.5
            else:
                sphere_radius = clipper_points[k].get_radius() * sphere_radius_coef
            mask = distances <= sphere_radius
            cut_plane = self.clipper_planes[k].get_pyvista_plane()
            plane_normal = -cut_plane.compute_normals().cell_normals[0]
            plane_point = cut_plane.center
            mesh = self.calculate_surface_intersection(artery_path, plane_point, cut_plane, sphere_radius)

            Writer.write_surface_intersection(mesh, geometry_dir + k + '.stl', k)
            Writer.write_natural_scale_surface(geometry_dir + k + '.stl')
            points_to_clip = clipped_surface.extract_points(mask)
            clipped = points_to_clip.clip(normal=plane_normal, origin=plane_point, invert=False)
            remaining_points = clipped_surface.extract_points(~mask)
            merged_polydata = remaining_points.merge(clipped).clean()
            connected_polydata = merged_polydata.connectivity(extraction_mode='largest')
            clipped_surface = connected_polydata
            if i == 2:
                final_result = clipped_surface.extract_surface()
            i += 1
        return final_result

    @classmethod
    def calculate_surface_intersection(cls, surface_path, center, pyvista_plane, sphere_radius):
        main_surface = vtkRdr.read_stl_file(surface_path)

        extracted_cells = vtkUtl.get_extracted_cells(main_surface, center, sphere_radius)
        cutter_polydata = vtkUtl.get_polydata_cutter(extracted_cells, pyvista_plane)

        mesh = pv.wrap(vtkUtl.apply_Delaunay2D(cutter_polydata))
        connected_mesh = mesh.connectivity(extraction_mode='largest')

        return connected_mesh

    def create_cut_planes(self, cutpoints, vectors, cut_planes_dir, const_plane_size, coef_cutplane_size):
        plane_list = []
        i_size = 0
        j_size = 0
        for k in cutpoints:
            i = 0
            for point in cutpoints[k]:
                if point.get_radius() < 1.1:
                    i_size = const_plane_size
                    j_size = const_plane_size
                # elif k == "ica2" or k == "eca2":
                #     i_size = cutpoints[k].get_radius() * 3 + 4
                #     j_size = cutpoints[k].get_radius() * 3 + 4
                else:
                    i_size = point.get_radius() * coef_cutplane_size
                    j_size = point.get_radius() * coef_cutplane_size

                center_point_coords = [point.get_x(), point.get_y(), point.get_z()]
                pyvista_plane = pv.Plane(center=center_point_coords, direction=vectors[k][i], i_size=i_size,
                                         j_size=j_size)
                new_plane = Plane(point, vectors[k][i], pyvista_plane)
                plane_list.append(new_plane)

                plane_file_path = f"{cut_planes_dir}{k}{i}_plane.stl"
                pyvista_plane.save(plane_file_path, binary=False)

                with open(plane_file_path, 'r+') as file:
                    lines = file.readlines()
                    lines[0] = f'solid {k}\n'
                    lines[-1] = f'endsolid {k}\n'
                    file.seek(0)
                    file.writelines(lines)
                    file.truncate()

                Writer.write_natural_scale_surface(plane_file_path)
                i = i + 1
            self.cut_planes[k] = plane_list.copy()
            plane_list.clear()

    def customize_cut_planes(self, removed_list):
        for name in removed_list:
            for k in self.cut_planes:
                if name[0] == k[0]:
                    self.cut_planes[k][int(name[-1])] = None
                else:
                    continue

    def cut_volume(self, artery_volume, output_dir, natural_scale_dir,
                   sphere_radius_coef, cut_planes_dir, start_name, scale=1):
        flow_rate_cca = 0  # start name = flow_ or vtu_intersection_
        for k in self.cut_planes:
            i = 0
            for plane in self.cut_planes[k]:
                plane_file_path = f"{cut_planes_dir}{k}{i}_plane.stl"
                if not os.path.exists(plane_file_path):
                    i += 1
                    continue
                if plane is None:
                    i += 1
                    continue
                pyvista_plane = plane.get_pyvista_plane()
                if not scale == 1:
                    pyvista_plane.scale([scale, scale, scale], inplace=True)
                    sphere_radius = plane.get_point().get_radius() * sphere_radius_coef * scale
                else:
                    sphere_radius = plane.get_point().get_radius() * sphere_radius_coef
                plane_point = pyvista_plane.center
                start_time_intersection = time.time()
                mesh = self.calculate_volume_intersection(artery_volume, plane_point, sphere_radius, pyvista_plane)
                end_time_intersection = time.time()
                elapsed_time_intersection = end_time_intersection - start_time_intersection
                if elapsed_time_intersection >= 1.0:
                    print(f"calculate_intersection {elapsed_time_intersection:.2f} seconds.\n")
                    print("\n")

                if start_name == "flow_":
                    mesh.save(output_dir + start_name + k + str(i) + '.vtk', binary=False)
                    Writer.write_natural_scale_volume(output_dir + start_name + k + str(i) + '.vtk')
                else:
                    mesh.save(output_dir + start_name + k + str(i) + '.vtk', binary=False)
                    # Writer.write_natural_scale_volume(output_dir + start_name + k + str(i) + '.vtk', scale_factor=1.0)

                    source_dataset = vtkRdr.read_vtk_dataset(natural_scale_dir + "flow_" + k + str(i) + '.vtk')
                    target_dataset = vtkRdr.read_vtk_dataset(output_dir + start_name + k + str(i) + '.vtk')

                    interpolator = vtkUtl.get_interpolator(source_dataset.GetOutput(), target_dataset.GetOutput())
                    Writer.write_vtk_dataset(interpolator, natural_scale_dir + 'interpolated_' + k + str(i) + '.vtk')

                    interpolated_flow_rate = vtkUtl.calculate_flow_rate(interpolator)
                    self.flow_rate_dict[k + str(i)] = interpolated_flow_rate

                    print(k + str(i) + ": " + str(interpolated_flow_rate))

                if not scale == 1:
                    self.rescale_pyvista_plane(pyvista_plane)
                i += 1
        print('\n')
    @classmethod
    def rescale_pyvista_plane(cls, pyvista_plane, scale=1000.0):
        pyvista_plane.scale([scale, scale, scale], inplace=True)

    @classmethod
    def calculate_volume_intersection(cls, volume, center, sphere_radius, pyvista_plane):
        extracted_cells = vtkUtl.get_extracted_cells(volume, center, sphere_radius)
        cutter_polydata = vtkUtl.get_polydata_cutter(extracted_cells, pyvista_plane)
        if cutter_polydata.GetNumberOfPoints() == 0 or cutter_polydata.GetNumberOfCells() == 0:
            print("Error: Empty or invalid polydata!")
            exit(1)

        mesh = pv.wrap(cutter_polydata)
        try:
            connected_mesh = mesh.connectivity(extraction_mode='largest')
        except Exception as e:
            print(f"Error occurred for calculate_volume_intersection: {e}")

        return connected_mesh

    def get_cut_planes_dict(self):
        return self.cut_planes

    def get_clipper_planes_dict(self):
        return self.clipper_planes

    def get_flow_rate_dict(self):
        return self.flow_rate_dict

    def calculate_cca_flow_rate(self, artery_volume, output_dir, natural_scale_dir, sphere_radius_coef, target_dataset):
        scaled_artery_volume = vtkUtl.get_scaled_volume(artery_volume)
        plane = self.clipper_planes["cca"]
        pyvista_plane = plane.get_pyvista_plane()
        self.rescale_pyvista_plane(pyvista_plane, 0.001)
        sphere_radius = plane.get_point().get_radius() * sphere_radius_coef
        plane_point = pyvista_plane.center
        mesh = self.calculate_volume_intersection(scaled_artery_volume, plane_point, sphere_radius, pyvista_plane)

        mesh.save(output_dir + "flow_cca.vtk", binary=False)
        Writer.write_natural_scale_volume(output_dir + "flow_cca.vtk", 1)

        source_dataset = vtkRdr.read_vtk_dataset(natural_scale_dir + "flow_cca.vtk")

        interpolator = vtkUtl.get_interpolator(source_dataset.GetOutput(), target_dataset)
        Writer.write_vtk_dataset(interpolator, natural_scale_dir + "cca_interpolated.vtk")
        interpolated_flow_rate = vtkUtl.calculate_flow_rate(interpolator)
        self.flow_rate_dict["cca"] = interpolated_flow_rate
        self.rescale_pyvista_plane(pyvista_plane)
