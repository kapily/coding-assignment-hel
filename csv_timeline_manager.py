"""
A timeline is a list of TimelineEntry objects sorted by time
(earliest to latest). Multiple files can be loaded into a single
timeline object.

Timeline should be in the following format on disk in a CSV file:

type (string), time (int), value (string)

Notes:
- time does not assume any dimensions, so it can represent any arbitrary integer dimension
(ie. epoch seconds, minutes, etc)
- time does NOT need to start from 0. all times are relative to each other
- a time CAN occur more than once
- there should be NO HEADER
- exactly 3 columns per row in the csv file
"""

import csv

NUMBER_OF_COLUMNS = 3  # there should always only be 3 columns as per our assumption

class TimelineEntry:
  def __init__(self, type_, time, value):
    assert(isinstance(type_, basestring))
    assert(isinstance(time, int))
    assert(isinstance(value, basestring))
    self.type = type_
    self.time = time
    self.value = value

  def __eq__(self, other):
    return self.type == other.type and self.time == other.time and self.value == other.value


class CSVTimelineManager:

  def __init__(self):
    self.timeline = []

  def load_timeline(self, csv_path):
    """
    loads the timeline file. multiple timelines can be imported
    but will not be in order
    """
    with open(csv_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      for row in reader:
        assert(len(row) == NUMBER_OF_COLUMNS)
        type_ = row[0]  # underscore after to not conflict with built-in type
        time = int(row[1].strip())
        value = row[2].strip()
        self.add_entry_without_sorting(TimelineEntry(type_, time, value))

    self.__sort_timeline()  # sort after adding all entries

  # returns editable version of the timeline
  def get_timeline(self):
    """
    Returns sorted list of TimelineEntries
    """
    return self.timeline

  def add_entry_without_sorting(self, entry):
    self.timeline.append(entry)

  def __sort_timeline(self):
    """ Sorts timeline by time"""
    self.timeline.sort(key=lambda elem: elem.time)

  def add_entry_with_sorting(self, entry):
    """Add entry. Sorts array after each entry. Don't use this function if you plan
    on adding a large number of entries."""
    self.add_entry_without_sorting(entry)
    self.__sort_timeline()

  def save_timeline(self, csv_path):
    with open(csv_path, 'w') as csvfile:
      csv_writer = csv.writer(csvfile)
      for entry in self.timeline:
        csv_writer.writerow((entry.type, entry.time, entry.value))
