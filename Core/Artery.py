from Core.Centerline import Centerline
import matplotlib.pyplot as plt
import pandas as pd
from collections import OrderedDict
from MathematicalFunction import MathematicalFunction as MF
from VTKModule.VTKReader import VTKReader
from VTKModule.VTKUtils import VTKUtils
from VTKModule.Writer import Writer


class Artery:
    def __init__(self, surface):
        self.surface = surface
        self.centerline = None
        self.combined_transform = OrderedDict()
        self.vtu_dataset = None
        self.vtp_dataset = None

    def create_centerline(self, centerline_polydata):
        self.centerline = Centerline(centerline_polydata)
        self.centerline.analyzing_centerline()

    def get_surface(self):
        return self.surface

    def get_centerline(self):
        return self.centerline

    def get_clipper_points(self):
        return self.centerline.get_clipper_points_and_vector()

    def plot_centerline(self):
        plt.switch_backend('TkAgg')
        plt3d = plt.figure()
        ax = plt3d.figure.add_subplot(111, projection='3d')

        x2 = self.centerline.get_point_coords()[:, 0]
        y2 = self.centerline.get_point_coords()[:, 1]
        z2 = self.centerline.get_point_coords()[:, 2]
        ax.scatter(x2, y2, z2, c='b', marker='o')
        for i, index in enumerate(self.centerline.get_point_coords()):
            if i % 11 == 1:
                id = self.centerline.get_centerline_polydata().FindPoint([x2[i], y2[i], z2[i]])
                ax.text(x2[i], y2[i], z2[i], str(id), color='black')
            elif i % 11 == 7:
                id = self.centerline.get_centerline_polydata().FindPoint([x2[i], y2[i], z2[i]])
                ax.text(x2[i], y2[i], z2[i], str(id), color='green')

        ax.scatter(self.centerline.bf_point.get_x(), self.centerline.bf_point.get_y(),
                   self.centerline.bf_point.get_z(), c='red', marker='o')
        ax.text(self.centerline.bf_point.get_x(), self.centerline.bf_point.get_y(), self.centerline.bf_point.get_z(),
                str(self.centerline.bf_point.get_id()), color='red')

        for k in self.centerline.end_points:
            ax.scatter(self.centerline.end_points[k].get_x(), self.centerline.end_points[k].get_y(),
                       self.centerline.end_points[k].get_z(), c='red', marker='o')

            ax.text(self.centerline.end_points[k].get_x(), self.centerline.end_points[k].get_y(),
                    self.centerline.end_points[k].get_z(),
                    str(self.centerline.end_points[k].get_id()) + " " + k, color='yellow')

        for k in self.centerline.get_cutpoints():
            ax.scatter(self.centerline.cut_points[k].get_x(), self.centerline.cut_points[k].get_y(),
                       self.centerline.cut_points[k].get_z(), c='red', marker='o')

        # for k in cut_points:
        #     ax.scatter(cut_points[k][1], cut_points[k][2], cut_points[k][3], c='yellow', marker='o')

        plt.show()

    def set_registration_matrix(self, matrix):
        self.combined_transform = matrix

    def get_clipper_points_vectors(self, variation_rate):
        clipper_points, clipper_vectors = self.centerline.find_clipper_points_and_vectors(variation_rate)
        return clipper_points, clipper_vectors

    def get_cutpoints_vectors(self):
        cut_points, cut_vectors = self.centerline.find_cut_points_and_vectors()
        return cut_points, cut_vectors

    def get_bf_point(self):
        return self.centerline.get_bf_point()

    def get_combined_transform(self):
        return self.combined_transform

    def set_vtu_dataset(self, vtu_dataset):
        self.vtu_dataset = vtu_dataset

    def get_vtu_dataset(self):
        return self.vtu_dataset

    def set_vtp_dataset(self, vtu_dataset):
        self.vtp_dataset = vtu_dataset

    def get_vtp_dataset(self):
        return self.vtp_dataset
