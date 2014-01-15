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

MINUTES_BUFFER_AFTER_LAST_EVENT = 240  # arbitrary for now. How long timeline should be active after last event
EXERCISE_DURATION = 60
FOOD_DURATION = 120
BASELINE_BLOOD_SUGAR = 80.0
GLYCATION_THRESHOLD = 150
FOOD_EVENT = "food"
EXERCISE_EVENT = "exercise"

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

    self.start_time = input_timeline[0].time
    self.end_time = input_timeline[-1].time

    output_timeline_size = self.end_time - self.start_time + 1 + MINUTES_BUFFER_AFTER_LAST_EVENT
    self.output_timeline_list = [None] * output_timeline_size
    self.glycation = 0

    self.last_food_time = float("-inf")
    self.last_exercise_time = float("-inf")

    self.has_run = False

  @staticmethod
  def eligible_for_normalization(t, last_food_time, last_exercise_time):
    return ((t - last_food_time) >= FOOD_DURATION and
            (t - last_exercise_time) >= EXERCISE_DURATION)

  def normalize_blood_sugar(self, previous_blood_sugar, t):
    """
    Normalize blood sugar (ie. bring it up / down to 80)
    We first set the current blood sugar to the previous minute's blood sugar and adjust by
    1 to approach 80
    """
    if previous_blood_sugar > BASELINE_BLOOD_SUGAR + 1:
      self.output_timeline_list[t] = previous_blood_sugar - 1
    elif previous_blood_sugar < BASELINE_BLOOD_SUGAR - 1:
      self.output_timeline_list[t] = previous_blood_sugar + 1
    elif previous_blood_sugar >= (BASELINE_BLOOD_SUGAR - 1) or previous_blood_sugar <= (BASELINE_BLOOD_SUGAR + 1):
      self.output_timeline_list[t] = BASELINE_BLOOD_SUGAR
    else:
      self.output_timeline_list[t] = previous_blood_sugar
    return

  def calculate_blood_sugar_change(self, event, t):
    """
    Given an event (exercise or food), determine the blood sugar change per minute
    and the duration of the change
    """
    bs_change_per_min = None
    event_duration = None
    if event.type == FOOD_EVENT:
      score = self.food_db_manager.get_value(event.value)
      bs_change_per_min = float(score) / FOOD_DURATION
      self.last_food_time = t
      event_duration = FOOD_DURATION
    elif event.type == EXERCISE_EVENT:
      score = self.exercise_db_manager.get_value(event.value)
      bs_change_per_min = -1 * float(score) / EXERCISE_DURATION  # multiple by negative 1 because it brings down sugar
      self.last_exercise_time = t
      event_duration = EXERCISE_DURATION
    return bs_change_per_min, event_duration

  @staticmethod
  def index_within_bounds(idx, l):
    assert(idx >= 0)
    return idx < len(l)

  @staticmethod
  def get_normalized_time(current_time, start_time):
    return current_time - start_time

  @staticmethod
  def minutes_between_start_and_end(start, end):
    """ Minutes between start and end, inclusive"""
    return end - start

  def run(self):
    assert(self.has_run is False)  # Should only be run once
    # At a high level, we want to iterate through each minute in between the first and last entry in
    # the timeline of events and update the scores during that time. This is not efficient for sparse
    # inputs. Also, we may run out of memory for really large timelines

    # t = the current normalized time
    # current normalized time means that it just starts from 0 index. For example, if start_time = minutes
    # after epoch, say 13897699, then it would be a waste to store all the seconds between 0 and
    # 13897699. Thus, we set "13897699" to be equivalent to 0 in our timeline, and count up from
    # there.

    # We add MINUTES_AFTER_LAST_EVENT to account for the minutes after the last entry.

    event_timeline_index = 0  # the pointer for start of timeline events which might be "active"

    previous_blood_sugar = BASELINE_BLOOD_SUGAR

    for t in xrange(self.minutes_between_start_and_end(self.start_time, self.end_time) + MINUTES_BUFFER_AFTER_LAST_EVENT):
      # An event is defined as either exercise or food.
      # The output_timeline contains an float for past events (before t). That integer represents a computed
      # and final value.
      assert(isinstance(previous_blood_sugar, float))
      # For current and future events, the output_timeline could be either None (no events have affected it)
      # or it could be a Delta object (some event has already affected it). Check to see that is the case.
      assert(isinstance(self.output_timeline_list[t], Delta) or self.output_timeline_list[t] is None)

      # Loop to add all the events that occur at the current time. There may be more than one at a given time
      # (because you might eat multiple things the same minute or eat and exercise). That's why we use
      # a while loop.
      while (self.index_within_bounds(event_timeline_index, self.input_timeline) and
             self.get_normalized_time(self.input_timeline[event_timeline_index].time, self.start_time) == t):
        current_event = self.input_timeline[event_timeline_index]

        blood_sugar_change_per_min, event_duration = self.calculate_blood_sugar_change(current_event, t)
        assert(isinstance(blood_sugar_change_per_min, float))

        # Update all of the following blood sugars (time Delta's) for the next 60-120 mins
        for i in xrange(t, t + event_duration):
          # First element can never be None and the previous element must have
          # been filled in
          if self.output_timeline_list[i] is None:
            self.output_timeline_list[i] = Delta(blood_sugar_change_per_min)
          else:
            assert(isinstance(self.output_timeline_list[i], Delta))
            self.output_timeline_list[i].delta += blood_sugar_change_per_min
        # advance the event_timeline index we look look for entries
        event_timeline_index += 1

      # If the current element in the output in a Delta object, then add the delta to the
      # previous value in the timeline
      if isinstance(self.output_timeline_list[t], Delta):
        self.output_timeline_list[t] = previous_blood_sugar + self.output_timeline_list[t].delta

      # adjust blood sugar after 120 and 60 minutes, respectively
      # => because it's (inclusive, exclusive)
      if BloodSugarSimulator.eligible_for_normalization(t, self.last_food_time, self.last_exercise_time):
        assert(self.output_timeline_list[t] is None)  # if bs is normalizing, it means there shouldn't be a Delta object
        self.normalize_blood_sugar(previous_blood_sugar, t)

      # by this point, the blood sugar for the current time would have been filled
      assert(isinstance(self.output_timeline_list[t], float))

      # Check for glycation
      if self.output_timeline_list[t] > GLYCATION_THRESHOLD:
        self.glycation += 1

      # before the next iteration, set the previous blood sugar
      previous_blood_sugar = self.output_timeline_list[t]

    self.has_run = True

  def print_results(self):
    print "glycation = ", self.glycation
    print "timeline: "
    for idx, val in enumerate(self.output_timeline_list[1:]):
      # time, sugar value
      print idx + self.start_time, round(self.output_timeline_list[idx], 2)

def main():
  food_db_manager = CSVDatabaseManager("food_db.csv")
  exercise_db_manager = CSVDatabaseManager("excercise_db.csv")
  input_timeline_manager = CSVTimelineManager()

  # NOTE: you can change "test_case_1.csv" below to your own input file to run
  # it on your own input.
  input_timeline_manager.load_timeline("test_case_1.csv")

  input_timeline = input_timeline_manager.get_timeline()
  bss = BloodSugarSimulator(food_db_manager, exercise_db_manager, input_timeline)
  bss.run()
  bss.print_results()

if __name__ == "__main__":
  main()