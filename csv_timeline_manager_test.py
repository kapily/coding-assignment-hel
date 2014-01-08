"""
Only checks for the edge case of missing the first and last
element in the csv file, and tests to see an entry in the
middle is present. Not thoroughly tested, but good enough
for the assignment.
"""

import unittest
from csv_timeline_manager import CSVTimelineManager
from csv_timeline_manager import TimelineEntry

class TestCSVTimelineManager(unittest.TestCase):

  def setUp(self):
    pass

  def test_db_loading(self):
    """
    This test saves TimelineEntries into a file and then opens them and checks to see that they all exist.
    Test case is small currently.
    """
    ctm_writer = CSVTimelineManager()
    input_entries = [TimelineEntry('type1', 12, 'v2'), TimelineEntry('type2', 2, 'v42'), TimelineEntry('type1', 5, 'v4'),
                     TimelineEntry('type1', 3, 'v424'), TimelineEntry('type2', 15, 'v432'), TimelineEntry('type2', 4, 'v4215')
                     ]
    for entry in input_entries:
      ctm_writer.add_entry(entry)

    # timeline = ctm.get_timeline()
    ctm_writer.save_timeline("test_timeline_manager_1.csv")

    # output entries will be sorted
    output_entries = sorted(input_entries, key=lambda e: e.time)
    ctm_reader = CSVTimelineManager()
    ctm_reader.load_timeline("test_timeline_manager_1.csv")
    self.assertEquals(output_entries, ctm_reader.get_timeline())


if __name__ == '__main__':
  unittest.main()