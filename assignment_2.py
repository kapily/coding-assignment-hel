"""
Assumptions:
- We have a list of the top 500 (in memory) which gets updated automatically
- The top 500 isn't updated very frequently (if it is, it will result in possible repetition
or expired data in our output)

Overview:
- Upon an initial request (with no state data or expired state data), the program stores the id's
of the top 500 users in a random order in the client's state (note, we could also do the randomization
 client side)
- The program then looks up the id's in the requested subset of that list.


"""

# the list of top 500 users. Assume it gets updated whenever the top 500 changes.
top_500 = []

