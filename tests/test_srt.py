import unittest

from parameterized import parameterized
from py.srt import seconds_to_srt_timestamp

class TestSrt(unittest.TestCase):

    @parameterized.expand([
        [4,     "00:00:04,000"],
        [44,    "00:00:44,000"]
    ])
    def test_seconds_to_srt_timestamp(self, input, expected):
        self.assertEqual(seconds_to_srt_timestamp(input), expected)
