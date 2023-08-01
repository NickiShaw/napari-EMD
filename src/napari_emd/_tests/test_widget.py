import numpy as np
from napari_emd._widget import EMDWidget
import unittest
from qtpy.QtWidgets import QApplication
from napari.utils._testsupport import make_napari_viewer
import napari


def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()

    # create our widget, passing in the viewer
    my_widget = EMDWidget(viewer)

    # viewer.window.addWidget(my_widget)

    # We only test whether we can instantiate the widget and add to window
    assert my_widget is not None
