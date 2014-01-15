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




# the list of top 500 users. Assume it gets updated whenever the top 500 changes.
# for testing purposes, we just have id's from 0 to 499, but in production, we
# would have the actually id's of the users
top_500 = range(500)

def get_top_users(offset, limit, state):
  #returns an array of user ids that can be fetched from the database
get_top_user_ids(0,5, list_id) #returns the top 5 user ids
get_top_user_ids(5,5, list_id) #returns the next ‘page’, ranks 5-9, using the same list id ensure we have the same random ordering as with the previous call so there are no repeats


