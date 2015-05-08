from collections import OrderedDict
from itertools import chain, combinations
import re

__author__ = 'mhwong'
from classes.FPTree import FPTree


def build_power_set(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))


class FPGrowth:
    def __init__(self, _input, _minsup, _minconf):
        # the threshold value
        self.threshold = 0

        # header table and fp tree
        self.header_table = []
        self.fpTree = None

        # the minimum confidence
        self.minconf = _minconf

        items_map_to_frequencies = {}
        sorted_items_by_frequencies = []
        items_to_remove = []

        self.build_item_list(_input, items_map_to_frequencies, sorted_items_by_frequencies, items_to_remove, _minsup)

        # build fp tree
        self.build_fp_tree(_input, items_map_to_frequencies, sorted_items_by_frequencies, items_to_remove)

        # perform fp growth
        self.frequent_patterns = dict()
        self.fp_growth(None, self.threshold, self.header_table, self.frequent_patterns)

        # frequent patterns sorted by key
        self.frequent_patterns = OrderedDict(sorted(self.frequent_patterns.items(), key=lambda t: t[0]))

        # print result
        self.print_fp()

        # generate rules
        self.generating_rules()

    def build_item_list(self, _input, items_map_to_frequencies, sorted_items_by_frequencies, items_to_remove, _minsup):
        with open(_input) as input_file:
            trans = 0
            for input_line in input_file:
                trans += 1
                token_list = re.split(r'[\s,\r\n]+', input_line)
                # filter empty string
                token_list = filter(None, token_list)
                for item in token_list:
                    if item in items_map_to_frequencies:
                        items_map_to_frequencies[item] += 1

                    else:
                        items_map_to_frequencies[item] = 1

            input_file.close()

            self.threshold = _minsup * trans

            # build sorted item list
            sorted_items_by_frequencies.append("null")
            items_map_to_frequencies["null"] = 0
            for item in items_map_to_frequencies:
                count = items_map_to_frequencies[item]
                i = 0
                for list_item in sorted_items_by_frequencies:
                    if items_map_to_frequencies[list_item] < count:
                        sorted_items_by_frequencies.insert(i, item)
                        break
                    i += 1

            # removing non-frequent
            for list_item in sorted_items_by_frequencies:
                if items_map_to_frequencies[list_item] < self.threshold:
                    items_to_remove.append(list_item)

            for itemToRemove in items_to_remove:
                sorted_items_by_frequencies.remove(itemToRemove)

    def build_fp_tree(self, _input, items_map_to_frequencies, sorted_items_by_frequencies, items_to_remove):
        # build header table
        # first element used as pointer
        self.header_table = []
        for itemsForTable in sorted_items_by_frequencies:
            self.header_table.append(FPTree(itemsForTable))

        self.fpTree = FPTree(None)
        self.fpTree.root = True

        transaction_sorted_by_frequency = []
        with open(_input) as input_file:
            for input_line in input_file:
                token_list = re.split(r'[\s,\r\n]+', input_line)
                # filter empty string
                token_list = filter(None, token_list)
                for item in token_list:
                    # ignore non-frequent items
                    if item in items_to_remove:
                        continue
                    index = 0
                    for string in transaction_sorted_by_frequency:
                        if items_map_to_frequencies[string] < items_map_to_frequencies[item] \
                                or (items_map_to_frequencies[string] == items_map_to_frequencies[item]
                                    and string.lower() < item.lower()):
                            transaction_sorted_by_frequency.insert(index, item)
                            break
                        index += 1

                    if item not in transaction_sorted_by_frequency:
                        transaction_sorted_by_frequency.append(item)

                # add to tree
                self.insert_into_tree(transaction_sorted_by_frequency, self.fpTree)
                transaction_sorted_by_frequency.clear()

            input_file.close()

            # header table with reversing order
            # first calculate the item frequencies in tree
            for item in self.header_table:
                count = 0
                temp_item = item
                while temp_item.next is not None:
                    temp_item = temp_item.next
                    count += temp_item.count
                item.count = count

            # sort header table
            self.header_table.sort(key=lambda x: x.count, reverse=True)

    def insert_into_tree(self, transaction_sorted_by_frequency, fp_tree):
        # return when list is empty
        if not transaction_sorted_by_frequency:
            return
        item_to_add_to_tree = transaction_sorted_by_frequency[0]
        new_node = None
        done = False
        for child in fp_tree.children:
            if child.item == item_to_add_to_tree:
                new_node = child
                child.count += 1
                done = True
                break

        if not done:
            new_node = FPTree(item_to_add_to_tree)
            new_node.count = 1
            new_node.parent = fp_tree
            fp_tree.children.append(new_node)
            for header_pointer in self.header_table:
                if header_pointer.item == item_to_add_to_tree:
                    while header_pointer.next is not None:
                        header_pointer = header_pointer.next
                    header_pointer.next = new_node

        transaction_sorted_by_frequency.pop(0)
        self.insert_into_tree(transaction_sorted_by_frequency, new_node)

    def fp_growth(self, base, threshold, header_table, frequent_patterns):
        for item_in_tree in header_table:
            current_pattern = (base if base is not None else "") + (" " if base is not None else "") + item_in_tree.item
            support_of_current_pattern = 0
            conditional_pattern_base = dict()
            while item_in_tree.next is not None:
                item_in_tree = item_in_tree.next
                support_of_current_pattern += item_in_tree.count
                conditional_pattern = None
                conditional_item = item_in_tree.parent

                while not conditional_item.is_root():
                    conditional_pattern = conditional_item.item + " " + (
                        conditional_pattern if conditional_pattern is not None else "")
                    conditional_item = conditional_item.parent

                if conditional_pattern is not None:
                    conditional_pattern_base[conditional_pattern] = item_in_tree.count

            frequent_patterns[tuple(current_pattern.split())] = support_of_current_pattern

            # counting frequencies of single items in conditional pattern-base
            conditional_items_map_to_frequency = dict()
            for conditional_pattern in conditional_pattern_base:
                split_conditional_pattern = conditional_pattern.split()
                for item in split_conditional_pattern:
                    if item in conditional_items_map_to_frequency:
                        count = conditional_items_map_to_frequency[item]
                        count += conditional_pattern_base[conditional_pattern]
                        conditional_items_map_to_frequency[item] = count
                    else:
                        conditional_items_map_to_frequency[item] = conditional_pattern_base[conditional_pattern]

            # create header table for conditional fp tree
            conditional_header_table = []
            for itemsForTable in conditional_items_map_to_frequency:
                count = conditional_items_map_to_frequency[itemsForTable]
                if count < threshold:
                    continue
                f = FPTree(itemsForTable)
                f.count = count
                conditional_header_table.append(f)

            conditional_fp_tree = self.build_conditional_fp_tree(conditional_pattern_base,
                                                                 conditional_items_map_to_frequency, threshold,
                                                                 conditional_header_table)

            # header table with reverse ordering
            conditional_header_table.sort(key=lambda x: x.count, reverse=True)
            # children is not empty
            if conditional_fp_tree.children:
                self.fp_growth(current_pattern, threshold, conditional_header_table, frequent_patterns)

    def build_conditional_fp_tree(self, conditional_pattern_base, conditional_items_map_to_frequency, threshold,
                                  conditional_header_table):
        conditional_fp_tree = FPTree(None)
        conditional_fp_tree.root = True

        for pattern in conditional_pattern_base:
            # removing non-frequent pattern and make a list instead of string
            pattern_list = []
            split_pattern = pattern.split()
            for item in split_pattern:
                if conditional_items_map_to_frequency[item] >= threshold:
                    pattern_list.append(item)
            self.insert_into_conditional_fp_tree(pattern_list, conditional_pattern_base[pattern], conditional_fp_tree,
                                                 conditional_header_table)
        return conditional_fp_tree

    # the insert function for conditional fp tree
    def insert_into_conditional_fp_tree(self, pattern_list, count_of_pattern, conditional_fp_tree,
                                        conditional_header_table):
        # return if patternArrayList is empty
        if not pattern_list:
            return

        item_to_add_to_tree = pattern_list[0]
        new_node = None
        done = False
        for child in conditional_fp_tree.children:
            if child.item == item_to_add_to_tree:
                new_node = child
                child.count += count_of_pattern
                done = True
                break

        if not done:
            for header_pointer in conditional_header_table:
                # remove non frequents too
                if header_pointer.item == item_to_add_to_tree:
                    new_node = FPTree(item_to_add_to_tree)
                    new_node.count = count_of_pattern
                    new_node.parent = conditional_fp_tree
                    conditional_fp_tree.children.append(new_node)
                    while header_pointer.next is not None:
                        header_pointer = header_pointer.next
                    header_pointer.next = new_node
        pattern_list.pop(0)
        self.insert_into_conditional_fp_tree(pattern_list, count_of_pattern, new_node, conditional_header_table)

    def print_fp(self):
        for item in self.frequent_patterns:
            print("{ %s } ( %d )" % (" ".join(item), self.frequent_patterns[item]))

    def generating_rules(self):
        # proceed if frequent pattern's size is larger than 1
        for frequent_pattern in self.frequent_patterns:
            if len(frequent_pattern) >= 2:
                power_set = list(build_power_set(frequent_pattern))
                for subset in power_set:
                    if subset in self.frequent_patterns.keys():
                        conf = self.frequent_patterns[frequent_pattern] / self.frequent_patterns[subset]
                        if conf >= self.minconf:
                            frequent_minus_subset = ""
                            for item in frequent_pattern:
                                if item not in subset:
                                    frequent_minus_subset += item + " "
                            print("{ %s } => { %s} ( %.2f )" % (" ".join(subset), frequent_minus_subset, conf))