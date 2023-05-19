

from napari.utils.notifications import show_info
import napari
from napari_plugin_engine import napari_hook_implementation

from qtpy.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QSpinBox, QLabel, QFrame, QFileDialog, QWidget, QApplication

from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget, QLabel

if TYPE_CHECKING:
    import napari

from napari.utils.events import Event

class EMDWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

        self.lb = QLabel('frame is' + str(self.viewer.dims.current_step[0]))
        self.layout().addWidget(self.lb)

        self.viewer.dims.events.current_step.connect(self.update_metadata)

    def update_metadata(self):
        self.lb.setText('frame is' + str(self.viewer.dims.current_step[0]))
        print('frame is' + str(self.viewer.dims.current_step[0]))

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

