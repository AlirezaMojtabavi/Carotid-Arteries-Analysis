import sys
import vtk
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QLabel, \
     QFrame, QGroupBox
from PyQt5.QtCore import Qt, QTimer, QThreadPool
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from FilesConfiguraiton import FilesConfiguration
from GUI.VolumeProcessingWorker import VolumeProcessingWorker
from GUI.ConsoleOutput import ConsoleOutput
from GUI.SettingWidget import SettingWidget
from GUI.CenterlineWidget import CenterlineWidget
from GUI.ClippedSurfaceWidget import ClippedSurfaceWidget
from PyQt5.QtGui import QIcon
from GUI.CutPlaneWidget import CutPlaneWidget
from GUI.VolumeProcessingWidget import VolumeProcessingWidget
from Stage import Stage
from GUI.Styles import sheet_style, main_group_style


class VTKPipelineGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.control_panel = None
        self.control_layout = None
        self.thread_pool = QThreadPool.globalInstance()  # Get global thread pool
        self.main_vertical_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()

        self.left_vtk_widget = None
        self.right_vtk_widget = None
        self.settingWidget = None
        self.centerline_widget = None
        self.clipped_surface_widget = None
        self.cutPlane_widget = None
        self.volume_processing_widget = None

        self.case_code = None
        self.side_chooser = None

        self.files_configuration = None
        self.stage = None
        self.left_plane_actors_dict = None
        self.right_plane_actors_dict = None
        self.removed_cutplane_actors_left = []
        self.removed_cutplane_actors_right = []
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Carotid Arteries Analysis")
        self.setWindowIcon(QIcon(FilesConfiguration.get_icon_pathName()))
        self.setGeometry(45, 45, 1600, 1080)  # Window size

        self.initUI()
        self.init_vtk()

        print("Let's begin")

    def initUI(self):
        self.control_panel = QWidget()
        self.control_panel.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        self.control_panel.setFixedWidth(350)

        self.control_layout = QVBoxLayout()
        self.control_layout.setContentsMargins(5, 2, 5, 2)
        self.control_panel.setLayout(self.control_layout)

        # ------------------------Setting----------------------
        self.settingWidget = SettingWidget()
        self.settingWidget.config_selected.connect(self.handle_config_selected)
        self.settingWidget.start_clicked_signal.connect(self.start_surface_processing)
        self.settingWidget.stop_clicked_signal.connect(self.stop)

        # ------------------------Centerline----------------------

        self.centerline_widget = CenterlineWidget()
        self.centerline_widget.confirm_clicked_signal.connect(self.confirm_centerline_pushed)
        self.centerline_widget.left_try_again_signal.connect(self.centerline_side_action)
        self.centerline_widget.right_try_again_signal.connect(self.centerline_side_action)

        # ------------------------Clipped Surface------------------------

        self.clipped_surface_widget = ClippedSurfaceWidget()
        self.clipped_surface_widget.confirm_clicked_signal.connect(self.confirm_clipped_pushed)
        self.clipped_surface_widget.update_parameters_signal.connect(self.apply_clipped_changes)

        # ------------------------Cut Plane----------------------------------------

        self.cutPlane_widget = CutPlaneWidget()
        self.cutPlane_widget.confirm_signal.connect(self.confirm_cut_plane_pushed)
        self.cutPlane_widget.toggled_name_signal.connect(self.toggled_cut_plane_slot)

        # ------------------------Volume Processing----------------------------------------

        self.volume_processing_widget = VolumeProcessingWidget()
        self.volume_processing_widget.confirm_registration_signal.connect(self.confirm_registration_pushed)

        # -----------------------Control panel --------------------------------
        control_groupbox = QGroupBox("Control Panel")
        control_groupbox.setStyleSheet(main_group_style)
        groupbox_layout = QVBoxLayout()
        groupbox_layout.setContentsMargins(2, 2, 2, 2)
        groupbox_layout.setSpacing(3)

        groupbox_layout.addWidget(self.wrap_centered(self.settingWidget))
        groupbox_layout.addWidget(self.create_separator())

        groupbox_layout.addWidget(self.wrap_centered(self.centerline_widget))
        groupbox_layout.addWidget(self.create_separator())

        groupbox_layout.addWidget(self.wrap_centered(self.clipped_surface_widget))
        groupbox_layout.addWidget(self.create_separator())

        groupbox_layout.addWidget(self.wrap_centered(self.cutPlane_widget))
        groupbox_layout.addWidget(self.create_separator())

        groupbox_layout.addWidget(self.wrap_centered(self.volume_processing_widget))

        groupbox_layout.addStretch()
        control_groupbox.setLayout(groupbox_layout)

        # Finally, add the group box to the control panel layout
        self.control_layout.addWidget(control_groupbox)

        # ------------------- VTK Viewport -------------------
        vtk_layout = QHBoxLayout()

        self.left_vtk_widget = QVTKRenderWindowInteractor()
        self.left_renderer = vtk.vtkRenderer()
        self.left_vtk_widget.GetRenderWindow().AddRenderer(self.left_renderer)
        left_label = QLabel("Left")
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        left_layout = QVBoxLayout()
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_vtk_widget)

        self.right_vtk_widget = QVTKRenderWindowInteractor()
        self.right_renderer = vtk.vtkRenderer()
        self.right_vtk_widget.GetRenderWindow().AddRenderer(self.right_renderer)
        right_label = QLabel("Right")
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_vtk_widget)

        vtk_layout.addLayout(left_layout)
        vtk_layout.addLayout(right_layout)

        # ------------------- Top Section -------------------
        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.control_panel, 1)
        self.top_layout.addLayout(vtk_layout, 3)

        # ------------------- Console -------------------
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: white; font-family: Monospace;")
        self.console_stream = ConsoleOutput(self.console_output)
        sys.stdout = self.console_stream

        # ------------------- Main Layout -------------------
        self.main_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.addLayout(self.top_layout, 3)
        self.main_vertical_layout.addWidget(self.console_output, 2)

        central_widget = QWidget()
        central_widget.setLayout(self.main_vertical_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(sheet_style)

    def handle_config_selected(self, case_code, side_chooser):
        self.case_code = case_code
        self.side_chooser = side_chooser
        self.centerline_widget.set_side(side_chooser)
        self.cutPlane_widget.set_side(side_chooser)
        self.files_configuration = FilesConfiguration(self.case_code, self.side_chooser)
        variation_rate = self.files_configuration.get_variation_rate()
        sphere_radius_coef = self.files_configuration.get_sphere_radius_coef()
        cutplane_size_coef = self.files_configuration.get_cutplane_size_coef()
        self.clipped_surface_widget.set_parameters(variation_rate, sphere_radius_coef, cutplane_size_coef)
        print(f"case code: {case_code}, side: {side_chooser}")

    def stop(self):
        print("Stopping all actions...")

        # Cancel/reset your logic/state
        self.stage = None  # Optional: release stage object
        self.left_renderer.RemoveAllViewProps()
        self.right_renderer.RemoveAllViewProps()
        self.left_vtk_widget.GetRenderWindow().Render()
        self.right_vtk_widget.GetRenderWindow().Render()
        # # Reset buttons
        self.settingWidget.reset_widget()
        self.centerline_widget.reset_widget()
        self.clipped_surface_widget.reset_widget()
        self.cutPlane_widget.reset_widget()
        self.volume_processing_widget.reset_widget()
        self.console_output.clear()

        print("Reset complete. Ready for new data.")

    def init_vtk(self):
        # Right: Two VTK Renderers
        self.left_vtk_widget.setWindowTitle("Left")
        self.left_renderer = vtk.vtkRenderer()
        self.left_renderer.SetBackground(1, 1, 1)

        self.right_vtk_widget.setWindowTitle("Right")
        self.right_renderer = vtk.vtkRenderer()
        self.right_renderer.SetBackground(1, 1, 1)

        self.left_vtk_widget.GetRenderWindow().AddRenderer(self.left_renderer)
        self.right_vtk_widget.GetRenderWindow().AddRenderer(self.right_renderer)

        self.left_interactor = self.left_vtk_widget.GetRenderWindow().GetInteractor()
        self.right_interactor = self.right_vtk_widget.GetRenderWindow().GetInteractor()

        self.left_interactor.Initialize()
        self.right_interactor.Initialize()

    def start_surface_processing(self):
        self.stage = Stage(self.files_configuration, self.side_chooser)
        self.stage.extract_arteries_surface()
        actor_plot_left, actor_plot_right = self.stage.extract_arteries_centerline()

        if len(actor_plot_left) > 0:
            self.left_renderer.AddActor(actor_plot_left[0])
            self.left_renderer.AddActor(actor_plot_left[1])
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()

        if len(actor_plot_right) > 0:
            self.right_renderer.AddActor(actor_plot_right[0])
            self.right_renderer.AddActor(actor_plot_right[1])
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()

        self.centerline_widget.confirm_centerline.setEnabled(True)
        self.centerline_widget.try_again_centerline.setEnabled(True)

    # =================== Centerline ======================

    def confirm_centerline_pushed(self):
        self.stage.save_and_set_centerline()
        actor_plot_left, actor_plot_right = self.stage.get_clipped_arteries_surface()
        if actor_plot_left is not None:
            self.left_renderer.RemoveAllViewProps()
            self.left_renderer.AddActor(actor_plot_left)
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()

        if actor_plot_right is not None:
            self.right_renderer.RemoveAllViewProps()
            self.right_renderer.AddActor(actor_plot_right)
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()

        self.clipped_surface_widget.enable_buttons()

    def centerline_side_action(self, str_side):
        if str_side == "left":
            actor_plot_left, actor_plot_right = self.stage.extract_arteries_centerline(True, "left")
            self.left_renderer.RemoveAllViewProps()
            self.left_renderer.AddActor(actor_plot_left[0])
            self.left_renderer.AddActor(actor_plot_left[1])
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()
            print("Left Side Centerline Generated")
        elif str_side == "right":
            actor_plot_left, actor_plot_right = self.stage.extract_arteries_centerline(True, "right")
            self.right_renderer.RemoveAllViewProps()
            self.right_renderer.AddActor(actor_plot_right[0])
            self.right_renderer.AddActor(actor_plot_right[1])
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()
            print("Right Side Centerline Generated")

    # =================== Clipped Surface ======================

    def confirm_clipped_pushed(self, cutplane_size_coef):
        self.left_plane_actors_dict, self.right_plane_actors_dict = self.stage.preparing_cut_planes(cutplane_size_coef)
        if self.left_plane_actors_dict is not None:
            self.left_renderer.RemoveAllViewProps()
            for k in self.left_plane_actors_dict:
                self.left_renderer.AddActor(self.left_plane_actors_dict[k])

            self.cutPlane_widget.set_actor_names(list(self.left_plane_actors_dict.keys()))
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()

        if self.right_plane_actors_dict is not None:
            self.right_renderer.RemoveAllViewProps()
            for k in self.right_plane_actors_dict:
                self.right_renderer.AddActor(self.right_plane_actors_dict[k])

            self.cutPlane_widget.set_actor_names(list(self.right_plane_actors_dict.keys()))
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()

        self.cutPlane_widget.enable_buttons()

    def apply_clipped_changes(self, variation_rate, sphere_radius_coef):
        actor_plot_left, actor_plot_right = self.stage.get_clipped_arteries_surface(variation_rate, sphere_radius_coef)
        if actor_plot_left is not None:
            self.left_renderer.RemoveAllViewProps()
            self.left_renderer.AddActor(actor_plot_left)
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()

        if actor_plot_right is not None:
            self.right_renderer.RemoveAllViewProps()
            self.right_renderer.AddActor(actor_plot_right)
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()

    # =================== Cut Planes ======================

    def toggled_cut_plane_slot(self, name, new_state, side=None):
        if side == "left":
            if new_state:
                print(f"{name} is checked (show actor)")
                if name in self.left_plane_actors_dict:
                    actor = self.left_plane_actors_dict[name]
                    self.left_renderer.AddActor(actor)
                    if name in self.removed_cutplane_actors_left:
                        self.removed_cutplane_actors_left.remove(name)
            else:
                print(f"{name} is unchecked (hide actor)")
                if name in self.left_plane_actors_dict:
                    actor = self.left_plane_actors_dict[name]
                    self.left_renderer.RemoveActor(actor)
                    self.removed_cutplane_actors_left.append(name)
            self.left_vtk_widget.GetRenderWindow().Render()

        elif side == "right":
            if new_state:
                print(f"{name} is checked (show actor)")
                if name in self.right_plane_actors_dict:
                    actor = self.right_plane_actors_dict[name]
                    self.right_renderer.AddActor(actor)
                    if name in self.removed_cutplane_actors_right:
                        self.removed_cutplane_actors_right.remove(name)
            else:
                print(f"{name} is unchecked (hide actor)")
                if name in self.right_plane_actors_dict:
                    actor = self.right_plane_actors_dict[name]
                    self.right_renderer.RemoveActor(actor)
                    self.removed_cutplane_actors_right.append(name)
            self.right_vtk_widget.GetRenderWindow().Render()

        else:
            if self.left_plane_actors_dict is not None:
                if new_state:
                    print(f"{name} is checked (show actor)")
                    if name in self.left_plane_actors_dict:
                        actor = self.left_plane_actors_dict[name]
                        self.left_renderer.AddActor(actor)
                        if name in self.removed_cutplane_actors_left:
                            self.removed_cutplane_actors_left.remove(name)
                else:
                    print(f"{name} is unchecked (hide actor)")
                    if name in self.left_plane_actors_dict:
                        actor = self.left_plane_actors_dict[name]
                        self.left_renderer.RemoveActor(actor)
                        self.removed_cutplane_actors_left.append(name)
                self.left_vtk_widget.GetRenderWindow().Render()

            if self.right_plane_actors_dict is not None:
                if new_state:
                    print(f"{name} is checked (show actor)")
                    if name in self.right_plane_actors_dict:
                        actor = self.right_plane_actors_dict[name]
                        self.right_renderer.AddActor(actor)
                        if name in self.removed_cutplane_actors_right:
                            self.removed_cutplane_actors_right.remove(name)
                else:
                    print(f"{name} is unchecked (hide actor)")
                    if name in self.right_plane_actors_dict:
                        actor = self.right_plane_actors_dict[name]
                        self.right_renderer.RemoveActor(actor)
                        self.removed_cutplane_actors_right.append(name)
                self.right_vtk_widget.GetRenderWindow().Render()

    def confirm_cut_plane_pushed(self):
        if self.left_plane_actors_dict is not None:
            if len(self.removed_cutplane_actors_left) > 0:
                self.stage.update_cutplanes(self.removed_cutplane_actors_left)

        if self.right_plane_actors_dict is not None:
            if len(self.removed_cutplane_actors_right) > 0:
                self.stage.update_cutplanes(self.removed_cutplane_actors_right)

        self.cutPlane_widget.disable_buttons()
        if self.side_chooser == 0:
            self.stage.left_registration_actors_signal.connect(
                lambda actors: self.add_actors_to_renderer(actors, "left"))
            QTimer.singleShot(0, self.stage.prepare_volume_processing)
        elif self.side_chooser == 1:
            self.stage.right_registration_actors_signal.connect(
                lambda actors: self.add_actors_to_renderer(actors, "right"))
            QTimer.singleShot(0, self.stage.prepare_volume_processing)
        elif self.side_chooser == 2:
            self.stage.left_registration_actors_signal.connect(
                lambda actors: self.add_actors_to_renderer(actors, "left"))
            self.stage.right_registration_actors_signal.connect(
                lambda actors: self.add_actors_to_renderer(actors, "right"))
            QTimer.singleShot(0, self.stage.prepare_volume_processing)
        self.volume_processing_widget.enable_buttons()

    def add_actors_to_renderer(self, actors, side):
        if side == "left":
            self.left_renderer.RemoveAllViewProps()
            for actor in actors:
                self.left_renderer.AddActor(actor)  # Add actors to the left renderer
            self.left_renderer.ResetCamera()
            self.left_vtk_widget.GetRenderWindow().Render()

        elif side == "right":
            self.right_renderer.RemoveAllViewProps()
            for actor in actors:
                self.right_renderer.AddActor(actor)  # Add actors to the right renderer
            self.right_renderer.ResetCamera()
            self.right_vtk_widget.GetRenderWindow().Render()

    # =================== volume Processing ======================

    def confirm_registration_pushed(self):
        self.volume_processing_widget.disable_buttons()
        worker = VolumeProcessingWorker(self.stage, self.on_processing_finished)
        self.thread_pool.start(worker)  # Run worker in background

    def try_again_registration_pushed(self):
        pass

    def on_processing_finished(self):
        print("Volume processing complete!")  # You can update UI here if needed
        self.volume_processing_widget.calculating_led.deactivate()
        self.volume_processing_widget.done_led.activate()

    @classmethod
    def create_separator(cls):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: gray; margin-top: 2px; margin-bottom: 2px;")  # tighter vertical spacing
        return line

    @classmethod
    def wrap_centered(cls, widget):
        """Wrap the given widget in a horizontal layout with stretch on both sides to center it."""
        hbox = QHBoxLayout()
        hbox.setSpacing(0)  # No spacing between widget and stretches
        hbox.setContentsMargins(0, 0, 0, 0)  # Remove any outer margin
        hbox.addStretch(1)
        hbox.addWidget(widget)
        hbox.addStretch(1)

        container = QWidget()
        container.setLayout(hbox)
        return container
