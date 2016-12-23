# Priority queue with drop() operation. The code is based on the sample from
# https://docs.python.org/3/library/heapq.html
from heapq import heappush, heappop


class PQueue:
    def __init__(self):
        self.__heap__ = list()
        self.__entry_finder__ = dict()
        self.__next_index__ = 0

    def put(self, t, value):
        index = self.__next_index__
        self.__next_index__ += 1
        entry = [t, index, value, False]  # time, index, event, dropped - the last one indicates whether
                                          # the entry was dropped
        self.__entry_finder__[index] = entry
        heappush(self.__heap__, entry)
        return index

    def drop(self, index):
        if index is not None and self.__entry_finder__.get(index) is not None:
            entry = self.__entry_finder__.pop(index)
            entry[-1] = True

    def drop_all_by(self, check):
        for index, entry in self.__entry_finder__.items():
            if check(entry[2]):
                entry[-1] = True

    def get(self):
        while self.__heap__:
            t, index, value, dropped = heappop(self.__heap__)
            if not dropped:
                del self.__entry_finder__[index]
                return t, index, value
        raise KeyError('pop from an empty priority queue')

    def empty(self):
        return len(self.__entry_finder__) == 0
