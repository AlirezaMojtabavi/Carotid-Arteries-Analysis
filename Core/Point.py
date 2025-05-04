class Point:
    def __init__(self, id, x, y, z, branch=None, critical_status=None):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.radius = None
        self.branch = branch
        self.critical_status = critical_status

    def set_critical_status(self, critical_status):
        self.critical_status = critical_status

    def set_branch(self, branch_name):
        self.branch = branch_name

    def set_radius(self, radius):
        self.radius = radius

    def get_radius(self):
        return self.radius

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_id(self):
        return self.id
