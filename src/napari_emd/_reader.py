"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
import numpy as np
import h5py
import time
import ujson
from collections.abc import Iterable


def rotateFrame(stack):
    for frame in range(len(stack)):
        stack[frame] = np.rot90(stack[frame])
    return stack


class navigate:

    @staticmethod
    def getGroupsNames(group):
        items = []
        for item in group:
            if group.get(item, getclass=True) == h5py._hl.group.Group:
                items.append(group.get(item).name)
        print(items)

    @staticmethod
    def getGroup(group, item):
        if group.get(item, getclass=True) == h5py._hl.group.Group:
            return group.get(item)

    @staticmethod
    def getSubGroup(group, path):
        return group[path]

    @staticmethod
    def getDirectoryMap(group):
        for item in group:
            # check if group
            if group.get(item, getclass=True) == h5py._hl.group.Group:
                item = group.get(item)
                # check if emd_group_type
                # if 'emd_group_type' in item.attrs:
                print('found a group emd at: {}'.format(item.name))
                # process subgroups
                if type(item) is h5py._hl.group.Group:
                    navigate.getDirectoryMap(item)
                else:
                    print('found an emd at: {}'.format(item))
                    # print(type(item))

    @staticmethod
    def getMemberName(group, path):
        members = list(group[path].keys())
        if len(members) == 1:
            return str(members[0])
        else:
            return members

    @staticmethod
    def parseFileName(file):
        return str(file).split("/")[-1].split(".")[0]


# class metadata:
#
#     def __init__(self, h5pyfile):
#         metalocation = navigate.getMemberName(h5pyfile, '/Data/Image/')  # CAUTION, may break.
#         self.meta = h5pyfile['/Data/Image/' + str(metalocation) + '/Metadata']
#         self.nframes = self.meta.shape[1]
#         self.transposed_meta = [list(i) for i in zip(*(self.meta[:]))]
#

#     def getMetaAllFrames(self, query):
#         for i in range(self.nframes):
#             meta = self.convertASCII(i)

class EMDreader:
    """
    Unpacks emd data files with the h5py package, by navigating subdirectories.

    Parameters
    ----------
    path : str
        Path to file, NOT a list of paths.
    """

    def __init__(self, singlePath: str):
        self.path = singlePath
        self.singleH5pyObject = h5py.File(singlePath, 'r', driver='core')

    @staticmethod
    def convertASCII(transposed_meta, frame):
        ascii_meta = transposed_meta[frame]
        metadata_text = ''.join(chr(i) for i in ascii_meta)
        ASCii = metadata_text.replace("\0", '')
        return ujson.loads(ASCii)

    def unpackMetadata(self):

        # TODO add implementation to search subfolders if the format is not the Velox default.

        try:
            metadata = self.singleH5pyObject[
                'Data/Image/' + navigate.getMemberName(self.singleH5pyObject, '/Data/Image/') + '/Metadata']
            transposed_meta = [list(i) for i in zip(*(metadata[:]))]
        except:
            raise ValueError("Metadata was not able to be read, see unpackMetadata function.")

        # Unpack metadata dictionaries.
        meta = {}
        nframes = metadata.shape[-1]
        for i in range(nframes):
            meta[i] = self.convertASCII(transposed_meta, i)

        return meta

    def unpackData(self):

        # TODO add implementation to search subfolders if the format is not the Velox default.

        try:
            data = self.singleH5pyObject[
                'Data/Image/' + navigate.getMemberName(self.singleH5pyObject, '/Data/Image/') + '/Data']
            data = np.array(data)
            return data

        except:
            raise ValueError("File was not able to be read, see unpackData function.")

    def parseEMDdata(self):
        """
        Returns
        -------
        tuple
            Returns a tuple with the contents: (data, add_kwargs, layer_type).
            data : image data.
            add_kwargs : metadata for each frame.
            layer_type : "image".
        """

        data = self.unpackData()
        # Shape single frame data by removing final channel.
        if data.shape[-1] == 1:
            data = data.reshape(data.shape[0], data.shape[1])
        # Shape multiple frame data with transpose.
        else:
            data = data[...].transpose()
            data = rotateFrame(data)

        add_kwargs = {'metadata': {'tag': 'emdfile', 'frames_metadata': self.unpackMetadata()}}

        layer_type = "image"  # optional, default is "image"

        return (data, add_kwargs, layer_type)


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".emd"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """

    # Assume that a list of strings are all separate files that wish to be opened.
    if isinstance(path, list):
        # Return a list of LayerData tuples if multiple files are opened.
        LayerDataList = []
        for file in path:
            LayerDataList.append(EMDreader(file).parseEMDdata())
        return LayerDataList
    else:
        # Return a single LayerData tuple.
        return [EMDreader(path).parseEMDdata()]
