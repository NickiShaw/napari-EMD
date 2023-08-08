import unittest
import numpy as np
from napari_emd._reader import EMDreader, rotateFrame
from napari_emd._tests.test_data.metadata import *

multiple_frame_test = 'src/napari_emd/_tests/test_data/MultipleFrameTestData.emd'
single_frame_test = 'src/napari_emd/_tests/test_data/SingleFrameTestData.emd'

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
        data = np.array([[[1,2,3,4], [5,6,7,8], [9,10,11,12], [13,14,15,16]],
                         [[17,18,19,20], [21,22,23,24], [25,26,27,28], [29,30,31,32]]])
        rotated_data = rotateFrame(data)
        self.assertEqual(rotated_data.tolist(), [[[1,5,9,13],[2,6,10,14],[3,7,11,15],[4,8,12,16]],
                                                 [[17,21,25,29],[18,22,26,30],[19,23,27,31],[20,24,28,32]]])


if __name__ == '__main__':
    unittest.main()
