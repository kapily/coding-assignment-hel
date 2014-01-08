"""
Only checks for the edge case of missing the first and last
element in the csv file, and tests to see an entry in the
middle is present. Not thoroughly tested, but good enough
for the assignment.
"""

import unittest
from csv_timeline_manager import CSVTimelineManager

class TestCSVTimelineManager(unittest.TestCase):

  def setUp(self):
    pass

  def test_db_loading(self):
    ctm = CSVTimelineManager("test_timeline_manager_1.csv")
    timeline = ctm.get_timeline()

    ctm.save_timeline()



    # first line in the file:
    self.assertEqual(cdm.get_value('Banana cake, made with sugar'), 47)

    # random line in the file:
    self.assertEqual(cdm.get_value('Peach, average'), 42)

    # last line in the file:
    self.assertEqual(cdm.get_value('Honey, average'), 61)

if __name__ == '__main__':
  unittest.main()