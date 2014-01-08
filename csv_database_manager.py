"""
This class reads a CSV database of the following format:

id, key, value

Assumptions:
- 3 and only 3 columns can be used
- the first row will be ignored (used for labels)
- keys are unique (second column)
- values are integers
"""

import csv

NUMBER_OF_COLUMNS = 3  # there should always only be 3 columns as per our assumption

class CSVDatabaseManager:
  def __init__(self, csv_path):
    # TODO: open file at that path and load stuff into values
    self.key_to_value = {}
    with open(csv_path, 'r') as csvfile:
      next(csvfile)  # skip the first line
      reader = csv.reader(csvfile)
      for row in reader:
        assert(len(row) == NUMBER_OF_COLUMNS)  # there should always only be 3 columns as per our assumption
        id = int(row[0].strip())  # right now, we don't need the id
        key = row[1].strip()
        value = int(row[2].strip())
        self.key_to_value[key] = value

  def get_value(self, key):
    return self.key_to_value[key]