from os import getenv
from typing import Type
from types import FunctionType
from vcr_unittest import VCRTestCase
from canonicalwebteam.retry_utils import delay_random, delay_exponential


class RetryHelpersTest(VCRTestCase):
    def test_delay_random(self):
        delay = delay_random(0.0, 1.0)
        self.assertIsInstance(delay, FunctionType)
        self.assertTrue(0.0 <= delay(0) <= 1.0)

    def test_delay_random_bad_min(self):
        with self.assertRaises(ValueError):
            delay = delay_random(-1.0, 1.0)

    def test_delay_random_bad_max(self):
        with self.assertRaises(ValueError):
            delay = delay_random(1.0, 1.0)

    def test_delay_exp(self):
        delay = delay_exponential(1.0, 2.0, 8.0)
        self.assertIsInstance(delay, FunctionType)
        self.assertEqual(delay(1), 2.0**1)
        self.assertEqual(delay(2), 2.0**2)
        self.assertEqual(delay(3), 2.0**3)
        self.assertEqual(delay(4), 2.0**3)

    def test_delay_exp_bad_mult(self):
        with self.assertRaises(ValueError):
            delay = delay_exponential(-1.0, 2.0, 8.0)

    def test_delay_exp_bad_base(self):
        with self.assertRaises(ValueError):
            delay = delay_exponential(1.0, 0.1, 8.0)

    def test_delay_exp_bad_max(self):
        with self.assertRaises(ValueError):
            delay = delay_exponential(1.0, 0.1, -8.0)
