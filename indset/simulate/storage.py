# coding=utf-8
from collections import defaultdict


class ListMap(object):
    def __init__(self, size):
        self.size = tuple(size)
        self.width = size[0]
        self.height = size[1]

        self._x_offset = self.width / 2
        self._y_offset = self.height / 2

        # For this implementation, we use native python lists
        self._grid_array = [[None for _ in xrange(self.width + 1)] for _ in xrange(self.height + 1)]

    def __getitem__(self, key):
        if len(key) != 2 or type(key[0]) != int or type(key[1]) != int:
            raise KeyError("ListMap required 2d int coordinates")

        x = key[0] + self._x_offset
        y = key[1] + self._y_offset

        if x < 0 or y < 0:
            raise ValueError("Index out of bounds!")

        return self._grid_array[x][y]

    def __setitem__(self, key, value):
        if len(key) != 2 or type(key[0]) != int or type(key[1]) != int:
            raise KeyError("ListMap required 2d int coordinates")

        x = key[0] + self._x_offset
        y = key[1] + self._y_offset

        if x < 0 or y < 0:
            raise ValueError("Index out of bounds!")

        self._grid_array[x][y] = value

    def __delitem__(self, key):
        if len(key) != 2 or type(key[0]) != int or type(key[1]) != int:
            raise KeyError("ListMap required 2d int coordinates")

        x = key[0] + self._x_offset
        y = key[1] + self._y_offset

        if x < 0 or y < 0:
            raise ValueError("Index out of bounds!")

        self._grid_array[x][y] = None

class ClassBasedList(object):
    def __init__(self):
        self._particle_list = []
        self._particle_class_lists = defaultdict(list)

    def add(self, particle):
        if particle in self._particle_list:
            raise ValueError("This particle is already in the list.")

        self._particle_list.append(particle)
        self._particle_class_lists[type(particle)].append(particle)

    def remove(self, particle):
        if particle not in self._particle_list:
            raise ValueError("This particle is not in the list.")

        self._particle_list.remove(particle)
        self._particle_class_lists[type(particle)].remove(particle)

    def __contains__(self, item):
        return item in self._particle_list

    def get_all(self):
        return (x for x in self._particle_list)

    def get_by_class(self, klass):
        return (x for x in self._particle_class_lists[klass])

    def get_class_list_pairs(self):
        return self._particle_class_lists.iteritems()
