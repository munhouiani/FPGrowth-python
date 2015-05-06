__author__ = 'mhwong'

# This is a FPTree Structure Class


class FPTree:

    def __init__(self, item):
        # to check if the node is root
        self.root = False

        # the holding item
        self.item = item

        # the node's children
        self.children = []

        # the frequency of the holding item
        self.count = 0

        # parent node
        self.parent = None

        # the next connect node, used in header table
        self.next = None

    def is_root(self):
        return self.root