#! /usr/bin/env python3
import time


__author__ = 'mhwong'
from classes.FPGrowth import FPGrowth
from sys import argv
if __name__ == '__main__':
    if len(argv) != 4:
        print("Usage:", argv[0], "input_file minsup minconf")
    else:
        start_time = time.clock()
        FPGrowth(argv[1], float(argv[2]), float(argv[3]))
        end_time = time.clock()
        print("Execution time", (end_time - start_time), "s")
    # FPGrowth("/home/mhwong/Desktop/testdata", 0.6, 0.5)