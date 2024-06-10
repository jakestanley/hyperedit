import unittest

from parameterized import parameterized
from hyperedit.srt import seconds_to_srt_timestamp, deaggress_ranges_by_seconds

class TestSrt(unittest.TestCase):

    @parameterized.expand([
        [4,     "00:00:04,000"],
        [44,    "00:00:44,000"]
    ])
    def test_seconds_to_srt_timestamp(self, input, expected):
        self.assertEqual(seconds_to_srt_timestamp(input), expected)

    @parameterized.expand([
        [[('1', 4.32, 6.605)], 0.5, 
         [('1', 3.82, 6.855)]],
    ])
    def test_deaggress(self, input_time, input_seconds, expected):
        # end seconds is always halved input seconds so it doesn't overlap with next
        actual = deaggress_ranges_by_seconds(input_time, input_seconds)
        # assert ID (string)
        self.assertEqual(actual[0][0], expected[0][0])
        # assert start and end times (floats)
        self.assertAlmostEqual(actual[0][1], expected[0][1])
        self.assertAlmostEqual(actual[0][2], expected[0][2])
