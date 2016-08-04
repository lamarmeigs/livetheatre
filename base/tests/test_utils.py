from django.test import TestCase

from base.utils import chunks


class ChunksTestCase(TestCase):
    def test_chunks(self):
        some_list = list(range(10))
        self.assertEqual(
            list(chunks(some_list, 2)),
            [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
        )
        self.assertEqual(
            list(chunks(some_list, 3)),
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        )
