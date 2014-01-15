"""
Input:
- food inputs
- excercise inputs
Output:
- graph of blood sugar over the course of day
- graph of glycation that occured over the day

- time is time in minutes (not necesarilly minute offset)

Assumptions:
- The list of food and exercises with a timestamp is in order (earliest to latest)
- Excercise won't send blood sugar into negatives (too much excercise)
"""

from csv_timeline_manager import CSVTimelineManager
from csv_database_manager import CSVDatabaseManager

MINUTES_AFTER_LAST_EVENT = 240  # arbitrary for now. How long timeline should be active after last event
EXERCISE_DURATION = 60
FOOD_DURATION = 120
BASELINE_BLOOD_SUGAR = 80
GLYCATION_THRESHOLD = 150

class Delta:
  def __init__(self, delta):
    self.delta = delta

class Influencer:
  def __init__(self, per_minute_change, time_remaining):
    self.per_minute_change = per_minute_change
    self.time_remaining = time_remaining

class BloodSugarSimulator:
  def __init__(self, food_db_manager, exercise_db_manager, input_timeline):

    self.food_db_manager = food_db_manager
    self.exercise_db_manager = exercise_db_manager
    self.input_timeline = input_timeline

    # input is minutes
    self.start_time = input_timeline[0].time
    self.end_time = input_timeline[-1].time

    output_timeline_size = self.end_time - self.start_time + 1 + MINUTES_AFTER_LAST_EVENT
    self.output_timeline_list = [None] * output_timeline_size
    self.glycation = 0

    #self.last_food_time = float("-inf")
    #self.last_exercise_time = float("-inf")

    self.has_run = False

  @staticmethod
  def eligible_for_normalization(current_time_normalized, last_food_time, last_exercise_time):
    return ((current_time_normalized - last_food_time) >= FOOD_DURATION and
            (current_time_normalized - last_exercise_time) >= EXERCISE_DURATION)

  def normalize_blood_sugar(self, previous_blood_sugar, current_time_normalized):
    if previous_blood_sugar > BASELINE_BLOOD_SUGAR + 1:
      self.output_timeline_list[current_time_normalized] = previous_blood_sugar - 1
    elif previous_blood_sugar < BASELINE_BLOOD_SUGAR - 1:
      self.output_timeline_list[current_time_normalized] = previous_blood_sugar + 1
    elif previous_blood_sugar >= (BASELINE_BLOOD_SUGAR - 1) or previous_blood_sugar <= (BASELINE_BLOOD_SUGAR + 1):
      self.output_timeline_list[current_time_normalized] = BASELINE_BLOOD_SUGAR
    else:
      self.output_timeline_list[current_time_normalized] = previous_blood_sugar
    return

  def run(self):
    assert(self.has_run is False)  # Should only be run once

    selflast_food_time = float("-inf")
    selflast_exercise_time = float("inf")
    input_timeline_index = 0  # the pointer for start of timeline events which might be "active"

    # At a high level, we want to iterate through each minute in between the first and last entry and
    # update the scores during that time. This is not efficient for sparse inputs. Also, we may
    # run out of memory for really large timelines

    # current_time_normalized means that it just starts from 0 index. We add 1 because beginning and end
    # are inclusive. We add MINUTES_AFTER_LAST_EVENT to account for the last entry.

    previous_score = BASELINE_BLOOD_SUGAR
    for current_time_normalized in xrange((self.end_time - self.start_time + 1) + MINUTES_AFTER_LAST_EVENT):
      assert(isinstance(self.output_timeline_list[current_time_normalized], Delta) or
             self.output_timeline_list[current_time_normalized] is None)

      # Loop to add all the factors that occur at this current time (because you might eat multiple things the same
      # minute, etc)

      while input_timeline_index < len(self.input_timeline) and (self.input_timeline[input_timeline_index].time - self.start_time) == current_time_normalized:

        current_element = self.input_timeline[input_timeline_index]


        # bs = blood sugar
        bs_change_per_min = None
        bs_duration = None
        if current_element.type == "food":
          score = self.food_db_manager.get_value(current_element.value)
          bs_change_per_min = float(score) / FOOD_DURATION
          selflast_food_time = current_time_normalized
          bs_duration = FOOD_DURATION
        elif current_element.type == "exercise":
          score = self.exercise_db_manager.get_value(current_element.value)
          bs_change_per_min = -1 * float(score) / EXERCISE_DURATION  # multiple by negative 1 because it brings down sugar
          selflast_exercise_time = current_time_normalized
          bs_duration = EXERCISE_DURATION


        assert(isinstance(bs_change_per_min, float))

        # Update all of the following blood sugars
        for i in xrange(current_time_normalized, current_time_normalized + bs_duration):
          # First element can never be None and the previous element must have
          # been filled in
          if self.output_timeline_list[i] is None:
            self.output_timeline_list[i] = Delta(bs_change_per_min)
          else:
            assert(isinstance(self.output_timeline_list[i], Delta))
            self.output_timeline_list[i].delta += bs_change_per_min
        # advance the index we look look for entries
        input_timeline_index += 1

      if isinstance(self.output_timeline_list[current_time_normalized], Delta):
        self.output_timeline_list[current_time_normalized] = previous_score + self.output_timeline_list[current_time_normalized].delta

      # adjust blood sugar after 120 and 60 minutes, respectively
      # => because it's (inclusive, exclusive)
      if BloodSugarSimulator.eligible_for_normalization(current_time_normalized, selflast_food_time, selflast_exercise_time):
        assert(self.output_timeline_list[current_time_normalized] is None)
        assert(self.output_timeline_list[current_time_normalized - 1] is not None)  # the previous entry cannot be None
        assert(current_time_normalized != 0)
        previous_blood_sugar = self.output_timeline_list[current_time_normalized - 1]

        # we first set the current blood sugar to the previous minute's blood sugar and adjust by
        # 1 to approach 80
        self.normalize_blood_sugar(previous_blood_sugar, current_time_normalized)

      # by this point, the blood sugar for the current time would have been filled
      assert(self.output_timeline_list[current_time_normalized] is not None)

      if self.output_timeline_list[current_time_normalized] > GLYCATION_THRESHOLD:
        self.glycation += 1

      previous_score = self.output_timeline_list[current_time_normalized]

    self.has_run = True

  def print_results(self):

    print "glycation = ", self.glycation
    print "timeline: "
    for idx, val in enumerate(self.output_timeline_list[1:]):
      # time, sugar value
      print idx + self.start_time, round(self.output_timeline_list[idx], 2)
      pass


def main():
  food_db_manager = CSVDatabaseManager("food_db.csv")
  exercise_db_manager = CSVDatabaseManager("excercise_db.csv")
  input_timeline_manager = CSVTimelineManager()
  input_timeline_manager.load_timeline("test_case_1.csv")
  # output_timeline_manager = CSVTimelineManager()
  # TODO: import all of the things into the timeline

  input_timeline = input_timeline_manager.get_timeline()
  bss = BloodSugarSimulator(food_db_manager, exercise_db_manager, input_timeline)
  bss.run()
  bss.print_results()

if __name__ == "__main__":
  main()