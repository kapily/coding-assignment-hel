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

class Influencer:
  def __init__(self, per_minute_change, time_remaining):
    self.per_minute_change = per_minute_change
    self.time_remaining = time_remaining


class BloodSugarSimulator:
  def __init__(self, food_db_manager, exercise_db_manager, input_timeline, output_timeline):

    # The active_influencers list is a list of "active" food or excercises effects
    # on the body in this format:
    active_influencers = []
    previous_time = None
    # previous_time = input_timeline.get_timeline()[0].time

    # input is minutes

    start_time = input_timeline[0].time
    end_time = input_timeline[-1].time

    output_timeline_size = end_time - start_time + 1
    output_timeline_list = [None] * output_timeline_size
    output_timeline_list[0] = 80  # starts out at 80

    input_timeline_index = 0  # the pointer for start of timeline events which might be "active"

    last_food_time = -Inf
    last_exercise_time = -Inf

    glycation = 0

    # At a high level, we want to iterate through each minute in between the first and last entry and
    # update the scores during that time. This is not efficient for sparse inputs. Also, we may
    # run out of memory for really large timelines
    for current_time in xrange(start_time, end_time + 1 + MINUTES_AFTER_LAST_EVENT):
      current_time_index = current_time - start_time
      #
      # set current score to previous score

      # output_timeline_list

      # Loop to add all the factors that occur at this current time (because you might eat multiple things the same
      # minute, etc)
      while input_timeline_index < len(input_timeline) and input_timeline[input_timeline_index].time == current_time:

        # TODO: process the input item here

        current_element = input_timeline[input_timeline_index]
        bs_change_per_min = None
        if current_element.type == "food":
          bs_change_per_min = current_element.value / 120
        else if current_element.type == "exercise":
          bs_change_per_min = current_element.value / 60

        last_food_time = current_time
        # TODO: increment the blood sugar for the next couple minutes
        bs_change_per_min = current_element.value / 120
        output_timeline_list[i] += bs_change_per_min

        # Update all of the following blood sugars
        # last_blood_sugar = output_timeline_list[cur]
        for i in xrange(current_time, current_time + 120):
          # First element can never be None and the previous element must have
          # been filled in
          if output_timeline_list[i] is None:
            output_timeline_list[i] = output_timeline_list[i - 1]
          output_timeline_list[i] += bs_change_per_min

        # advance the index we look look for entries
        input_timeline_index += 1

      # adjust blood sugar after 120 and 60 minutes, respectively
      if (current_time - last_food_time) > 120 and (current_time - last_exercise_time) > 60:
        previous_blood_sugar = output_timeline_list[current_time]

        # we first set the current blood sugar to the previous minute's blood sugar and adjust by
        # 1 to approach 80
        if output_timeline_list[current_time_index] > 80:
          input_timeline[current_time] = previous_blood_sugar - 1
        if output_timeline_list[current_time_index] < 80:
          input_timeline[current_time] = previous_blood_sugar + 1

      # by this point, the blood sugar for the current time would have been filled
      if output_timeline_list[current_time_index] > 150:
        glycation += 1


      active_excercise = False
      active_food = False

      # check for glycation


    # to lookup a time time_to_lookup in timeline, use to find the appropriate index:
    # timeline[time_to_lookup - start_time]

    # in xrange(start_min, end_min + 1):




    for entry in input_timeline:
      now_time = entry.time

      if active_influencers:
        # copy all the influences from the previous_time (exclusive) to now_time (inclusive)

      per_minute_change = None
      if entry.type == "excercise":
        per_minute_change = exercise_db_manager[entry.value]

      if entry.type == "food":
        per_minute_change = food_db_manager[entry.value] * -1



    # edge case: get the last one
    end_time = input_timeline.get_timeline()[-1].time



def main():
  food_db_manager = CSVDatabaseManager("food_db.csv")
  exercise_db_manager = CSVDatabaseManager("excercise_db.csv")
  input_timeline_manager = CSVTimelineManager()
  output_timeline_manager = CSVTimelineManager()
  # TODO: import all of the things into the timeline

  input_timeline = input_timeline_manager.get_timeline()
  bss = BloodSugarSimulator(food_db_manager, exercise_db_manager, input_timeline, output_timeline_manager)


if __name__ == "__main__":
  main()