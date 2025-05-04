import math
from collections import OrderedDict
from VTKModule.VTKUtils import VTKUtils as VTK
import numpy as np
from Core.Point import Point


class Centerline:
    def __init__(self, smooth_centerline_polydata):
        self.centerline_polydata = smooth_centerline_polydata
        self.point_coords = None
        self.connectivity = None
        self.bf_point = None
        self.end_points = dict()
        self.clipper_points = dict()
        self.clipper_vector = dict()
        self.cut_points = OrderedDict()
        self.cut_vectors = OrderedDict()
        self.centerline_points_list = []
        self.labeled_line = OrderedDict()

    def analyzing_centerline(self):
        point_coords, connectivity = VTK.get_coords_and_connectivity(self.centerline_polydata)
        self.point_coords = point_coords
        self.connectivity = connectivity
        bf_pt_id, bifurcation_coords = self.find_bifurcation_point(point_coords, connectivity)
        self.find_endpoints(bf_pt_id, point_coords, connectivity)

    def find_bifurcation_point(self, point_coords, connectivity):
        # Identify the bifurcation point (the point that is common in 3 lines)
        point_usage = {}
        for line in connectivity:
            for pt_id in line:
                if pt_id in point_usage:
                    point_usage[pt_id] += 1
                else:
                    point_usage[pt_id] = 1

        # The bifurcation point should be the one used in exactly 3 lines
        bifurcation_pt_id = [pt_id for pt_id, count in point_usage.items() if count == 3]
        bifurcation_coords = point_coords[bifurcation_pt_id[0]] if bifurcation_pt_id else None

        # Verbose output for debugging
        print(f"Bifurcation point coordinates: {bifurcation_coords} (ID: {bifurcation_pt_id[0]})")
        point_id = self.centerline_polydata.FindPoint(bifurcation_coords)
        # print(str(point_id))
        self.bf_point = Point(point_id, bifurcation_coords[0], bifurcation_coords[1], bifurcation_coords[2])
        self.bf_point.set_radius(VTK.get_radius_for_coord(self.centerline_polydata, bifurcation_coords))
        return bifurcation_pt_id, bifurcation_coords

    def find_endpoints(self, bifurcation_pt_id, point_coords, connectivity):
        true_end_points = []
        for line in connectivity:
            endpoints = [line[0], line[-1]]  # First and last points in the line
            for pt_id in endpoints:
                if pt_id not in bifurcation_pt_id:
                    true_end_points.append(pt_id)

        # Ensure we have exactly 3 unique true endpoints
        true_end_points = list(set(true_end_points))

        if len(true_end_points) != 3:
            raise ValueError("Error: Expected exactly 3 true end points, found {}".format(len(true_end_points)))

        # Get the coordinates of the true end points
        true_end_points_coords = point_coords[true_end_points]

        # Label the CCA branch (the line with the lowest Z value)
        cca_idx = np.argmin([point_coords[pt][2] for pt in true_end_points])  # Z is the third component
        cca_pt = true_end_points[cca_idx]

        # Remove the CCA point from the remaining points for ICA and ECA labeling
        remaining_pts = [pt for pt in true_end_points if pt != cca_pt]

        # Label the ICA (line with lower Y value) and ECA (the other remaining line)
        ica_pt = remaining_pts[0] if point_coords[remaining_pts[0]][1] < point_coords[remaining_pts[1]][1] else \
            remaining_pts[1]
        eca_pt = remaining_pts[1] if ica_pt == remaining_pts[0] else remaining_pts[0]

        print(f"CCA endpoint coordinates: {point_coords[cca_pt]} (ID: {cca_pt})\n")
        cca_pt_id = self.centerline_polydata.FindPoint(point_coords[cca_pt])
        print(str(cca_pt_id))
        print(f"ICA endpoint coordinates: {point_coords[ica_pt]} (ID: {ica_pt})")
        ica_pt_id = self.centerline_polydata.FindPoint(point_coords[ica_pt])
        print(str(ica_pt_id))
        print(f"ECA endpoint coordinates: {point_coords[eca_pt]} (ID: {eca_pt})")

        self.end_points["cca"] = Point(cca_pt, point_coords[cca_pt][0], point_coords[cca_pt][1],
                                       point_coords[cca_pt][2])
        self.end_points["eca"] = Point(eca_pt, point_coords[eca_pt][0], point_coords[eca_pt][1],
                                       point_coords[eca_pt][2])
        self.end_points["ica"] = Point(ica_pt, point_coords[ica_pt][0], point_coords[ica_pt][1],
                                       point_coords[ica_pt][2])

        self.end_points["cca"].set_radius(VTK.get_radius_for_coord(self.centerline_polydata, point_coords[cca_pt]))
        self.end_points["eca"].set_radius(VTK.get_radius_for_coord(self.centerline_polydata, point_coords[eca_pt]))
        self.end_points["ica"].set_radius(VTK.get_radius_for_coord(self.centerline_polydata, point_coords[ica_pt]))

    def find_clipper_points_and_vectors(self, variation_rate):
        for k in self.end_points:
            endpoint_id = int(self.end_points[k].get_id())
            radius = self.end_points[k].get_radius()
            if endpoint_id == 0 or endpoint_id == 1:
                for j in range(endpoint_id + 1, self.centerline_polydata.GetNumberOfPoints()):
                    current_radius = VTK.get_radius_by_point_id(self.centerline_polydata, j)
                    if (1 + variation_rate) * radius > current_radius > (1 - variation_rate) * radius:
                        point_coords = self.centerline_polydata.GetPoint(j)
                        self.clipper_points[k] = Point(j, point_coords[0], point_coords[1], point_coords[2])
                        self.clipper_points[k].set_radius(current_radius)
                        break
            else:
                current_id = int(endpoint_id - 5)
                while True:
                    current_radius = VTK.get_radius_by_point_id(self.centerline_polydata,
                                                                current_id)  # centerline_points[current_id + 3][4]
                    previous_radius = VTK.get_radius_by_point_id(self.centerline_polydata, int(current_id - 1))
                    if current_radius * (1 + variation_rate) > previous_radius > current_radius * (1 - variation_rate):
                        point_coords = self.centerline_polydata.GetPoint(current_id - 1)
                        self.clipper_points[k] = Point(int(current_id - 1), point_coords[0], point_coords[1],
                                                       point_coords[2])
                        self.clipper_points[k].set_radius(VTK.get_radius_by_point_id(self.centerline_polydata,
                                                                                     int(current_id - 1)))
                        # ---------------------- Vector-------------------------------------
                        destination_coord = self.centerline_polydata.GetPoint(current_id)
                        origin_coord = self.centerline_polydata.GetPoint(int(current_id - 1))
                        x_normalize = destination_coord[0] - origin_coord[0]
                        y_normalize = destination_coord[1] - origin_coord[1]
                        z_normalize = destination_coord[2] - origin_coord[2]
                        normalize_vector_item = [x_normalize, y_normalize, z_normalize]
                        self.clipper_vector[k] = normalize_vector_item
                        break
                    else:
                        current_id = current_id - 1

        return self.clipper_points.copy(), self.clipper_vector.copy()

    def find_cut_points_and_vectors(self):
        self.set_lines_label()
        self.calculate_cutpoints()
        self.calculate_cut_vector()
        return self.cut_points, self.cut_vectors

    def set_lines_label(self):
        cca_line = None
        ica_line = None
        eca_line = None

        for line in self.connectivity:
            if self.clipper_points["cca"].get_id() in line and self.bf_point.get_id() in line:
                cca_line = self.label_line_segment(line, self.bf_point.get_id(), self.clipper_points["cca"].get_id())
            if self.clipper_points["ica"].get_id() in line and self.bf_point.get_id() in line:
                ica_line = self.label_line_segment(line, self.bf_point.get_id(), self.clipper_points["ica"].get_id())
            if self.clipper_points["eca"].get_id() in line and self.bf_point.get_id() in line:
                eca_line = self.label_line_segment(line, self.bf_point.get_id(), self.clipper_points["eca"].get_id())

        # Check if all lines were found
        if cca_line is None:
            raise ValueError("CCA line not found.")
        if ica_line is None:
            raise ValueError("ICA line not found.")
        if eca_line is None:
            raise ValueError("ECA line not found.")

        self.labeled_line["cca"] = cca_line
        self.labeled_line["ica"] = ica_line
        self.labeled_line["eca"] = eca_line

    @classmethod
    def label_line_segment(cls, line, bifurcation_pt_id, end_pt_id):
        """
        Extract the part of the line from bifurcation point to the endpoint.
        We assume the bifurcation point is on the line, so we split the line at the bifurcation.
        """
        if bifurcation_pt_id in line and end_pt_id in line:
            bifurcation_idx = line.index(bifurcation_pt_id)
            end_pt_idx = line.index(end_pt_id)

            # Extract the segment from bifurcation to the end point
            if bifurcation_idx < end_pt_idx:
                return line[bifurcation_idx:end_pt_idx + 1]  # Forward segment
            else:
                return line[end_pt_idx:bifurcation_idx + 1][::-1]  # Reverse segment
        return None

    def calculate_cutpoints(self):
        cut_point_indices = OrderedDict()
        points_list = []
        for k in self.labeled_line:
            cut_point_indices[k] = self.select_points_in_line(self.labeled_line[k])
            for idx in cut_point_indices[k]:
                pnt_coord = self.point_coords[idx]
                point = Point(idx, pnt_coord[0], pnt_coord[1], pnt_coord[2])
                point.set_radius(VTK.get_radius_for_coord(self.centerline_polydata, pnt_coord))
                points_list.append(point)
            self.cut_points[k] = points_list.copy()
            points_list.clear()

    def calculate_cut_vector(self):
        cut_vector_list = []
        for k in self.cut_points:
            for point in self.cut_points[k]:
                destination_coord = self.centerline_polydata.GetPoint(point.get_id())
                origin_coord = self.centerline_polydata.GetPoint(int(point.get_id() - 1))
                x_normalize = destination_coord[0] - origin_coord[0]
                y_normalize = destination_coord[1] - origin_coord[1]
                z_normalize = destination_coord[2] - origin_coord[2]
                normalize_vector_item = [x_normalize, y_normalize, z_normalize]
                cut_vector_list.append(normalize_vector_item)
            self.cut_vectors[k] = cut_vector_list.copy()
            cut_vector_list.clear()

    @classmethod
    def select_points_in_line(cls, line, num_parts=5):
        if len(line) < num_parts:
            raise ValueError("Line is too short to divide into parts.")

        # Calculate the dividing indices
        dividing_indices = [int(round(i * (len(line) - 1) / num_parts)) for i in range(1, num_parts)]

        # Select the points corresponding to the indices
        selected_points_indices = [line[idx] for idx in dividing_indices]

        return selected_points_indices

    def get_centerline_polydata(self):
        return self.centerline_polydata

    def get_clipper_points_and_vector(self):
        return self.clipper_points, self.clipper_vector

    def get_point_coords(self):
        return self.point_coords

    def get_cutpoints(self):
        return self.cut_points

    def get_bf_point(self):
        return self.bf_point

    def create_split_relabeled_centerline(self):
        split_centerline = VTK.create_split_centerline(self.labeled_line, self.point_coords, self.centerline_polydata)
        relabel_centerline = VTK.relabel_lines(split_centerline, self.bf_point.get_id())
        return split_centerline, relabel_centerline
