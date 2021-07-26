import unittest

from process_event.helpers import Helpers


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self._configurtion = {
            "configuration": ["body", "config"]
        }
        self._h = Helpers()

    def test_helpers(self):
        self._h.iterate_dictionary(dictionary=self._dict, key=self._configurtion)
