import numpy as np
from scipy.spatial.transform import Rotation
import pyvista as pv
import pandas as pd
from collections import defaultdict
from scipy.spatial import KDTree
import re


class MathematicalFunction:
    @classmethod
    def taubin_smooth_and_reflect_stl(cls, input_stl, output_stl, iterations=500, pass_band=0.05):
        # Reads an STL file, reflects it across the x and y axes, applies Taubin smoothing, and saves the smoothed STL.
        #
        # Parameters:
        # - input_stl (str): Path to the input STL file.
        # - output_stl (str): Path to save the smoothed STL file.
        # - iterations (int): Number of smoothing iterations.
        # - pass_band (float): Controls the smoothing effect (lower values give stronger smoothing).
        # """
        mesh = pv.read(input_stl)

        # Reflect across x-axis
        mesh.points[:, 0] *= -1

        # Reflect across y-axis
        mesh.points[:, 1] *= -1

        # Apply Taubin smoothing
        smoothed_mesh = mesh.smooth_taubin(n_iter=iterations, pass_band=pass_band)

        # Save the smoothed STL file
        smoothed_mesh.save(output_stl)
        print(f"Smoothed and reflected STL saved to: {output_stl}")

    @classmethod
    def filter_and_average_flow_rates(cls, flow_rates):
        cca_flow_rates_list = []
        eca_flow_rates_list = []
        ica_flow_rates_list = []
        for k in flow_rates:
            if k.startswith("c"):
                if k == "cca":
                    continue
                cca_flow_rates_list.append(flow_rates[k])
            elif k.startswith("e"):
                eca_flow_rates_list.append(flow_rates[k])
            elif k.startswith("i"):
                ica_flow_rates_list.append(flow_rates[k])

        cca_sorted_rates = sorted(cca_flow_rates_list)
        eca_sorted_rates = sorted(eca_flow_rates_list)
        ica_sorted_rates = sorted(ica_flow_rates_list)

        cca_avg_flow_rate = cls.calculate_average_flowrate(cca_sorted_rates)
        ica_avg_flow_rate = cls.calculate_average_flowrate(ica_sorted_rates)
        eca_avg_flow_rate = cls.calculate_average_flowrate(eca_sorted_rates)

        print("cca_avg: " + str(cca_avg_flow_rate))
        print("ica_avg: " + str(ica_avg_flow_rate))
        print("eca_avg: " + str(eca_avg_flow_rate))

        branch_constant = ica_avg_flow_rate / eca_avg_flow_rate
        cca_constant = cca_avg_flow_rate / flow_rates["cca"]
        print("cca_constant_left: " + str(cca_constant))

        new_ica = cca_avg_flow_rate / (1 + 1 / branch_constant)
        new_eca = new_ica / branch_constant

        return cca_constant, new_ica, new_eca

    @classmethod
    def calculate_average_flowrate(cls, sorted_list):
        selected_rates = [sorted_list[-1]]
        max_value = sorted_list[-1]

        # Step 3: Compare subsequent values with max_value
        for i in range(len(sorted_list) - 2, -1, -1):  # Iterate from second highest to lowest
            if abs(max_value - sorted_list[i]) / max_value <= 0.10:
                selected_rates.append(sorted_list[i])
            else:
                break  # Stop if the difference exceeds 10%

        # Step 4: Compute the average of selected values
        avg_flow_rate = sum(selected_rates) / len(selected_rates)

        return avg_flow_rate

    @classmethod
    def do_the_rotation(cls, reflected_source_points, affine_reflection_matrix=None):
        Ry = np.array([[0, 0, 1],
                       [0, 1, 0],
                       [-1, 0, 0]])
        Rz = np.array([[0, -1, 0],
                       [1, 0, 0],
                       [0, 0, 1]])
        R0 = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])

        combined_rotation_matrix = Rz @ Ry
        # rotation = Rotation.from_matrix(R0)
        rotation = Rotation.from_matrix(combined_rotation_matrix)

        rotated_points = rotation.apply(reflected_source_points)

        pre_registration_matrix = np.eye(4)
        pre_registration_matrix[:3, :3] = rotation.as_matrix()  # Insert the rotation matrix
        if affine_reflection_matrix is not None:
            pre_registration_matrix = np.dot(pre_registration_matrix, affine_reflection_matrix)

        return rotated_points, pre_registration_matrix

    @classmethod
    def reflect_source_points(cls, source_points, matrix=None):
        # source_points = VTK.vtk_to_numpy_points(surface_filter_output)
        reflection_x = np.diag([-1, 1, 1])  # Reflect across the X plane
        reflection_y = np.diag([1, -1, 1])  # Reflect across the Y plane
        # reflection_z = np.diag([1, 1, -1])

        no_reflection = np.eye(3)  # 3x3 identity matrix

        reflection_matrix = no_reflection

        affine_reflection_matrix = np.eye(4)
        affine_reflection_matrix[:3, :3] = reflection_matrix

        source_points_homogeneous = np.hstack([source_points, np.ones((source_points.shape[0], 1))])
        reflected_source_points = (affine_reflection_matrix @ source_points_homogeneous.T).T[:, :3]

        centroid_original = np.mean(source_points, axis=0)
        centroid_reflected = np.mean(reflected_source_points, axis=0)
        translation_vector = centroid_original - centroid_reflected

        affine_reflection_matrix[:3, 3] = translation_vector
        if matrix is not None:
            affine_reflection_matrix = np.dot(affine_reflection_matrix, matrix)

        # source_points_homogeneous = np.hstack([source_points, np.ones((source_points.shape[0], 1))])
        # reflected_source_points = (affine_reflection_matrix @ source_points_homogeneous.T).T[:, :3]

        # reflected_poly_data = VTK.numpy_to_vtk_polydata(reflected_source_points, surface_filter_output)
        # writer1 = vtk.vtkPolyDataWriter()
        # writer1.SetFileName("reflected_surface.vtk")
        # writer1.SetInputData(reflected_poly_data)
        # writer1.Write()
        # writer2 = vtk.vtkPolyDataWriter()
        # writer2.SetFileName("source_surface.vtk")
        # writer2.SetInputData(surface_filter_output)
        # writer2.Write()

        # Plot.rendering_two_polydata(surface_filter_output, reflected_poly_data,
        #                             "source_surface(Red) - reflected_poly_data(Blue)")  # red - blue

        return reflected_source_points, affine_reflection_matrix

    @classmethod
    def calculate_centerpoint(cls, unstructuredGrid):
        bounds = unstructuredGrid.GetBounds()

        centerX = (bounds[0] + bounds[1]) / 2.0
        centerY = (bounds[2] + bounds[3]) / 2.0
        centerZ = (bounds[4] + bounds[5]) / 2.0

        center_point = (centerX, centerY, centerZ)

        return center_point

    @classmethod
    def extract_number(cls, filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    @classmethod
    def remesh_stl(cls, input_file, output_file, subdivisions=2, hole_size_threshold=1000, smoothing_iterations=30):
        # Read the original STL file using pyvista
        mesh = pv.read(input_file)

        # Step 1: Fill holes with a specified maximum size threshold
        repaired_mesh = mesh.fill_holes(hole_size_threshold)  # Fill holes with the defined threshold
        cleaned_mesh = repaired_mesh.clean()  # Clean the mesh to remove any artifacts

        # Step 2: Smooth the cleaned mesh after hole filling
        smoothed_filled_region = cleaned_mesh.smooth(n_iter=smoothing_iterations, relaxation_factor=0.1)

        # Step 3: Subdivide the smoothed mesh to refine the number of points (vertices)
        refined_mesh = smoothed_filled_region.subdivide(subdivisions)

        # Step 4: Save the refined mesh to a new STL file
        refined_mesh.save(output_file)
        print(f"Remeshed STL saved as {output_file}")

    @classmethod
    def load_stl_points_and_boundary(cls, file_path):
        mesh_data = mesh.Mesh.from_file(file_path)
        points = np.vstack((mesh_data.v0, mesh_data.v1, mesh_data.v2))
        points = np.unique(points, axis=0)

        # Identify boundary edges (edges belonging to only one triangle)
        edges = defaultdict(int)
        for i in range(len(mesh_data.vectors)):
            triangle = [mesh_data.v0[i], mesh_data.v1[i], mesh_data.v2[i]]
            for j in range(3):
                edge = tuple(sorted([tuple(triangle[j]), tuple(triangle[(j + 1) % 3])]))
                edges[edge] += 1

        boundary_edges = [edge for edge, count in edges.items() if count == 1]
        boundary_points = np.unique([point for edge in boundary_edges for point in edge], axis=0)

        return points, boundary_points

    @classmethod
    def find_intersection_points(cls, boundary_points1, boundary_points2, threshold=1e-3):
        tree = KDTree(boundary_points2)
        distances, indices = tree.query(boundary_points1)
        intersection_mask = distances < threshold
        intersection_points = boundary_points1[intersection_mask]
        return intersection_points

    @classmethod
    def save_points_to_csv(cls, points, output_file):
        df = pd.DataFrame(points, columns=['X', 'Y', 'Z'])
        df.to_csv(output_file, index=False)
        print(f"Intersection points saved to {output_file}")

    @classmethod
    def reciprocal_closest_point(cls, df1, df2):
        matches = []
        for i, point_A in df1.iterrows():
            point_A_coords = [point_A['X'], point_A['Y'], point_A['Z']]
            distances_B = df2.apply(
                lambda point_B: cls.distance(point_A_coords, [point_B['X'], point_B['Y'], point_B['Z']]), axis=1)
            idx_B = distances_B.idxmin()
            point_B_coords = [df2.loc[idx_B, 'X'], df2.loc[idx_B, 'Y'], df2.loc[idx_B, 'Z']]

            distances_A_check = df1.apply(lambda point_A_check: cls.distance(point_B_coords,
                                                                             [point_A_check['X'], point_A_check['Y'],
                                                                              point_A_check['Z']]), axis=1)
            idx_A_check = distances_A_check.idxmin()

            if idx_A_check == i:
                matches.append((i, idx_B))

        return matches

    @classmethod
    def distance(cls, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    @classmethod
    def update_or_use_existing_values(cls, df_source, idx_source, df_target, idx_target):
        if np.all(df_target.loc[idx_target, ['X_NEW', 'Y_NEW', 'Z_NEW']] != 0):
            df_source.loc[idx_source, ['X_NEW', 'Y_NEW', 'Z_NEW']] = df_target.loc[
                idx_target, ['X_NEW', 'Y_NEW', 'Z_NEW']]
        else:
            point_source = df_source.loc[idx_source, ['X', 'Y', 'Z']].values
            point_target = df_target.loc[idx_target, ['X', 'Y', 'Z']].values
            D = cls.interpolate(point_source, point_target)
            df_source.loc[idx_source, ['X_NEW', 'Y_NEW', 'Z_NEW']] = D
            df_target.loc[idx_target, ['X_NEW', 'Y_NEW', 'Z_NEW']] = D

    @classmethod
    def update_remaining_points(cls, df):
        for i, point in df.iterrows():
            if point['X_NEW'] == 0 and point['Y_NEW'] == 0 and point['Z_NEW'] == 0:
                point_coords = [point['X'], point['Y'], point['Z']]
                non_zero_points = df[(df['X_NEW'] != 0) & (df['Y_NEW'] != 0) & (df['Z_NEW'] != 0)]
                if not non_zero_points.empty:
                    distances = non_zero_points.apply(lambda non_zero_point: cls.distance(point_coords,
                                                                                          [non_zero_point['X'],
                                                                                           non_zero_point['Y'],
                                                                                           non_zero_point['Z']]),
                                                      axis=1)
                    nearest_idx = distances.idxmin()
                    nearest_coords = non_zero_points.loc[nearest_idx, ['X_NEW', 'Y_NEW', 'Z_NEW']].values
                    df.loc[i, ['X_NEW', 'Y_NEW', 'Z_NEW']] = nearest_coords

    @classmethod
    def interpolate(cls, p1, p2):
        return (np.array(p1) + np.array(p2)) / 2
