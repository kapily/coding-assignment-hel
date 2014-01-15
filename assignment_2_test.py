
import unittest

from assignment_2 import get_top_users
from assignment_2 import User
from assignment_2 import State
from assignment_2 import NUMBER_OF_TOP_USERS

class InfiniteScrollTest(unittest.TestCase):

  def setUp(self):
    pass

  def testRandomListHasUniqueElements(self):
    """
    Request all of the users (for test purposes, we will create User001 ... User500) and
    sort the list, and check to see that all of the users are present. This means that the
    randomized list contains all unique elements.
    """
    state = State()
    a = get_top_users(0, NUMBER_OF_TOP_USERS, state)
    users_str_list = [str(x) for x in a]
    users_str_list.sort()
    self.assertEquals(len(set(users_str_list)), NUMBER_OF_TOP_USERS)

    # Check to see all of the users expected are present
    all_users = [User(x) for x in range(NUMBER_OF_TOP_USERS)]
    all_users_str_list = [str(x) for x in all_users]
    self.assertEquals(users_str_list, all_users_str_list)

if __name__ == '__main__':
  unittest.main()