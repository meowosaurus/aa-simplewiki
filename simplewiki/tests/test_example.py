"""
simplewiki Test
"""

# Django
from django.test import TestCase


class Testsimplewiki(TestCase):
    """
    Testsimplewiki
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Test setup
        :return:
        :rtype:
        """

        super().setUpClass()

    def test_simplewiki(self):
        """
        Dummy test function
        :return:
        :rtype:
        """

        self.assertEqual(True, True)
