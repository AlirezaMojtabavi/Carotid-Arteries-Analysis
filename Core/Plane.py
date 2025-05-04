class Plane:
    def __init__(self, point, normal_vector, pyvista_plane):
        self.point = point
        self.vector = normal_vector
        self.pyvista_plane = pyvista_plane

    def get_pyvista_plane(self):
        return self.pyvista_plane

    def get_point(self):
        return self.point
