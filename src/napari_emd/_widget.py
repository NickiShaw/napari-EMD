from napari.utils.notifications import show_info
import napari
from napari_plugin_engine import napari_hook_implementation

from qtpy.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QLabel, QTreeWidget, QTreeWidgetItem
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import napari


class EMDWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.current_metadata_widget = None

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.current_layout = layout

        # Active layer label (top layer in list view).
        self.nm = QLabel()
        self.current_layout.addWidget(self.nm)
        # Update layer label when file is changed.
        self.viewer.layers.events.reordered.connect(self.update_frame_name_and_metadata)

        # Set frame label.
        self.lb = QLabel()
        self.current_layout.addWidget(self.lb)
        # Update frame label when frame is changed.
        self.viewer.dims.events.current_step.connect(self.update_frame_name_and_metadata)

        self.update_frame_name_and_metadata()

        # Button to perform action _on_click.
        # btn = QPushButton("Export metadata")
        # btn.clicked.connect(self._on_click)
        # self.current_layout.addWidget(btn)

    def get_topmost_layer_name(self):
        if len(self.viewer.layers) == 0:
            return "No image open"

        # Get name of topmost layer in list to display in metadata view.
        return 'Image ' + str(self.viewer.layers[-1])

    def get_current_frame_number(self):
        # Return number of frames.
        if len(self.viewer.layers) > 0 and len(self.viewer.layers[-1].data.shape) > 2:
            return self.viewer.dims.current_step[0]
        else:
            return 0  # single frame

    def get_frame_number_label(self):
        if len(self.viewer.layers) == 0:
            return ""

        # Return frame number for stack images, or 'Single frame' for single images.
        if len(self.viewer.layers[-1].data.shape) > 2:
            return 'Frame #' + str(self.viewer.dims.current_step[0])
        else:
            return 'Single frame'

    def get_empty_metadata_view(self):
        tabs = QTabWidget()
        empty_tab = QTreeWidget()
        empty_tab.setHeaderLabels([''])
        tabs.addTab(empty_tab, 'Metadata')
        return tabs

    def get_metadata_view(self, frame_num: int):
        assert (self.is_current_layer_emd())

        # Get metadata from kwargs of topmost layer.
        data_dict = self.viewer.layers[-1].metadata

        # Get frame of metadata to unpack.
        frame_meta = data_dict['frames_metadata'][frame_num]

        tabs = QTabWidget()

        tab_list = self.create_tabs_ui(frame_meta)
        for tab_widget, tab_name in tab_list:
            tabs.addTab(tab_widget, tab_name)

        return tabs

    def create_tabs_ui(self, tab_items):
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

    def update_frame_name_and_metadata(self):
        self.nm.setText(self.get_topmost_layer_name())

        # Get the frame number for the image if it is a stack.
        self.lb.setText(self.get_frame_number_label())

        self.update_metadata()


    def is_current_layer_emd(self):
        if len(self.viewer.layers) == 0:
            return False

        # Get metadata for topmost layer.
        # See _reader.py for the format of the metadata dictionary.
        data_dict = self.viewer.layers[-1].metadata
        return data_dict and 'tag' in data_dict and data_dict['tag'] == 'emdfile'

    def update_metadata(self):
        # Remove old metadata view.
        if self.current_metadata_widget:
            self.current_layout.removeWidget(self.current_metadata_widget)
            self.current_metadata_widget = None

        # Create new metadata view.
        # Add an empty placeholder if the current layer does not have EMD metadata.
        if self.is_current_layer_emd():
            frame_num = self.get_current_frame_number()
            self.current_metadata_widget = self.get_metadata_view(frame_num)
        else:
            self.current_metadata_widget = self.get_empty_metadata_view()

        self.current_layout.addWidget(self.current_metadata_widget)

    def _on_click(self):
        # TODO: export metadata as .csv.
        pass
