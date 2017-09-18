from __future__ import division, print_function
import unittest

import datetime as dt

from BDProjects import datetime_to_float, float_to_datetime


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.now = dt.datetime.now()

    def test_default_config(self):
        dt_f = datetime_to_float(self.now)
        dt_t = float_to_datetime(dt_f)
        self.assertEqual(dt_t, self.now)
        with self.assertRaises(ValueError):
            float_to_datetime('not a number')
        self.assertIsNone(float_to_datetime(None))
        with self.assertRaises(ValueError):
            datetime_to_float('not a datetime')
