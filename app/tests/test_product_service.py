import unittest
import random

from common.di_container import product_service


class TestProductService(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_product(self):
        code = random.randint
        # product_service.create_product('ru', code)

