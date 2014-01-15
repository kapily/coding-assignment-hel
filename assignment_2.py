"""
Assumptions:
- We have a list of the top 500 (in memory) which gets updated automatically
- The top 500 isn't updated very frequently (if it is, it will result in possible repetition
or expired data in our output)

Overview:
- Upon an initial request (with no state data or expired state data), the program stores the
 numbers 0 to 499 in a random order to the state. These numbers represent the indexes of the
 Users list. (note: this can be done entirely client-side so we don't waste bytes sending this
 list to the client. This list has an "expiration" time.
- The program then looks up the id's in the requested subset of that list. Again, the client
 in this example will send the entire list over. But in production, this logic of sending
 over only the id's required by the infinite scroll will be done by the client.

Note:
- For this assignment, I'm assuming the client passes the entire state to the server. In production,
we could have client-side js which only sends the id's with the correct amount and offset

"""

from random import shuffle

import time

SECONDS_TILL_EXPIRATION = 60
NUMBER_OF_TOP_USERS = 500
DIGITS_IN_NUMBER_OF_TOP_USERS = 3


class User:
  def __init__(self, user_id):
    # Adding leading 0's helps for testing because it puts them in correct order
    user_id_str = str(user_id)
    assert(len(user_id_str) <= DIGITS_IN_NUMBER_OF_TOP_USERS)
    if len(user_id_str) != DIGITS_IN_NUMBER_OF_TOP_USERS:
      user_id_str = '0' * (DIGITS_IN_NUMBER_OF_TOP_USERS - len(user_id_str)) + user_id_str


    self.id = "User" + user_id_str  # again just for testing
    self.rank = id  # rank == id, for test data

  def __str__(self):
    return self.id

class State:
  def __init__(self):
    self.random_ids = None  # must be set
    self.expires = 0  # By default, it's set to epoch


# the list of top 500 users. Assume it gets updated whenever the top 500 changes.
# for testing purposes, we just have id's from 0 to 499, but in production, we
# would have the actually id's of the users
top_500 = [User(i) for i in range(NUMBER_OF_TOP_USERS)]


def get_top_users(offset, limit, state):
  #returns an array of user ids that can be fetched from the database
  assert(isinstance(state, State))
  now = int(time.time())
  if now > state.expires:
    state.expires = now + SECONDS_TILL_EXPIRATION
    state.random_ids = range(NUMBER_OF_TOP_USERS)
    shuffle(state.random_ids)  # this logic can be done client-side

  # now we return the id's requested since it is stored in the state
  end = min(NUMBER_OF_TOP_USERS, offset + limit)  # make sure the last element is <= 499
  ids_requested = state.random_ids[offset:end]  # end is EXCLUSIVE
  result = []  # result is an array of User objects
  for id_requested in ids_requested:
    assert(id_requested >= 0)
    assert(id_requested < NUMBER_OF_TOP_USERS)
    result.append(top_500[id_requested])
  return result

