import pickle
import sys
import unittest

from HLL import HyperLogLog
from random import randint

class TestAdd(unittest.TestCase):

    def setUp(self):
        self.hll = HyperLogLog(5)

    def test_add_string(self):
        try:
            self.hll.add('my string')
        except Exception as ex:
            self.fail('failed to add string: %s' % ex)

    @unittest.skipIf(sys.version_info[0] > 2, 'buffer is deprecated in python 3.x')
    def test_add_buffer(self):
        try:
            self.hll.add(buffer('asdf'))
        except Exception as ex:
            self.fail('failed to add buffer: %s' % ex)

    def test_add_bytes(self):
        try:
            self.hll.add(b'some bytes')
        except Exception as ex:
            self.fail('failed to add bytes: %s' % ex)

    def test_return_value_indicates_register_update(self):
        changed = self.hll.add('asdf')
        self.assertTrue(changed)
        changed = self.hll.add('asdf')
        self.assertFalse(changed)
        changed = self.hll.add('otherdata')
        self.assertTrue(changed)


class TestHyperLogLogConstructor(unittest.TestCase):

    def test_size_lower_bound(self):
        for i in range(-1, 2):
            with self.assertRaises(ValueError):
                HyperLogLog(i)

    def test_size_upper_bound(self):
        with self.assertRaises(ValueError):
            HyperLogLog(64)

    def test_registers_initialized_to_zero(self):
        hll = HyperLogLog(5)
        for i in range(hll.size()):
            self.assertEqual(hll._get_register(i), 0)

    def test_histogram_initialized_to_zero(self):
        hll = HyperLogLog(5)
        hist = hll._histogram()
        self.assertEqual(sum(hist), 0)

    def test_p_sets_size(self):
        for i in range(2, 6):
            hll = HyperLogLog(i)
            self.assertEqual(hll.size(), 2**i)

    def test_setting_a_seed(self):
        hll = HyperLogLog(5, seed=4)
        self.assertEqual(hll.seed(), 4)

        hll2 = HyperLogLog(5, seed=20000)
        self.assertNotEqual(hll.hash('test'), hll2.hash('test'))

class TestMerging(unittest.TestCase):

    def test_only_same_size_can_be_merged(self):
        hll = HyperLogLog(4)
        hll2 = HyperLogLog(5)
        with self.assertRaises(Exception):
            hll.merge(hll2)

    def test_merging(self):
        #expected = bytearray(4)
        #expected[0] = 1
        #expected[3] = 1

        hll = HyperLogLog(2)
        hll2 = HyperLogLog(2)

        #hll.set_register(0, 1)
        #hll2.set_register(3, 1)

        hll.merge(hll2)
        #self.assertEqual(hll.registers(), expected)

class TestPickling(unittest.TestCase):

    def setUp(self):
        hlls = [HyperLogLog(x, randint(1, 10**6)) for x in range(4, 16)]
        cardinalities = [x**5 for x in range(1, 16)]

        for hll, n in zip(hlls, cardinalities):
            for i in range(1, n):
                hll.add(str(i))
        self.hlls = hlls

    def test_pickled_cardinality(self):
        for hll in self.hlls:
            expected = hll.cardinality()
            hll2 = pickle.loads(pickle.dumps(hll))
            self.assertEqual(expected, hll2.cardinality())

    def test_pickled_seed(self):
        for hll in self.hlls:
            expected = hll.seed()
            hll2 = pickle.loads(pickle.dumps(hll))
            self.assertEqual(expected, hll2.seed())

    def test_pickled_register_histogram(self):
        for hll in self.hlls:
            expected = hll._histogram()
            hll2 = pickle.loads(pickle.dumps(hll))
            self.assertEqual(expected, hll2._histogram())

    def test_pickled_size(self):
         for hll in self.hlls:
            expected = hll.size()
            hll2 = pickle.loads(pickle.dumps(hll))
            self.assertEqual(expected, hll2.size())

if __name__ == '__main__':
    unittest.main()
