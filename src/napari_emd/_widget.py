from napari.utils.notifications import show_info
import napari
from napari_plugin_engine import napari_hook_implementation

from qtpy.QtWidgets import QPushButton, QVBoxLayout, QSpinBox, QLabel, QFrame, QFileDialog, QWidget, QApplication, \
    QListWidget, QTabWidget, QWidget, QLabel, QTreeWidget, QTreeWidgetItem
from typing import TYPE_CHECKING
from collections.abc import Iterable

from magicgui import magic_factory

if TYPE_CHECKING:
    import napari


class EMDWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.current_metadata_tabs = None
        layout = QVBoxLayout()
        self.setLayout(layout)

        if not self.viewer.layers:
            raise Exception('Provide an image, and re-open the widget.')

        # Active layer label (top layer in list view).
        self.nm = QLabel(self.get_topmost_image())
        self.layout().addWidget(self.nm)
        # Update file name (and frame number) when file is changed.
        self.viewer.layers.events.reordered.connect(self.update_layer_name)

        # Set frame number label.
        self.lb = QLabel(self.get_frame_name())
        self.layout().addWidget(self.lb)
        # Update frame number when frame is changed.
        self.viewer.dims.events.current_step.connect(self.update_frame_name_and_metadata)

        self.update_metadata()

        # # Add this files scenes widget to viewer
        # self.list_widget = QListWidget()
        # self.list_widget.setWindowTitle("EMD frame metadata")
        # self.list_widget.addItem("test")
        #
        # # Add this files scenes widget to viewer
        # self.viewer.window.add_dock_widget(self.list_widget, area="right")

        # Button to perform action _on_click.
        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.layout().addWidget(btn)

    def get_topmost_image(self):
        # Get name of topmost layer in list to display in metadata view.
        return 'Image ' + str(self.viewer.layers[-1])

    def get_current_frame(self):
        # Return number of frames.
        if len(self.viewer.layers[-1].data.shape) > 2:
            return self.viewer.dims.current_step[0]
        else:
            return 0  # single frame

    def get_frame_name(self):
        # Return frame number for stack images, or 'Single frame' for single images.
        if len(self.viewer.layers[-1].data.shape) > 2:
            return 'Frame #' + str(self.viewer.dims.current_step[0])
        else:
            return 'Single frame'

    def collect_items(self, dict_items: dict):
        items = []
        for key, val in dict_items.items():
            if isinstance(val, str):
                items.append((key, val))
        return items

    def display_metadata(self, framenum: int):
        # Get metadata from kwargs of topmost layer.
        data = self.viewer.layers[-1].metadata
        # Get frame of metadata to unpack.
        frame_meta = data[framenum]

        tabs = QTabWidget()

        tab_list = self.createTabsUI(frame_meta)
        for tab_widget, tab_name in tab_list:
            tabs.addTab(tab_widget, tab_name)

        return tabs

    def createTabsUI(self, tab_items):
        tabs_by_name = {}
        items_by_tab_name = {}

        # Go over each top-level item and create a tab representing each non-trivial group (i.e. where the value is a
        # dictionary).
        for key, val in tab_items.items():
            if isinstance(val, dict):
                tab = QTreeWidget()
                tab.setColumnCount(2)
                tab.setHeaderLabels(['Name', 'Value'])
                tabs_by_name[key] = tab

        # Add an extra tab for any top-level items that are just plain strings.
        extra_tab = QTreeWidget()
        extra_tab.setColumnCount(2)
        extra_tab.setHeaderLabels(['Name', 'Value'])
        tabs_by_name['Extra Items'] = extra_tab
        items_by_tab_name['Extra Items'] = []

        for key, val in tab_items.items():
            if isinstance(val, str):
                items_by_tab_name['Extra Items'].append(QTreeWidgetItem([key, val]))
            else:
                items_by_tab_name[key] = self.collectInnerWidgetItems(val)

        for tab_name, tab_items in items_by_tab_name.items():
            tabs_by_name[tab_name].insertTopLevelItems(0, tab_items)

        tabs = []
        for tab_name, tab_widget in tabs_by_name.items():
            tabs.append((tab_widget, tab_name))

        return tabs

    def collectInnerWidgetItems(self, dict_items):
        widget_items = []
        for key, val in dict_items.items():
            if isinstance(val, str):
                widget_items.append(QTreeWidgetItem([key, val]))
            elif isinstance(val, dict):
                # Collect a group of items.
                group_item = QTreeWidgetItem([key])
                group_children = self.collectInnerWidgetItems(val)
                group_item.addChildren(group_children)
                widget_items.append(group_item)

        return widget_items

    def update_layer_name(self):
        # Set name to image at the top of the layer list.
        self.nm.setText(self.get_topmost_image())
        # Update frame name automatically.
        self.update_frame_name()

    def update_frame_name_and_metadata(self):
        # Get the frame number for the image if it is a stack.
        self.lb.setText(self.get_frame_name())

        self.update_metadata()

    def update_metadata(self):
        if self.current_metadata_tabs:
            self.layout().removeWidget(self.current_metadata_tabs)
            self.current_metadata_tabs = None

        # Create the tabs for the metadata view.
        framenum = self.get_current_frame()
        tabs = self.display_metadata(framenum)
        self.current_metadata_tabs = tabs
        self.layout().addWidget(tabs)

    def _on_click(self):
        # print("napari has", len(self.viewer.layers), "layers")
        print("layer is " + str(self.viewer.layers[-1]))
        # print("the metadata is " + str(self.viewer.layers[0].metadata))
