import unittest
import numpy as np
from napari_emd._reader import EMDreader, rotateFrame, reader_function
from napari_emd._tests.test_data.metadata import *

multiple_frame_test = 'test_data/MultipleFrameTestData.emd'
single_frame_test = 'test_data/SingleFrameTestData.emd'

test_files = [multiple_frame_test, single_frame_test]

test_file_metadata = [test_metadata_multiframe, test_metadata_singleframe]

test_file_metadata_raw = [(1024, 1024, 23), (2048, 2048, 1)]


class TestEMDReader(unittest.TestCase):

    def test_convertASCII(self):
        # Test the convertASCII method
        emd_reader = EMDreader("")
        converted1 = emd_reader.convertASCII(test_metadata_ascii, 0)
        converted2 = emd_reader.convertASCII(test_metadata_ascii, 1)
        self.assertDictEqual(converted1, {'fruit': 'Apple', 'size': 'Large', 'color': 'Red'})
        self.assertDictEqual(converted2,
                             {'quiz': {'sport': {'q1': {'question': 'Which one is correct team name in NBA?',
                                                        'options': ['New York Bulls', 'Los Angeles Kings',
                                                                    'Golden State Warriros', 'Huston Rocket'],
                                                        'answer': 'Huston Rocket'}}, 'maths': {
                                 'q1': {'question': '5 + 7 = ?', 'options': ['10', '11', '12', '13'], 'answer': '12'},
                                 'q2': {'question': '12 - 8 = ?', 'options': ['1', '2', '3', '4'], 'answer': '4'}}}})

    def test_unpackMetadata(self):
        # Test the unpackMetadata method
        for i in [0, 1]:
            emd_reader = EMDreader(test_files[i])
            metadata = emd_reader.unpackMetadata()
            self.assertDictEqual(metadata, test_file_metadata[i])

    def test_unpackData(self):
        # Test the unpackData method
        for i in [0, 1]:
            emd_reader = EMDreader(test_files[i])
            data = emd_reader.unpackData()
            self.assertEqual(data.shape, test_file_metadata_raw[i])

    def test_parseEMDdata(self):
        # Test the parseEMDdata method
        for i in [0, 1]:
            emd_reader = EMDreader(test_files[i])
            data, add_kwargs, layer_type = emd_reader.parseEMDdata()
            self.assertIsInstance(data, np.ndarray)
            self.assertIsInstance(add_kwargs, dict)
            self.assertIsInstance(layer_type, str)


class TestRotateFrame(unittest.TestCase):

    def test_rotateFrame(self):
        # Test the rotateFrame function
        data = np.array([[[2, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
                         [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]])
        rotated_data = rotateFrame(data)
        self.assertEqual(rotated_data.tolist(), [[[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [2, 1, 1, 1]],
                                                 [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0]]])


if __name__ == '__main__':
    unittest.main()
