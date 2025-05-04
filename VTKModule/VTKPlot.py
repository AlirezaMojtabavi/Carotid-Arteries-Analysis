import matplotlib.pyplot as plt
import vtk
import pyvista as pv
from VTKModule.VTKReader import VTKReader as vtkRdr

plt.switch_backend('TkAgg')


class VTKPlot:
    @classmethod
    def plot_centerline_endpoints_cutPoints(cls, centerline_points, endpoints_properties,
                                            cut_points, bifurcation_point):
        plt3d = plt.figure()
        ax = plt3d.figure.add_subplot(111, projection='3d')

        x2 = centerline_points[:, 1]
        y2 = centerline_points[:, 2]
        z2 = centerline_points[:, 3]
        ax.scatter(x2, y2, z2, c='b', marker='o')
        for i, index in enumerate(centerline_points):
            if i % 10 == 1:
                ax.text(x2[i], y2[i], z2[i], str(int(centerline_points[i, 0])), color='black')
            elif i % 10 == 5:
                ax.text(x2[i], y2[i], z2[i], str(int(centerline_points[i, 0])), color='green')

        for k in range(len(bifurcation_point)):
            ax.scatter(bifurcation_point[k][1], bifurcation_point[k][2], bifurcation_point[k][3], c='red', marker='o')
            ax.text(bifurcation_point[k][1], bifurcation_point[k][2], bifurcation_point[k][3],
                    str(int(bifurcation_point[k][0])), color='red')
            print(str(int(bifurcation_point[k][0])))

        for k in endpoints_properties:
            ax.scatter(endpoints_properties[k][1], endpoints_properties[k][2], endpoints_properties[k][3], c='red',
                       marker='o')
            ax.text(endpoints_properties[k][1], endpoints_properties[k][2], endpoints_properties[k][3],
                    str(int(endpoints_properties[k][0])) + " " + k, color='red')

        for k in cut_points:
            ax.scatter(cut_points[k][1], cut_points[k][2], cut_points[k][3], c='yellow', marker='o')

        plt.show()

    @classmethod
    def visualize_vtk_file(cls, vtk_file_path):
        vtk_data = pv.read(vtk_file_path)

        # Extract the surface
        surface = vtk_data.extract_surface()

        stl_surface_mapper = vtk.vtkPolyDataMapper()
        stl_surface_mapper.SetInputData(surface)
        stl_surface = vtk.vtkUnstructuredGridReader()
        stl_surface.SetFileName(vtk_file_path)
        stl_surface.Update()
        stl_surface_mapper = vtk.vtkPolyDataMapper()
        stl_surface_mapper.SetInputConnection(stl_surface.GetOutputPort())
        stl_surface_actor = vtk.vtkActor()
        stl_surface_actor.SetMapper(stl_surface_mapper)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(stl_surface_actor)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        interactor.Initialize()
        render_window.Render()
        interactor.Start()

    @classmethod
    def rendering_surface_centerline_sphere_cuts(cls, artery, cut_planes_dict, centerline_polydata, sphere_radius_coef,
                                                 clipper_planes_dict=None, window_title=None):
        actors_dict = dict()
        renderer = vtk.vtkRenderer()

        artery_mapper = vtk.vtkDataSetMapper()
        artery_mapper.SetInputData(artery)
        artery_actor = vtk.vtkActor()
        artery_actor.SetMapper(artery_mapper)
        artery_actor.GetProperty().SetOpacity(0.7)
        renderer.AddActor(artery_actor)
        actors_dict["Artery"] = artery_actor

        centerline_mapper = vtk.vtkPolyDataMapper()
        centerline_mapper.SetInputData(centerline_polydata)
        centerline_actor = vtk.vtkActor()
        centerline_actor.SetMapper(centerline_mapper)
        centerline_actor.GetProperty().SetColor(1, 0, 0)
        centerline_actor.GetProperty().SetLineWidth(7)
        renderer.AddActor(centerline_actor)
        actors_dict["Centerline"] = centerline_actor

        # for k in cut_planes_dict:
        #     i = 0
        #     for plane in cut_planes_dict[k]:
        #         if i == 1:
        #             pyvista_plane = plane.get_pyvista_plane()
        #             sphere_radius = plane.get_point().get_radius() * sphere_radius_coef
        #             sphere = vtk.vtkSphereSource()
        #             center = pyvista_plane.center
        #             sphere.SetCenter(center)
        #             sphere.SetRadius(sphere_radius)
        #             sphere.Update()
        #             sphere_mapper = vtk.vtkPolyDataMapper()
        #             sphere_mapper.SetInputConnection(sphere.GetOutputPort())
        #             sphere_actor = vtk.vtkActor()
        #             sphere_actor.SetMapper(sphere_mapper)
        #             sphere_actor.GetProperty().SetOpacity(0.5)
        #             renderer.AddActor(sphere_actor)
        #         i += 1

        if clipper_planes_dict is not None:
            for k in clipper_planes_dict:
                plane_mapper = vtk.vtkPolyDataMapper()
                plane_mapper.SetInputData(clipper_planes_dict[k].get_pyvista_plane())
                plane_actor = vtk.vtkActor()
                plane_actor.SetMapper(plane_mapper)
                plane_actor.GetProperty().SetColor(1, 0, 0)
                renderer.AddActor(plane_actor)
                actors_dict[k] = plane_actor

        for k in cut_planes_dict:
            i = 0
            for plane in cut_planes_dict[k]:
                plane_mapper = vtk.vtkPolyDataMapper()
                plane_mapper.SetInputData(plane.get_pyvista_plane())
                plane_actor = vtk.vtkActor()
                plane_actor.SetMapper(plane_mapper)
                if i == 0:
                    plane_actor.GetProperty().SetColor(0, 1, 0)
                renderer.AddActor(plane_actor)
                actors_dict[k + str(i)] = plane_actor
                i += 1

        # render_window = vtk.vtkRenderWindow()
        # render_window.AddRenderer(renderer)
        # renderer.SetBackground(1, 1, 1)
        # interactor = vtk.vtkRenderWindowInteractor()
        # interactor.SetRenderWindow(render_window)
        # render_window.SetWindowName(window_title)
        # render_window.SetSize(750, 950)
        #
        # interactor.Initialize()
        # render_window.Render()
        # interactor.Start()

        return actors_dict

    @classmethod
    def plot_surface_and_centerline(cls, main_path, centerline_reader, window_name):
        renderer = vtk.vtkRenderer()
        main_reader = vtkRdr.read_stl_file(main_path)

        main_surface_mapper = vtk.vtkPolyDataMapper()
        main_surface_mapper.SetInputConnection(main_reader.GetOutputPort())
        main_surface_actor = vtk.vtkActor()
        main_surface_actor.SetMapper(main_surface_mapper)
        main_surface_actor.GetProperty().SetOpacity(0.85)
        renderer.AddActor(main_surface_actor)

        centerline_mapper = vtk.vtkPolyDataMapper()
        centerline_mapper.SetInputData(centerline_reader)
        centerline_surface_actor = vtk.vtkActor()
        centerline_surface_actor.SetMapper(centerline_mapper)
        centerline_surface_actor.GetProperty().SetColor(1, 0, 0)
        centerline_surface_actor.GetProperty().SetLineWidth(7)
        renderer.AddActor(centerline_surface_actor)

        render_window = vtk.vtkRenderWindow()
        renderer.SetBackground(1, 1, 1)
        render_window.AddRenderer(renderer)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)
        render_window.SetSize(700, 900)

        interactor.Initialize()
        render_window.Render()
        render_window.SetWindowName(window_name)
        interactor.Start()

    @classmethod
    def visualization_of_two_stl(cls, main_path, second_path):
        main_reader = vtkRdr.read_stl_file(main_path)
        second_reader = vtkRdr.read_stl_file(second_path)
        cls.rendering_two_polydata(main_reader.GetOutput(), second_reader.GetOutput())

    @classmethod
    def rendering_three_dataset(cls, first_dataset, second_dataset, third_dataset, window_title=None):
        first_surface_mapper = vtk.vtkDataSetMapper()
        if isinstance(first_dataset, vtk.vtkUnstructuredGrid):
            first_surface_mapper.SetInputData(first_dataset)
        elif isinstance(first_dataset, vtk.vtkPolyData):
            first_surface_mapper.SetInputData(first_dataset)
        else:
            first_surface_mapper.SetInputConnection(first_dataset.GetOutputPort())
        first_surface_actor = vtk.vtkActor()
        first_surface_actor.SetMapper(first_surface_mapper)
        first_surface_actor.GetProperty().SetColor(1, 1, 0)  # yellow
        first_surface_actor.GetProperty().SetOpacity(0.95)

        second_surface_mapper = vtk.vtkDataSetMapper()
        if isinstance(third_dataset, vtk.vtkTransformFilter):
            second_surface_mapper.SetInputData(second_dataset.GetOutput())
        else:
            second_surface_mapper.SetInputData(second_dataset)
        second_surface_actor = vtk.vtkActor()
        second_surface_actor.SetMapper(second_surface_mapper)
        second_surface_actor.GetProperty().SetColor(1, 0, 0)
        second_surface_actor.GetProperty().SetOpacity(0.8)

        third_surface_mapper = vtk.vtkDataSetMapper()
        if isinstance(third_dataset, vtk.vtkTransformFilter):
            third_surface_mapper.SetInputData(third_dataset.GetOutput())
        else:
            third_surface_mapper.SetInputData(third_dataset)

        third_surface_actor = vtk.vtkActor()
        third_surface_actor.SetMapper(third_surface_mapper)
        third_surface_actor.GetProperty().SetColor(0, 0, 1)
        third_surface_actor.GetProperty().SetOpacity(0.9)

        # renderer = vtk.vtkRenderer()
        # renderer.AddActor(first_surface_actor)
        # renderer.AddActor(second_surface_actor)
        # renderer.AddActor(third_surface_actor)
        #
        # render_window = vtk.vtkRenderWindow()
        # render_window.AddRenderer(renderer)
        #
        # interactor = vtk.vtkRenderWindowInteractor()
        # interactor.SetRenderWindow(render_window)
        #
        # interactor.Initialize()
        # render_window.Render()
        # render_window.SetWindowName(window_title)
        # interactor.Start()

        return first_surface_actor, second_surface_actor, third_surface_actor

    @classmethod
    def rendering_two_dataset(cls, first_dataset, third_dataset, window_title=None):
        first_surface_mapper = vtk.vtkDataSetMapper()
        if isinstance(first_dataset, vtk.vtkUnstructuredGrid):
            first_surface_mapper.SetInputData(first_dataset)
        elif isinstance(first_dataset, vtk.vtkPolyData):
            first_surface_mapper.SetInputData(first_dataset)
        else:
            first_surface_mapper.SetInputConnection(first_dataset.GetOutputPort())
        first_surface_actor = vtk.vtkActor()
        first_surface_actor.SetMapper(first_surface_mapper)
        first_surface_actor.GetProperty().SetColor(1, 1, 0)  # yellow
        first_surface_actor.GetProperty().SetOpacity(0.95)

        third_surface_mapper = vtk.vtkDataSetMapper()
        if isinstance(third_dataset, vtk.vtkTransformFilter):
            third_surface_mapper.SetInputData(third_dataset.GetOutput())
        else:
            third_surface_mapper.SetInputData(third_dataset)

        third_surface_actor = vtk.vtkActor()
        third_surface_actor.SetMapper(third_surface_mapper)
        third_surface_actor.GetProperty().SetColor(0, 0, 1)
        third_surface_actor.GetProperty().SetOpacity(0.9)

        return first_surface_actor, third_surface_actor

    @classmethod
    def rendering_two_polydata(cls, first_polydata, second_polydata, window_title=None):
        first_surface_mapper = vtk.vtkPolyDataMapper()
        first_surface_mapper.SetInputData(first_polydata)
        first_surface_actor = vtk.vtkActor()
        first_surface_actor.SetMapper(first_surface_mapper)
        first_surface_actor.GetProperty().SetColor(1, 0, 0)
        first_surface_actor.GetProperty().SetOpacity(0.95)

        second_surface_mapper = vtk.vtkPolyDataMapper()
        second_surface_mapper.SetInputData(second_polydata)
        second_surface_actor = vtk.vtkActor()
        second_surface_actor.SetMapper(second_surface_mapper)
        second_surface_actor.GetProperty().SetColor(0, 0, 1)
        second_surface_actor.GetProperty().SetOpacity(0.8)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(first_surface_actor)
        renderer.AddActor(second_surface_actor)
        renderer.SetBackground(1, 1, 1)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(700, 900)
        if window_title is not None:
            render_window.SetWindowName(window_title)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        interactor.Initialize()
        render_window.Render()
        interactor.Start()

    @classmethod
    def render_one_polydata(cls, polydata):
        polydata_surface_mapper = vtk.vtkPolyDataMapper()
        polydata_surface_mapper.SetInputData(polydata)
        polydata_surface_actor = vtk.vtkActor()
        polydata_surface_actor.SetMapper(polydata_surface_mapper)
        polydata_surface_actor.GetProperty().SetColor(0, 0, 1)
        polydata_surface_actor.GetProperty().SetOpacity(0.8)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(polydata_surface_actor)
        renderer.SetBackground(1, 1, 1)

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(700, 900)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        interactor.Initialize()
        render_window.Render()
        interactor.Start()

    @classmethod
    def render_DataSet(cls, flow_vtk_path):
        reader = vtkRdr.read_vtk_dataset(flow_vtk_path)
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        renderer = vtk.vtkRenderer()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(renderer)

        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        renderer.AddActor(actor)
        renderWindow.SetSize(700, 900)
        renderer.SetBackground(0, 0, 0)
        renderWindow.Render()
        renderWindowInteractor.Start()

    @classmethod
    def render_unstructuredGrid(cls, carotid_arteries_grid, full_domain_dataSet, window_title):
        carotid_arteries_mapper = vtk.vtkDataSetMapper()
        carotid_arteries_mapper.SetInputData(carotid_arteries_grid)
        carotid_arteries_actor = vtk.vtkActor()
        carotid_arteries_actor.SetMapper(carotid_arteries_mapper)
        carotid_arteries_actor.GetProperty().SetColor(0, 0, 1)

        full_domain_mapper = vtk.vtkDataSetMapper()
        full_domain_mapper.SetInputData(full_domain_dataSet)

        full_domain_actor = vtk.vtkActor()
        full_domain_actor.SetMapper(full_domain_mapper)
        full_domain_actor.GetProperty().SetOpacity(0.55)
        full_domain_actor.GetProperty().SetColor(0, 1, 0)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(carotid_arteries_actor)
        renderer.AddActor(full_domain_actor)
        renderer.SetBackground(1, 1, 1)

        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(renderer)

        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        renderWindowInteractor.SetInteractorStyle(interactorStyle)
        renderWindow.SetSize(700, 900)

        renderWindow.Render()
        renderWindow.SetWindowName(window_title)
        renderWindowInteractor.Start()

    @classmethod
    def render_vtkSTL_file(cls, stl_file_path, window_title=None):
        stl_reader = vtkRdr.read_stl_file(stl_file_path)
        stl_surface_mapper = vtk.vtkPolyDataMapper()
        stl_surface_mapper.SetInputConnection(stl_reader.GetOutputPort())
        stl_surface_actor = vtk.vtkActor()
        stl_surface_actor.SetMapper(stl_surface_mapper)

        # renderer = vtk.vtkRenderer()
        # renderer.AddActor(stl_surface_actor)
        # render_window = vtk.vtkRenderWindow()
        # renderer.SetBackground(1, 1, 1)
        # render_window.AddRenderer(renderer)
        # if window_title is not None:
        #     render_window.SetWindowName(window_title)
        # render_window.SetSize(700, 900)
        # interactor = vtk.vtkRenderWindowInteractor()
        # interactor.SetRenderWindow(render_window)
        # interactor.Initialize()
        # render_window.Render()
        # interactor.Start()
        return stl_surface_actor

    @classmethod
    def render_two_stl_file(cls, org_file, smooth_file, window_title):
        org_reader = vtkRdr.read_stl_file(org_file)
        org_surface_mapper = vtk.vtkPolyDataMapper()
        org_surface_mapper.SetInputConnection(org_reader.GetOutputPort())
        org_surface_actor = vtk.vtkActor()
        org_surface_actor.SetMapper(org_surface_mapper)
        org_surface_actor.GetProperty().SetOpacity(0.75)
        org_surface_actor.GetProperty().SetColor(0, 1, 0)

        smooth_reader = vtkRdr.read_stl_file(smooth_file)
        smooth_surface_mapper = vtk.vtkPolyDataMapper()
        smooth_surface_mapper.SetInputConnection(smooth_reader.GetOutputPort())
        smooth_surface_actor = vtk.vtkActor()
        smooth_surface_actor.SetMapper(smooth_surface_mapper)
        smooth_surface_actor.GetProperty().SetOpacity(0.9)
        smooth_surface_actor.GetProperty().SetColor(1, 0, 0)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(org_surface_actor)
        renderer.AddActor(smooth_surface_actor)

        render_window = vtk.vtkRenderWindow()
        renderer.SetBackground(1, 1, 1)
        render_window.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)
        render_window.SetSize(700, 900)
        interactor.Initialize()
        render_window.Render()
        render_window.SetWindowName(window_title)
        interactor.Start()

    @classmethod
    def render_two_poly_data(cls, polydata1, polydata2, window_title=None):
        org_surface_mapper = vtk.vtkPolyDataMapper()
        if isinstance(polydata1, vtk.vtkPolyData):
            org_surface_mapper.SetInputData(polydata1)
        else:
            org_surface_mapper.SetInputConnection(polydata1.GetOutputPort())
        org_surface_actor = vtk.vtkActor()
        org_surface_actor.SetMapper(org_surface_mapper)
        org_surface_actor.GetProperty().SetOpacity(0.75)
        org_surface_actor.GetProperty().SetColor(0, 1, 0)

        smooth_surface_mapper = vtk.vtkPolyDataMapper()
        if isinstance(polydata2, vtk.vtkPolyData):
            smooth_surface_mapper.SetInputData(polydata2)
        else:
            smooth_surface_mapper.SetInputConnection(polydata2.GetOutputPort())

        smooth_surface_actor = vtk.vtkActor()
        smooth_surface_actor.SetMapper(smooth_surface_mapper)
        smooth_surface_actor.GetProperty().SetOpacity(0.9)
        smooth_surface_actor.GetProperty().SetColor(1, 0, 0)

        # renderer = vtk.vtkRenderer()
        # renderer.AddActor(org_surface_actor)
        # renderer.AddActor(smooth_surface_actor)
        #
        # render_window = vtk.vtkRenderWindow()
        # renderer.SetBackground(1, 1, 1)
        # render_window.AddRenderer(renderer)
        # interactor = vtk.vtkRenderWindowInteractor()
        # interactor.SetRenderWindow(render_window)
        # render_window.SetSize(700, 900)
        # interactor.Initialize()
        # render_window.Render()
        # render_window.SetWindowName(window_title)
        # interactor.Start()

        return org_surface_actor, smooth_surface_actor
