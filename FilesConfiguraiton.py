import os
import configparser
import shutil


# project_dir = os.path.dirname(os.path.abspath(__file__))


class FilesConfiguration:
    def __init__(self, case_code, side_chooser):
        self.project_config = None
        self.load_config()
        self.inputs_dir = None
        self.outputs_dir = None
        self.current_subject_code = case_code
        self.post_processing_dir = None
        self.side_chooser = side_chooser
        self.current_imaging_scale_dir = None
        self.current_imaging_scale_geometry_dir = None
        self.current_natural_scale_dir = None
        self.current_natural_scale_geometry_dir = None
        self.imaging_scale_flow_output_dir = None
        self.subject_input_dir = None
        self.subject_flow_input_dir = None
        self.set_inputs_outputs_dir()
        self.initiate_folder()
        # self.initiate_folders()

    def load_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        print(f"Reading config file from: {config_path}")
        config.read(config_path)
        self.project_config = config

    @classmethod
    def get_initial_dir(cls):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        return os.path.dirname(__file__) + '\\' + config.get('Paths', 'inputs_dir')

    def set_inputs_outputs_dir(self):
        self.outputs_dir = os.path.dirname(__file__) + '\\' + self.project_config.get('Paths', 'outputs_dir')
        self.inputs_dir = os.path.dirname(__file__) + '\\' + self.project_config.get('Paths', 'inputs_dir')

    def get_side_chooser(self):
        return self.side_chooser

    def initiate_folders(self):
        side_chooser = int(self.project_config.get('Parameters', 'side_chooser'))
        if not os.path.exists(self.outputs_dir):
            os.makedirs(self.outputs_dir)

        subjects_codes = []
        for subject_code in os.listdir(self.inputs_dir):
            subject_path = self.inputs_dir + subject_code + '\\'
            subjects_codes.append(subject_code)
            if os.path.isdir(subject_path):
                output_path = self.outputs_dir + subject_code + "\\imaging_scale"
                output_natural_path = self.outputs_dir + subject_code + "\\natural_scale"
                output_postp = self.outputs_dir + subject_code + "\\post_processing"
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                if not os.path.exists(output_natural_path):
                    os.makedirs(output_natural_path)
                if not os.path.exists(output_postp):
                    os.makedirs(output_postp)

                flow_output_dir = output_path + "\\flow"
                flow_output_natural_dir = output_natural_path + "\\flow"
                if not os.path.exists(flow_output_natural_dir):
                    os.makedirs(flow_output_natural_dir)
                if not os.path.exists(flow_output_dir):
                    os.makedirs(flow_output_dir)

                flow_time_step_dir = flow_output_dir + "\\time_steps"
                flow_time_step_natural_dir = flow_output_natural_dir + "\\time_steps"
                if not os.path.exists(flow_time_step_natural_dir):
                    os.makedirs(flow_time_step_natural_dir)
                if not os.path.exists(flow_time_step_dir):
                    os.makedirs(flow_time_step_dir)

                flow_flow_rate_dir = flow_output_natural_dir + "\\flow_rate"
                if not os.path.exists(flow_flow_rate_dir):
                    os.makedirs(flow_flow_rate_dir)
                flow_cca_dir = flow_output_natural_dir + "\\cca"
                if not os.path.exists(flow_cca_dir):
                    os.makedirs(flow_cca_dir)
                geometry_path = output_path + "\\geometry"
                if not os.path.exists(geometry_path):
                    os.makedirs(geometry_path)
                left_path = geometry_path + "\\left"
                right_path = geometry_path + "\\right"
                if not os.path.exists(left_path) and not side_chooser == 1:
                    os.makedirs(left_path)
                if not os.path.exists(right_path) and not side_chooser == 0:
                    os.makedirs(right_path)

                vtu_path = subject_path + 'vtu\\'
                if not os.path.exists(vtu_path):
                    os.makedirs(vtu_path)
                left_vtu = vtu_path + "left\\"
                right_vtu = vtu_path + "right\\"
                if not os.path.exists(left_vtu) and not side_chooser == 1:
                    os.makedirs(left_vtu)
                if not os.path.exists(right_vtu) and not side_chooser == 0:
                    os.makedirs(right_vtu)

        current_code_number = int(self.project_config.get('Parameters', 'current_code_number'))
        self.current_subject_code = subjects_codes[current_code_number]
        self.subject_input_dir = self.inputs_dir + str(self.current_subject_code) + '\\'
        print("Current Subject Code: " + str(self.current_subject_code))
        self.current_imaging_scale_dir = self.outputs_dir + self.current_subject_code + "\\imaging_scale\\"
        self.current_imaging_scale_geometry_dir = self.current_imaging_scale_dir + "geometry\\"
        self.current_natural_scale_dir = self.outputs_dir + self.current_subject_code + "\\natural_scale\\"
        self.current_natural_scale_geometry_dir = self.current_natural_scale_dir + "geometry\\"
        self.imaging_scale_flow_output_dir = self.current_imaging_scale_dir + "flow\\"
        self.subject_flow_input_dir = self.subject_input_dir + 'flow\\'
        self.post_processing_dir = self.outputs_dir + self.current_subject_code + "\\post_processing\\"

        subjects_codes.clear()

    def initiate_folder(self):
        if not os.path.exists(self.outputs_dir):
            os.makedirs(self.outputs_dir)

        subject_path = self.inputs_dir + self.current_subject_code + '\\'
        if os.path.isdir(subject_path):
            output_path = self.outputs_dir + self.current_subject_code + "\\imaging_scale"
            output_natural_path = self.outputs_dir + self.current_subject_code + "\\natural_scale"
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            if not os.path.exists(output_natural_path):
                os.makedirs(output_natural_path)
            flow_output_dir = output_path + "\\flow"
            flow_output_natural_dir = output_natural_path + "\\flow"
            if not os.path.exists(flow_output_natural_dir):
                os.makedirs(flow_output_natural_dir)
            if not os.path.exists(flow_output_dir):
                os.makedirs(flow_output_dir)
            flow_time_step_dir = flow_output_dir + "\\time_steps"
            flow_time_step_natural_dir = flow_output_natural_dir + "\\time_steps"
            if not os.path.exists(flow_time_step_natural_dir):
                os.makedirs(flow_time_step_natural_dir)
            if not os.path.exists(flow_time_step_dir):
                os.makedirs(flow_time_step_dir)
            flow_flow_rate_dir = flow_output_natural_dir + "\\flow_rate"
            if not os.path.exists(flow_flow_rate_dir):
                os.makedirs(flow_flow_rate_dir)
            flow_cca_dir = flow_output_natural_dir + "\\cca"
            if not os.path.exists(flow_cca_dir):
                os.makedirs(flow_cca_dir)
            geometry_path = output_path + "\\geometry"
            if not os.path.exists(geometry_path):
                os.makedirs(geometry_path)
            left_path = geometry_path + "\\left"
            right_path = geometry_path + "\\right"
            if not os.path.exists(left_path) and not self.side_chooser == 1:
                os.makedirs(left_path)
            if not os.path.exists(right_path) and not self.side_chooser == 0:
                os.makedirs(right_path)
            vtu_path = subject_path + 'vtu\\'
            if not os.path.exists(vtu_path):
                os.makedirs(vtu_path)
            left_vtu = vtu_path + "left\\"
            right_vtu = vtu_path + "right\\"
            if not os.path.exists(left_vtu) and not self.side_chooser == 1:
                os.makedirs(left_vtu)
            if not os.path.exists(right_vtu) and not self.side_chooser == 0:
                os.makedirs(right_vtu)

        current_code_number = int(self.project_config.get('Parameters', 'current_code_number'))
        # self.current_subject_code = subjects_codes[current_code_number]
        self.subject_input_dir = self.inputs_dir + str(self.current_subject_code) + '\\'
        print("Current Subject Code: " + str(self.current_subject_code))
        self.current_imaging_scale_dir = self.outputs_dir + self.current_subject_code + "\\imaging_scale\\"
        self.current_imaging_scale_geometry_dir = self.current_imaging_scale_dir + "geometry\\"
        self.current_natural_scale_dir = self.outputs_dir + self.current_subject_code + "\\natural_scale\\"
        self.current_natural_scale_geometry_dir = self.current_natural_scale_dir + "geometry\\"
        self.imaging_scale_flow_output_dir = self.current_imaging_scale_dir + "flow\\"
        self.subject_flow_input_dir = self.subject_input_dir + 'flow\\'

    def get_input_dir(self):
        return self.inputs_dir

    def get_outputs_dir(self):
        return self.outputs_dir

    def get_left_artery_surface_input_pathName(self):
        return self.subject_input_dir + self.project_config.get('Names', 'left_surface')

    def get_right_artery_surface_input_pathName(self):
        return self.subject_input_dir + self.project_config.get('Names', 'right_surface')

    def get_NIFTI_pathName(self):
        current_input_path = self.inputs_dir + self.current_subject_code + "\\"
        NIFTI_path = current_input_path + self.current_subject_code + ".nii"
        return NIFTI_path

    def get_original_geometry_namepath(self):
        original_geometry_stl_path = self.current_imaging_scale_geometry_dir + \
                                     self.project_config.get('Names', 'original_geometry_stl')
        return original_geometry_stl_path

    def get_smooth_original_geometry_namepath(self):
        current_smoothed_geometry_pathName = self.current_imaging_scale_geometry_dir + \
                                             self.project_config.get('Names', 'smooth_geometry_stl')
        return current_smoothed_geometry_pathName

    def get_smooth_original_geometry_namepath_input(self):
        current_smoothed_geometry_pathName = self.subject_input_dir + \
                                             self.project_config.get('Names', 'smooth_geometry_stl')
        return current_smoothed_geometry_pathName

    def get_left_artery_surface_path(self):
        left_artery_surface_path = self.current_imaging_scale_geometry_dir  # + "left\\"
        left_artery_surface_pathName = left_artery_surface_path + self.project_config.get('Names', 'left_surface')
        return left_artery_surface_pathName

    def get_right_artery_surface_path(self):
        right_artery_surface_path = self.current_imaging_scale_geometry_dir  # + "right\\"
        right_artery_surface_pathName = right_artery_surface_path + self.project_config.get('Names', 'right_surface')
        return right_artery_surface_pathName

    def get_clipped_left_artery_surface_path(self):
        clipped_left_artery_surface_path = self.current_imaging_scale_geometry_dir + "left\\"
        clipped_left_artery_surface_pathName = clipped_left_artery_surface_path + \
                                               self.project_config.get('Names', 'clipped_surface_left')

        return clipped_left_artery_surface_pathName

    def get_clipped_right_artery_surface_path(self):
        clipped_right_artery_surface_path = self.current_imaging_scale_geometry_dir + "right\\"
        clipped_left_artery_surface_pathName = clipped_right_artery_surface_path + \
                                               self.project_config.get('Names', 'clipped_surface_right')

        return clipped_left_artery_surface_pathName

    def get_left_centerline_pathName(self):
        left_geometry_path = self.current_imaging_scale_geometry_dir + "left\\"
        left_centerline_pathName = left_geometry_path + str(self.current_subject_code) + "_left.vtk"
        return left_centerline_pathName

    def get_right_centerline_pathName(self):
        right_geometry_path = self.current_imaging_scale_geometry_dir + "right\\"
        right_centerline_pathName = right_geometry_path + str(self.current_subject_code) + "_right.vtk"
        return right_centerline_pathName

    def get_left_clipper_planes_dir(self):
        left_clipper_planes_dir = self.current_imaging_scale_dir + "Planes\\" + "left\\"
        if not os.path.exists(left_clipper_planes_dir):
            os.makedirs(left_clipper_planes_dir)
        return left_clipper_planes_dir

    def get_right_clipper_planes_dir(self):
        right_clipper_planes_dir = self.current_imaging_scale_dir + "Planes\\" + "right\\"
        if not os.path.exists(right_clipper_planes_dir):
            os.makedirs(right_clipper_planes_dir)
        return right_clipper_planes_dir

    def get_left_cut_planes_dir(self):
        left_cut_planes_dir = self.current_imaging_scale_dir + "Planes\\" + "left\\"
        if not os.path.exists(left_cut_planes_dir):
            os.makedirs(left_cut_planes_dir)
        return left_cut_planes_dir

    def get_natural_left_cut_planes_dir(self):
        left_cut_planes_dir = self.current_natural_scale_dir + "Planes\\" + "left\\"
        return left_cut_planes_dir

    def get_natural_right_cut_planes_dir(self):
        right_cut_planes_dir = self.current_natural_scale_dir + "Planes\\" + "right\\"
        return right_cut_planes_dir

    def get_right_cut_planes_dir(self):
        right_cut_planes_dir = self.current_imaging_scale_dir + "Planes\\" + "right\\"
        if not os.path.exists(right_cut_planes_dir):
            os.makedirs(right_cut_planes_dir)
        return right_cut_planes_dir

    def get_right_geometry_dir(self):
        return self.current_imaging_scale_geometry_dir + "right\\"

    def get_left_geometry_dir(self):
        return self.current_imaging_scale_geometry_dir + "left\\"

    def get_left_clipped_surface_pathName(self):
        return self.current_imaging_scale_geometry_dir + "left\\" + \
               self.project_config.get('Names', 'clipped_surface_left')

    def get_right_clipped_surface_pathName(self):
        return self.current_imaging_scale_geometry_dir + "right\\" + \
               self.project_config.get('Names', 'clipped_surface_right')

    def get_variation_rate(self):
        return float(self.project_config.get('Parameters', 'variation_rate'))

    def get_imaging_scale_flow_output_dir(self):
        return self.imaging_scale_flow_output_dir

    def get_input_volume_dir(self):
        return self.subject_flow_input_dir

    def get_current_timestep_flow_left_dir(self, counter):
        str_counter = str(counter)
        left_time_step_dir = self.imaging_scale_flow_output_dir + 'time_steps\\' + str_counter + '\\left\\'
        if not os.path.exists(left_time_step_dir):
            os.makedirs(left_time_step_dir)
        return left_time_step_dir

    def get_current_timestep_flow_right_dir(self, counter):
        str_counter = str(counter)
        right_time_step_dir = self.imaging_scale_flow_output_dir + 'time_steps\\' + str_counter + '\\right\\'
        if not os.path.exists(right_time_step_dir):
            os.makedirs(right_time_step_dir)
        return right_time_step_dir

    def get_current_full_domain_pathName(self):
        pass

    def get_carotid_arteries_volume_pathName(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\"
        if not os.path.exists(path):
            os.makedirs(path)

        pathName = path + self.project_config.get('Names', 'carotid_arteries')
        return pathName

    def get_left_artery_volume_pathName(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "left\\"
        if not os.path.exists(path):
            os.makedirs(path)

        pathName = path + self.project_config.get('Names', 'flow_artery')
        return pathName

    def get_right_artery_volume_pathName(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "right\\"
        if not os.path.exists(path):
            os.makedirs(path)

        pathName = path + self.project_config.get('Names', 'flow_artery')
        return pathName

    def get_left_aligned_artery_volume_pathName(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "left\\"
        if not os.path.exists(path):
            os.makedirs(path)

        pathName = path + self.project_config.get('Names', 'registration_result')
        return pathName

    def get_right_aligned_artery_volume_pathName(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "right\\"
        if not os.path.exists(path):
            os.makedirs(path)

        pathName = path + self.project_config.get('Names', 'registration_result')
        return pathName

    def get_right_volume_time_step_dir(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "right\\"
        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_left_volume_time_step_dir(self, counter):
        path = self.imaging_scale_flow_output_dir + 'time_steps\\' + str(counter) + "\\" + "left\\"
        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def get_plane_size(self):
        return float(self.project_config.get('Parameters', 'pyvista_plane_size_1'))

    def get_sphere_radius_coef(self):
        return float(self.project_config.get('Parameters', 'sphere_radius_coef'))

    def get_combined_left_namePath(self):
        return self.current_imaging_scale_geometry_dir + "left\\" + \
               self.project_config.get('Names', 'combined')

    def get_combined_right_namePath(self):
        return self.current_imaging_scale_geometry_dir + "right\\" + \
               self.project_config.get('Names', 'combined')

    def get_vtu_left_pathName(self):
        path = self.subject_input_dir + 'vtu\\'
        left_path = path + 'left\\'
        return left_path + self.project_config.get('Names', 'vtu_file')

    def get_vtu_right_pathName(self):
        path = self.subject_input_dir + 'vtu\\'
        right_path = path + 'right\\'
        return right_path + self.project_config.get('Names', 'vtu_file')

    def get_vtp_left_pathName(self):
        path = self.subject_input_dir + 'vtu\\'
        left_path = path + 'left\\'
        return left_path + self.project_config.get('Names', 'vtp_cca')

    def get_vtp_right_pathName(self):
        path = self.subject_input_dir + 'vtu\\'
        right_path = path + 'right\\'
        return right_path + self.project_config.get('Names', 'vtp_cca')

    def get_flow_rate_left_dir(self):
        path = self.current_natural_scale_dir + "flow\\flow_rate\\left\\"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_flow_rate_right_dir(self):
        path = self.current_natural_scale_dir + "flow\\flow_rate\\right\\"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_cca_left_dir(self):
        path = self.current_natural_scale_dir + "\\flow\\cca\\left\\"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_cca_right_dir(self):
        path = self.current_natural_scale_dir + "\\flow\\cca\\right\\"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @classmethod
    def get_natural_scale_dir(cls, imaging_scale_dir):
        parts = imaging_scale_dir.split('\\')
        parts = ['natural_scale' if part == 'imaging_scale' else part for part in parts]
        natural_scale_dir = '\\'.join(parts)
        return natural_scale_dir

    def copy_and_rename_folders(self, file_dir, coefficient, repeat_count=2):
        folders = sorted(self.get_folders(file_dir))  # Sort the folder names numerically
        num_folders = len(folders)
        for i in range(num_folders * repeat_count):
            original_folder_index = i % num_folders
            original_folder_name = folders[original_folder_index]
            new_folder_name = f'{coefficient * (num_folders + i):.3f}'  # Increment index for naming
            source_folder = os.path.join(file_dir, original_folder_name)
            dest_folder = os.path.join(file_dir, new_folder_name)

            # Check if the destination folder already exists to avoid overwriting
            if not os.path.exists(dest_folder):
                # Copy the folder and its contents
                shutil.copytree(source_folder, dest_folder)

    @classmethod
    def get_icon_pathName(cls):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        return os.path.dirname(__file__) + '\\' + config.get('Paths', 'icon')

    @classmethod
    def get_folders(cls, directory):
        return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

    def get_input_vtu_dir(self):
        return self.subject_input_dir + 'vtu\\'

    def get_cutplane_size_coef(self):
        return float(self.project_config.get('Parameters', 'cutplane_size_coef'))

    def check_vtu_exists(self):
        left_vtu = self.get_vtu_left_pathName()
        right_vtu = self.get_vtu_right_pathName()
        if os.path.exists(left_vtu) or os.path.exists(right_vtu):
            return True
        else:
            return False

    @classmethod
    def get_pic_pathName(cls):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        return os.path.dirname(__file__) + '\\' + config.get('Names', 'pic')

    def get_left_remeshed_surface_path(self):
        postPro_dir = self.post_processing_dir + "split_branch\\" + "left\\"
        if not os.path.exists(postPro_dir):
            os.makedirs(postPro_dir)
        remeshed_surface_pathName = postPro_dir + self.project_config.get('Names', 'remeshed_surface')

        return remeshed_surface_pathName

    def get_right_remeshed_surface_path(self):
        postPro_dir = self.post_processing_dir + "split_branch\\" + "right\\"
        if not os.path.exists(postPro_dir):
            os.makedirs(postPro_dir)
        remeshed_surface_pathName = postPro_dir + self.project_config.get('Names', 'remeshed_surface')

        return remeshed_surface_pathName

    def get_left_branch_split_dir(self):
        postPro_dir = self.post_processing_dir + "split_branch\\" + "left\\"
        if not os.path.exists(postPro_dir):
            os.makedirs(postPro_dir)
        return postPro_dir

    def get_right_branch_split_dir(self):
        postPro_dir = self.post_processing_dir + "split_branch\\" + "right\\"
        if not os.path.exists(postPro_dir):
            os.makedirs(postPro_dir)
        return postPro_dir
