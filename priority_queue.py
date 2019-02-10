import heapq
from queue import Queue


class TSPriorityQueue(Queue):
    """A Queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first.
    If order is 'min', the item with minimum f(x) is
    returned first; if order is 'max', then it is the item with maximum f(x).
    Also supports dict-like lookup."""

    def set_f(self, f):
        self.f = f

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        """Insert item at its correct position."""
        heapq.heappush(self.queue, (self.f(item), item))

    def _get(self):
        """Pop and return the item (with min or max f(x) value
        depending on the order."""
        if self.queue:
            return heapq.heappop(self.queue)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def __len__(self):
        """Return current capacity of PriorityQueue."""
        return len(self.queue)

    def __contains__(self, item):
        """Return True if item in PriorityQueue."""
        return (self.f(item), item) in self.queue

    def __getitem__(self, key):
        for _, item in self.queue:
            if item == key:
                return item

    def __delitem__(self, key):
        """Delete the first occurrence of key."""
        self.queue.remove((self.f(key), key))
        heapq.heapify(self.queue)

    def __repr__(self):
        return str(self.queue)