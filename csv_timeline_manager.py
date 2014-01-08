"""
Timeline should be in the following format:

type, time, value

Assumptions
- time is an int (ie. seconds from epoch). It does not assume any dimensions
- time does NOT need to start from 0. all times are relative to eachother
- value must be a string
- there should be NO HEADER
- only 3 columns per row
- CSVTimelineManager does NOT sort the values. That functionality can be
added in later, but is not necessary for this assignment
"""

import csv

NUMBER_OF_COLUMNS = 3  # there should always only be 3 columns as per our assumption

class TimelineEntry:
  def __init__(self, type, time, value):
    self.type = type
    self.time = time
    self.value = value

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
        self.timeline.append(TimelineEntry(type_, time, value))

    # TODO: sort the timeline

  # returns editable version of the timeline
  def get_timeline(self):
    """
    Returns sorted list of TimelineEntries
    """
    return self.timeline

  def add_entry(self, entry):
    # TODO: add a timeline entry to the timeline
    pass

  def save_timeline(self, csv_path):
    with open(csv_path) as csvfile:
      csv_writer = csv.writer(csvfile)
      for entry in self.timeline:
        csv_writer.writerow((entry.type, entry.time, entry.value))
