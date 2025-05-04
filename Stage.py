from PyQt5.QtWidgets import QApplication
from MathematicalFunction import MathematicalFunction as MathFun
from VTKModule.Writer import Writer
from VTKModule.VTKReader import VTKReader as vtkRdr
from VTKModule.VTKUtils import VTKUtils as vtkUtl
from VTKModule.VTKConvertor import VTKConvertor as vtkCnvrt
from Core.Artery import Artery
from Core.PlaneContainer import PlaneContainer
from VTKModule.VTKPlot import VTKPlot as vtkplt
import pyvista as pv
import numpy as np
import os
from collections import OrderedDict
from PyQt5.QtCore import pyqtSignal, QObject


class Stage(QObject):
    left_registration_actors_signal = pyqtSignal(list)
    right_registration_actors_signal = pyqtSignal(list)
    save_centerline_signal = pyqtSignal()

    def __init__(self, files_configuration, side_chooser):
        super().__init__()
        self.right_vmtk_centerline = None
        self.left_vmtk_centerline = None
        self.flow_input_files = None
        self.fl_confg = files_configuration
        self.side_chooser = side_chooser
        self.left_artery = None
        self.right_artery = None
        self.left_pln_contnr = PlaneContainer()
        self.right_pln_contnr = PlaneContainer()
        self.ica_left_dict = OrderedDict()
        self.ica_right_dict = OrderedDict()
        self.eca_left_dict = OrderedDict()
        self.eca_right_dict = OrderedDict()
        self.updated_variation_rate = 0
        self.updated_sphere_coef = 0
        self.updated_planes_coef = 0

    def extract_arteries_surface(self):
        if os.path.exists(self.fl_confg.get_left_artery_surface_input_pathName()) and not self.side_chooser == 1:
            left_artery_surface = vtkRdr.read_stl_file(self.fl_confg.get_left_artery_surface_input_pathName())
            Writer.write_stl(left_artery_surface, 'solid left\n', 'endsolid left\n',
                             self.fl_confg.get_left_artery_surface_path())
            Writer.write_natural_scale_surface(self.fl_confg.get_left_artery_surface_path())
            self.left_artery = Artery(left_artery_surface.GetOutput())

        if os.path.exists(self.fl_confg.get_right_artery_surface_input_pathName()) and not self.side_chooser == 0:
            right_artery_surface = vtkRdr.read_stl_file(self.fl_confg.get_right_artery_surface_input_pathName())
            Writer.write_stl(right_artery_surface, 'solid right\n', 'endsolid right\n',
                             self.fl_confg.get_right_artery_surface_path())
            Writer.write_natural_scale_surface(self.fl_confg.get_right_artery_surface_path())
            self.right_artery = Artery(right_artery_surface.GetOutput())

        if self.right_artery is not None or self.left_artery is not None:
            return

        if os.path.exists(self.fl_confg.get_NIFTI_pathName()) and \
                not os.path.exists(self.fl_confg.get_smooth_original_geometry_namepath()):
            arteries_polydata = vtkRdr.get_arteries_polydata_from_nifti(self.fl_confg.get_NIFTI_pathName())
            Writer.write_stl(arteries_polydata,
                             'solid original_geometry\n', 'endsolid original_geometry\n',
                             self.fl_confg.get_original_geometry_namepath())

            Writer.write_natural_scale_surface(self.fl_confg.get_original_geometry_namepath())

            vtkUtl.apply_taubin_smoothing(self.fl_confg.get_original_geometry_namepath(),
                                          self.fl_confg.get_smooth_original_geometry_namepath())
        if os.path.exists(self.fl_confg.get_smooth_original_geometry_namepath_input()) and \
                not os.path.exists(self.fl_confg.get_smooth_original_geometry_namepath()):
            smooth_arteries_polydata = vtkRdr.read_stl_file(self.fl_confg.get_smooth_original_geometry_namepath_input())
            Writer.write_stl(smooth_arteries_polydata,
                             'solid smooth_geometry\n', 'endsolid smooth_geometry\n',
                             self.fl_confg.get_smooth_original_geometry_namepath())

        smooth_arteries_polydata = vtkRdr.read_stl_file(self.fl_confg.get_smooth_original_geometry_namepath())
        # Plot.render_two_poly_data(arteries_polydata, smooth_arteries_polydata,
        #                           "Original geometry and Smoothed geometry")
        Writer.write_natural_scale_surface(self.fl_confg.get_smooth_original_geometry_namepath())
        self.set_arteries_surface(smooth_arteries_polydata)

    def set_arteries_surface(self, smooth_arteries_polydata):
        clip_origin = MathFun.calculate_centerpoint(smooth_arteries_polydata.GetOutput())
        left_normal = [1.0, 0.0, 0.0]
        right_normal = [-1.0, 0.0, 0.0]
        left_artery_surface = None
        right_artery_surface = None
        if not self.side_chooser == 1:
            left_plane_divider = self.left_pln_contnr.get_divider_plane(clip_origin, left_normal)
            left_artery_surface = self.left_pln_contnr.divide_dataset(left_plane_divider, smooth_arteries_polydata)
            self.left_artery = Artery(left_artery_surface)

        if not self.side_chooser == 0:
            right_plane_divider = self.right_pln_contnr.get_divider_plane(clip_origin, right_normal)
            right_artery_surface = self.right_pln_contnr.divide_dataset(right_plane_divider, smooth_arteries_polydata)
            self.right_artery = Artery(right_artery_surface)

        if self.side_chooser == 0:
            vtkplt.render_one_polydata(left_artery_surface)
        elif self.side_chooser == 1:
            vtkplt.render_one_polydata(right_artery_surface)
        else:
            vtkplt.render_two_poly_data(left_artery_surface, right_artery_surface,
                                        "Left and Right Arteries Surfaces")

        if not self.side_chooser == 1:
            Writer.write_stl(left_artery_surface, 'solid left\n', 'endsolid left\n',
                             self.fl_confg.get_left_artery_surface_path())
            Writer.write_natural_scale_surface(self.fl_confg.get_left_artery_surface_path())

        if not self.side_chooser == 0:
            Writer.write_stl(right_artery_surface, 'solid right\n', 'endsolid right\n',
                             self.fl_confg.get_right_artery_surface_path())
            Writer.write_natural_scale_surface(self.fl_confg.get_right_artery_surface_path())

    def extract_arteries_centerline(self, try_again=None, side=None):
        left_centerline_actors = []
        right_centerline_actors = []
        if try_again is not None:
            if side == "left":
                left_centerline_actors.clear()
                self.left_vmtk_centerline = None
                self.left_vmtk_centerline = vtkUtl.get_smooth_centerline(self.left_artery.get_surface())
                left_org_surface_actor, left_smooth_surface_actor = vtkplt.render_two_poly_data(
                    self.left_artery.get_surface(),
                    self.left_vmtk_centerline,
                    "Left Artery and it's centerline")
                left_centerline_actors.append(left_org_surface_actor)
                left_centerline_actors.append(left_smooth_surface_actor)
            elif side == "right":
                right_centerline_actors.clear()
                self.right_vmtk_centerline = None
                self.right_vmtk_centerline = vtkUtl.get_smooth_centerline(self.right_artery.get_surface())
                right_org_surface_actor, right_smooth_surface_actor = vtkplt.render_two_poly_data(
                    self.right_artery.get_surface(),
                    self.right_vmtk_centerline,
                    "Right Artery and it's centerline")
                right_centerline_actors.append(right_org_surface_actor)
                right_centerline_actors.append(right_smooth_surface_actor)
            else:
                if not self.side_chooser == 1:
                    left_centerline_actors.clear()
                    self.left_vmtk_centerline = None
                    self.left_vmtk_centerline = vtkUtl.get_smooth_centerline(self.left_artery.get_surface())
                    left_org_surface_actor, left_smooth_surface_actor = vtkplt.render_two_poly_data(
                        self.left_artery.get_surface(),
                        self.left_vmtk_centerline,
                        "Left Artery and it's centerline")
                    left_centerline_actors.append(left_org_surface_actor)
                    left_centerline_actors.append(left_smooth_surface_actor)
                if not self.side_chooser == 0:
                    right_centerline_actors.clear()
                    self.right_vmtk_centerline = None
                    self.right_vmtk_centerline = vtkUtl.get_smooth_centerline(self.right_artery.get_surface())
                    right_org_surface_actor, right_smooth_surface_actor = vtkplt.render_two_poly_data(
                        self.right_artery.get_surface(),
                        self.right_vmtk_centerline,
                        "Right Artery and it's centerline")
                    right_centerline_actors.append(right_org_surface_actor)
                    right_centerline_actors.append(right_smooth_surface_actor)

        else:
            if not self.side_chooser == 1:
                if os.path.exists(self.fl_confg.get_left_centerline_pathName()):
                    self.left_vmtk_centerline = vtkRdr.read_vtk_polydata(self.fl_confg.get_left_centerline_pathName())
                elif not os.path.exists(self.fl_confg.get_left_centerline_pathName()):
                    self.left_vmtk_centerline = vtkUtl.get_smooth_centerline(self.left_artery.get_surface())

                left_org_surface_actor, left_smooth_surface_actor = vtkplt.render_two_poly_data(
                    self.left_artery.get_surface(),
                    self.left_vmtk_centerline,
                    "Left Artery and it's centerline")
                left_centerline_actors.append(left_org_surface_actor)
                left_centerline_actors.append(left_smooth_surface_actor)

            if not self.side_chooser == 0:
                if os.path.exists(self.fl_confg.get_right_centerline_pathName()):
                    self.right_vmtk_centerline = vtkRdr.read_vtk_polydata(self.fl_confg.get_right_centerline_pathName())
                elif not os.path.exists(self.fl_confg.get_right_centerline_pathName()):
                    self.right_vmtk_centerline = vtkUtl.get_smooth_centerline(self.right_artery.get_surface())

                right_org_surface_actor, right_smooth_surface_actor = vtkplt.render_two_poly_data(
                    self.right_artery.get_surface(),
                    self.right_vmtk_centerline,
                    "Right Artery and it's centerline")
                right_centerline_actors.append(right_org_surface_actor)
                right_centerline_actors.append(right_smooth_surface_actor)

        return left_centerline_actors, right_centerline_actors

    def save_and_set_centerline(self):
        if not self.side_chooser == 1:
            Writer.write_polydata(self.left_vmtk_centerline, self.fl_confg.get_left_centerline_pathName())
            self.left_artery.create_centerline(self.left_vmtk_centerline)
            left_bf_point = self.left_artery.get_bf_point()
            Writer.write_point_text(left_bf_point, self.fl_confg.get_left_geometry_dir())
        if not self.side_chooser == 0:
            Writer.write_polydata(self.right_vmtk_centerline, self.fl_confg.get_right_centerline_pathName())
            self.right_artery.create_centerline(self.right_vmtk_centerline)
            right_bf_point = self.right_artery.get_bf_point()
            Writer.write_point_text(right_bf_point, self.fl_confg.get_right_geometry_dir())

    def get_clipped_arteries_surface(self, variation_rate=None, sphere_radius_coef=None):
        actor_plot_left = None
        actor_plot_right = None
        if variation_rate is None:
            variation_rate = self.fl_confg.get_variation_rate()
        else:
            self.updated_variation_rate = variation_rate
        if sphere_radius_coef is None:
            self.updated_sphere_coef = self.fl_confg.get_sphere_radius_coef()
        else:
            self.updated_sphere_coef = sphere_radius_coef

        if not self.side_chooser == 1:
            left_clipper_points, left_clipper_vectors = self.left_artery.get_clipper_points_vectors(variation_rate)
            self.left_pln_contnr.create_clipper_planes(left_clipper_points, left_clipper_vectors,
                                                       self.fl_confg.get_left_clipper_planes_dir(),
                                                       self.fl_confg.get_plane_size())

            self.clip_artery_surface(self.left_artery, self.fl_confg.get_left_artery_surface_path(),
                                     self.fl_confg.get_left_geometry_dir(),
                                     self.fl_confg.get_left_clipped_surface_pathName(), self.left_pln_contnr)

            combined_clipped_artery_left = vtkUtl.combine_stl_files(self.fl_confg.get_left_clipped_surface_pathName(),
                                                                    self.fl_confg.get_left_geometry_dir(),
                                                                    self.left_pln_contnr.get_clipper_planes_dict())

            Writer.write_stl(combined_clipped_artery_left, 'solid combined\n', 'endsolid combined\n',
                             self.fl_confg.get_combined_left_namePath())
            Writer.write_natural_scale_surface(self.fl_confg.get_combined_left_namePath())
            actor_plot_left = vtkplt.render_vtkSTL_file(self.fl_confg.get_combined_left_namePath())

        if not self.side_chooser == 0:
            right_clipper_points, right_clipper_vectors = self.right_artery.get_clipper_points_vectors(variation_rate)
            self.right_pln_contnr.create_clipper_planes(right_clipper_points, right_clipper_vectors,
                                                        self.fl_confg.get_right_clipper_planes_dir(),
                                                        self.fl_confg.get_plane_size())
            self.clip_artery_surface(self.right_artery, self.fl_confg.get_right_artery_surface_path(),
                                     self.fl_confg.get_right_geometry_dir(),
                                     self.fl_confg.get_right_clipped_surface_pathName(), self.right_pln_contnr)
            combined_clipped_artery_right = vtkUtl.combine_stl_files(
                self.fl_confg.get_right_clipped_surface_pathName(),
                self.fl_confg.get_right_geometry_dir(),
                self.right_pln_contnr.get_clipper_planes_dict())

            Writer.write_stl(combined_clipped_artery_right, 'solid combined\n', 'endsolid combined\n',
                             self.fl_confg.get_combined_right_namePath())
            Writer.write_natural_scale_surface(self.fl_confg.get_combined_right_namePath())
            actor_plot_right = vtkplt.render_vtkSTL_file(self.fl_confg.get_combined_right_namePath())

        return actor_plot_left, actor_plot_right

    def clip_artery_surface(self, artery, surface_artery_pathName, geometry_dir, clipped_path, plane_container):
        original_geometry = pv.read(surface_artery_pathName)
        clipped_surface = original_geometry
        clipper_points, clipper_vectors = artery.get_clipper_points()

        clipped_artery = plane_container.clip_surface(clipped_surface, clipper_points, surface_artery_pathName,
                                                      geometry_dir, self.updated_sphere_coef)

        Writer.write_clipped_surface(clipped_artery, clipped_path)
        # vtkplt.render_vtkSTL_file(clipped_path, "Clipped Surface")
        Writer.write_natural_scale_surface(clipped_path)
        Writer.write_bounds_text(clipped_path, float(self.fl_confg.project_config.get('Parameters', 'bounds_criteria')))

    def preparing_cut_planes(self, cutplane_size_coef):
        left_actors_dict = None
        right_actors_dict = None
        if not self.side_chooser == 1:
            left_cutpoints, left_vectors = self.left_artery.get_cutpoints_vectors()
            self.left_pln_contnr.create_cut_planes(left_cutpoints, left_vectors,
                                                   self.fl_confg.get_left_cut_planes_dir(),
                                                   self.fl_confg.get_plane_size(), cutplane_size_coef)
            left_actors_dict = vtkplt.rendering_surface_centerline_sphere_cuts(self.left_artery.get_surface(),
                                                                               self.left_pln_contnr.get_cut_planes_dict(),
                                                                               self.left_artery.get_centerline().get_centerline_polydata(),
                                                                               self.fl_confg.get_sphere_radius_coef(),
                                                                               self.left_pln_contnr.get_clipper_planes_dict(),
                                                                               "Left artery volume and it's cut planes")

        if not self.side_chooser == 0:
            right_cutpoints, right_vectors = self.right_artery.get_cutpoints_vectors()
            self.right_pln_contnr.create_cut_planes(right_cutpoints, right_vectors,
                                                    self.fl_confg.get_right_cut_planes_dir(),
                                                    self.fl_confg.get_plane_size(), cutplane_size_coef)

            right_actors_dict = vtkplt.rendering_surface_centerline_sphere_cuts(self.right_artery.get_surface(),
                                                                                self.right_pln_contnr.get_cut_planes_dict(),
                                                                                self.right_artery.get_centerline().get_centerline_polydata(),
                                                                                self.fl_confg.get_sphere_radius_coef(),
                                                                                self.right_pln_contnr.get_clipper_planes_dict(),
                                                                                "Right artery volume and it's cut "
                                                                                "planes")

        return left_actors_dict, right_actors_dict

    def update_cutplanes(self, removed_list):
        if not self.side_chooser == 1:
            self.left_pln_contnr.customize_cut_planes(removed_list)

        if not self.side_chooser == 0:
            self.right_pln_contnr.customize_cut_planes(removed_list)

    def prepare_volume_processing(self):
        current_input_flow = self.fl_confg.get_input_volume_dir()
        flow_input_files = [f for f in os.listdir(current_input_flow) if f.endswith('.vtk')]

        # Sort the list based on the extracted numeric value
        self.flow_input_files = sorted(flow_input_files, key=MathFun.extract_number)
        current_full_domain_path = os.path.join(current_input_flow, flow_input_files[0])
        if not os.path.exists(self.fl_confg.get_carotid_arteries_volume_pathName(0)):
            carotid_arteries_grid, full_domain_output = vtkRdr.extract_volume_by_flow(current_full_domain_path)
        else:
            carotid_arteries_grid = vtkRdr.read_vtk_UnstructuredGrid(
                self.fl_confg.get_carotid_arteries_volume_pathName(0))
            # Plot.render_DataSet(self.fl_confg.get_carotid_arteries_volume_pathName(i))

        clip_origin = MathFun.calculate_centerpoint(carotid_arteries_grid)
        if not self.side_chooser == 1:
            left_normal = [0.0, 1.0, 0.0]
            left_plane_clipper = vtkUtl.create_divider_plane(clip_origin, left_normal)
            left_artery_volume = vtkUtl.get_divided_dataset(left_plane_clipper, carotid_arteries_grid)

            left_transform_matrix, left_registration_actors = self.registration(
                source_output=left_artery_volume,
                target=self.left_artery.get_surface(),
                current_time_step_dir=self.fl_confg.get_current_timestep_flow_left_dir(0))

            QApplication.processEvents()
            self.left_artery.set_registration_matrix(left_transform_matrix)
            self.left_registration_actors_signal.emit(left_registration_actors)

        if not self.side_chooser == 0:
            right_normal = [0.0, -1.0, 0.0]
            right_plane_clipper = vtkUtl.create_divider_plane(clip_origin, right_normal)
            right_artery_volume = vtkUtl.get_divided_dataset(right_plane_clipper, carotid_arteries_grid)

            right_transform_matrix, right_registration_actors = self.registration(
                source_output=right_artery_volume,
                target=self.right_artery.get_surface(),
                current_time_step_dir=self.fl_confg.get_current_timestep_flow_right_dir(0))

            QApplication.processEvents()
            self.right_registration_actors_signal.emit(right_registration_actors)
            self.right_artery.set_registration_matrix(right_transform_matrix)

    def volume_processing(self):
        current_input_flow = self.fl_confg.get_input_volume_dir()
        if not self.side_chooser == 1:
            vtu_left = vtkRdr.read_XMLUnstructuredGrid(self.fl_confg.get_vtu_left_pathName())
            self.left_artery.set_vtu_dataset(vtu_left.GetOutput())
            vtp_left = vtkRdr.read_XMLPolydata(self.fl_confg.get_vtp_left_pathName())
            self.left_artery.set_vtp_dataset(vtp_left.GetOutput())

        if not self.side_chooser == 0:
            vtu_right = vtkRdr.read_XMLUnstructuredGrid(self.fl_confg.get_vtu_right_pathName())
            self.right_artery.set_vtu_dataset(vtu_right.GetOutput())
            vtp_right = vtkRdr.read_XMLPolydata(self.fl_confg.get_vtp_right_pathName())
            self.right_artery.set_vtp_dataset(vtp_right.GetOutput())

        i = 0
        for vtk_file in self.flow_input_files:
            current_full_domain_path = os.path.join(current_input_flow, vtk_file)
            if not os.path.exists(self.fl_confg.get_carotid_arteries_volume_pathName(i)):
                carotid_arteries_grid, full_domain_output = vtkRdr.extract_volume_by_flow(current_full_domain_path)
                # carotid_arteries_grid = self.carotid_arteries_preProcessing(carotid_arteries_grid)

                # if i == 0:
                #     vtkplt.render_unstructuredGrid(carotid_arteries_grid, full_domain_output,
                #                                    "Carotid Arteries and Full domain")
                Writer.write_UnstructuredGrid(carotid_arteries_grid,
                                              self.fl_confg.get_carotid_arteries_volume_pathName(i))
                Writer.write_natural_scale_volume(self.fl_confg.get_carotid_arteries_volume_pathName(i))
            else:
                carotid_arteries_grid = vtkRdr.read_vtk_UnstructuredGrid(
                    self.fl_confg.get_carotid_arteries_volume_pathName(i))
                # Plot.render_DataSet(self.fl_confg.get_carotid_arteries_volume_pathName(i))

            registered_left_volume, registered_right_volume = self.split_arteries_volume(carotid_arteries_grid, i)
            self.cut_artery_volume(i, registered_left_volume, registered_right_volume)

            self.calculate_new_flow_rate(i)
            print("==================================")
            print(f"Process's completed for {i}th time")
            print("\n")

            i += 1

    def split_arteries_volume(self, carotid_arteries_grid, time_step):
        clip_origin = MathFun.calculate_centerpoint(carotid_arteries_grid)
        registered_left_volume = None
        registered_right_volume = None

        if not self.side_chooser == 1:
            left_normal = [0.0, 1.0, 0.0]
            left_plane_clipper = vtkUtl.create_divider_plane(clip_origin, left_normal)
            left_artery_volume = vtkUtl.get_divided_dataset(left_plane_clipper, carotid_arteries_grid)
            Writer.write_UnstructuredGrid(left_artery_volume,
                                          self.fl_confg.get_left_artery_volume_pathName(time_step))
            Writer.write_natural_scale_volume(self.fl_confg.get_left_artery_volume_pathName(time_step))

            registered_left_volume = vtkUtl.apply_transformation_to_volume(left_artery_volume,
                                                                           self.left_artery.get_combined_transform())

            Writer.write_UnstructuredGrid(registered_left_volume,
                                          self.fl_confg.get_left_aligned_artery_volume_pathName(time_step))
            Writer.write_natural_scale_volume(self.fl_confg.get_left_aligned_artery_volume_pathName(time_step))
            print("Left Registration Matrix: " + str(self.left_artery.get_combined_transform()))

        if not self.side_chooser == 0:
            right_normal = [0.0, -1.0, 0.0]
            right_plane_clipper = vtkUtl.create_divider_plane(clip_origin, right_normal)
            right_artery_volume = vtkUtl.get_divided_dataset(right_plane_clipper, carotid_arteries_grid)
            Writer.write_UnstructuredGrid(right_artery_volume,
                                          self.fl_confg.get_right_artery_volume_pathName(time_step))
            Writer.write_natural_scale_volume(self.fl_confg.get_right_artery_volume_pathName(time_step))

            registered_right_volume = vtkUtl.apply_transformation_to_volume(right_artery_volume,
                                                                            self.right_artery.get_combined_transform())

            Writer.write_UnstructuredGrid(registered_right_volume,
                                          self.fl_confg.get_right_aligned_artery_volume_pathName(time_step))
            Writer.write_natural_scale_volume(self.fl_confg.get_right_aligned_artery_volume_pathName(time_step))
            print("Right Registration Matrix: " + str(self.right_artery.get_combined_transform()))

        # Plot.render_unstructuredGrid(left_artery_volume, right_artery_volume, "Left and Right Flow")

        return registered_left_volume, registered_right_volume

    @classmethod
    def registration(cls, source_output, target, current_time_step_dir):
        surface_filter = vtkUtl.get_surface_from_volume(source_output)
        source_points = vtkCnvrt.vtk_to_numpy_points(surface_filter.GetOutput())
        # reflected_source_points = source_points
        # affine_reflection_matrix = None
        reflected_source_points, affine_reflection_matrix = MathFun.reflect_source_points(source_points)
        pre_registration_points, pre_registration_matrix = MathFun.do_the_rotation(source_points,
                                                                                   affine_reflection_matrix)
        pre_registration_data = vtkCnvrt.numpy_to_vtk_polydata(pre_registration_points, surface_filter.GetOutput())
        print("Rotation has done!")
        # Plot.rendering_three_dataset(target, surface_filter.GetOutput(), pre_registration_data,
        #                              "Pre-Registration Result: target_surface(yellow) - source("
        #                              "Red) - pre_registration_volume(blue)")
        icp_polydata, icp_matrix_np = vtkUtl.calculate_ICP_matrix_registration(target, pre_registration_data)
        combined_transform_matrix1 = np.dot(icp_matrix_np, pre_registration_matrix)
        transformed_polydata, center_matrix = vtkUtl.center_surface(icp_polydata, target)
        combined_transform_matrix2 = np.dot(center_matrix, combined_transform_matrix1)
        icp_polydata2, icp_matrix_np2 = vtkUtl.calculate_ICP_matrix_registration(target, transformed_polydata)
        # final_transform_matrix = np.dot(icp_matrix_np2, combined_transform_matrix2)
        combined_transform_matrix = np.dot(icp_matrix_np2, combined_transform_matrix2)
        # combined_transform_matrix = np.dot(icp_matrix_np, pre_registration_matrix)
        np.savetxt(current_time_step_dir + 'combined_transform.txt', combined_transform_matrix, fmt='%0.6f')
        registered_volume = vtkUtl.apply_transformation_to_volume(source_output, combined_transform_matrix)

        # first_surface_actor, second_surface_actor, third_surface_actor = \
        #     vtkplt.rendering_three_dataset(target, surface_filter.GetOutput(), registered_volume,
        #                                    "Registration Result: Target(yellow) - Source(red) - registered_volume(blue)")
        # registration_actors = [first_surface_actor, second_surface_actor, third_surface_actor]

        first_surface_actor, third_surface_actor = vtkplt.rendering_two_dataset(target, registered_volume,
                                                                                "Registration Result: Target(yellow) - Source(red) - registered_volume(blue)")
        registration_actors = [first_surface_actor, third_surface_actor]

        return combined_transform_matrix, registration_actors

    def cut_artery_volume(self, time_step, registered_left_volume, registered_right_volume):
        if not self.side_chooser == 1:
            left_dir = self.fl_confg.get_current_timestep_flow_left_dir(time_step)
            left_scaled_dir = self.fl_confg.get_natural_scale_dir(left_dir)
            self.left_pln_contnr.cut_volume(registered_left_volume, left_dir, left_scaled_dir,
                                            self.fl_confg.get_sphere_radius_coef(),
                                            self.fl_confg.get_natural_left_cut_planes_dir(), "flow_")
            self.left_pln_contnr.calculate_cca_flow_rate(registered_left_volume, left_dir, left_scaled_dir,
                                                         self.updated_sphere_coef,
                                                         self.left_artery.get_vtp_dataset())

            print(f"\nvtu_intersection left start {time_step}")
            self.left_pln_contnr.cut_volume(self.left_artery.get_vtu_dataset(), left_dir, left_scaled_dir,
                                            self.updated_sphere_coef,
                                            self.fl_confg.get_natural_left_cut_planes_dir(), "vtu_intersection_", 0.001)

        if not self.side_chooser == 0:
            right_dir = self.fl_confg.get_current_timestep_flow_right_dir(time_step)
            right_scaled_dir = self.fl_confg.get_natural_scale_dir(right_dir)

            self.right_pln_contnr.cut_volume(registered_right_volume, right_dir, right_scaled_dir,
                                             self.updated_sphere_coef,
                                             self.fl_confg.get_natural_right_cut_planes_dir(), "flow_")

            self.right_pln_contnr.calculate_cca_flow_rate(registered_right_volume, right_dir, right_scaled_dir,
                                                          self.fl_confg.get_sphere_radius_coef(),
                                                          self.right_artery.get_vtp_dataset())
            print(f"\nvtu_intersection right start {time_step} --------------------------\n")

            self.right_pln_contnr.cut_volume(self.right_artery.get_vtu_dataset(), right_dir, right_scaled_dir,
                                             self.updated_sphere_coef,
                                             self.fl_confg.get_natural_right_cut_planes_dir(), "vtu_intersection_",
                                             0.001)

    def calculate_new_flow_rate(self, time_step):
        last_time_parameter = float(self.fl_confg.project_config.get('Parameters', 'last_time'))
        if not self.side_chooser == 1:
            cca_constant_l, new_ica_l, new_eca_l = MathFun.filter_and_average_flow_rates(
                self.left_pln_contnr.get_flow_rate_dict())
            left_dir = self.fl_confg.get_current_timestep_flow_left_dir(time_step)
            left_scaled_dir = self.fl_confg.get_natural_scale_dir(left_dir)
            if time_step == 0:
                Writer.write_Points_file(left_scaled_dir + "flow_cca.vtk", self.fl_confg.get_cca_left_dir())

            cca_left_dir = self.fl_confg.get_cca_left_dir() + str(time_step * last_time_parameter)
            self.ica_left_dict[time_step] = -new_ica_l
            self.eca_left_dict[time_step] = -new_eca_l
            Writer.write_U_file(left_scaled_dir + "flow_cca.vtk", cca_left_dir, cca_constant_l)

        if not self.side_chooser == 0:
            cca_constant_r, new_ica_r, new_eca_r = MathFun.filter_and_average_flow_rates(
                self.right_pln_contnr.get_flow_rate_dict())
            right_dir = self.fl_confg.get_current_timestep_flow_right_dir(time_step)
            right_scaled_dir = self.fl_confg.get_natural_scale_dir(right_dir)
            if time_step == 0:
                Writer.write_Points_file(right_scaled_dir + "flow_cca.vtk", self.fl_confg.get_cca_right_dir())

            cca_right_dir = self.fl_confg.get_cca_right_dir() + str(time_step * last_time_parameter)
            self.ica_right_dict[time_step] = -new_ica_r
            self.eca_right_dict[time_step] = -new_eca_r
            Writer.write_U_file(right_scaled_dir + "flow_cca.vtk", cca_right_dir, cca_constant_r)

    def finalize(self):
        last_time_parameter = float(self.fl_confg.project_config.get('Parameters', 'last_time'))

        if not self.side_chooser == 1:
            last_time_dir_left = self.fl_confg.get_left_geometry_dir()
            last_time_dir_left = self.fl_confg.get_natural_scale_dir(last_time_dir_left)
            Writer.write_new_flow_rate(self.ica_left_dict, self.eca_left_dict, self.fl_confg.get_flow_rate_left_dir(),
                                       last_time_parameter, last_time_dir_left)
            self.fl_confg.copy_and_rename_folders(self.fl_confg.get_cca_left_dir(), last_time_parameter)

        if not self.side_chooser == 0:
            last_time_dir_right = self.fl_confg.get_right_geometry_dir()
            last_time_dir_right = self.fl_confg.get_natural_scale_dir(last_time_dir_right)
            Writer.write_new_flow_rate(self.ica_right_dict, self.eca_right_dict,
                                       self.fl_confg.get_flow_rate_right_dir(),
                                       last_time_parameter, last_time_dir_right)
            self.fl_confg.copy_and_rename_folders(self.fl_confg.get_cca_right_dir(), last_time_parameter)

    @classmethod
    def carotid_arteries_preProcessing(cls, arteries):
        reflection_y = np.diag([1, -1, 1])
        reflection_matrix = reflection_y
        affine_reflection_matrix = np.eye(4)
        affine_reflection_matrix[:3, :3] = reflection_matrix

        carotid_arteries = vtkUtl.apply_transformation_to_volume(arteries, affine_reflection_matrix)
        return carotid_arteries

    @classmethod
    def get_right_registration_actors(cls, actors):
        return actors

    @classmethod
    def get_left_registration_actors(cls, actors):
        return actors

