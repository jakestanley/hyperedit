import unittest

from parameterized import parameterized
from py.srt import seconds_to_srt_timestamp, deaggress

class TestSrt(unittest.TestCase):

    @parameterized.expand([
        [4,     "00:00:04,000"],
        [44,    "00:00:44,000"]
    ])
    def test_seconds_to_srt_timestamp(self, input, expected):
        self.assertEqual(seconds_to_srt_timestamp(input), expected)

    @parameterized.expand([
        [[('1', 4.32, 6.605)], 0.5, [('1', 3.82, 7.105)]],
    ])
    def test_deaggress(self, input_time, input_seconds, expected):
        self.assertEqual(deaggress(input_time, input_seconds), expected)
