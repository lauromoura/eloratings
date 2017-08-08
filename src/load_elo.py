import sys
import os
import logging
import cProfile
import argparse

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

from elo.db import Championship


def simulate(data, n, acc, acc2):
    for i in range(n):
        print(i)
        standings = data.play_matches(n=500).standings()

        for key in standings.index:
            position = standings.index.get_loc(key) + 1

            acc[key].append(position)
            acc2[key][position] += 1

def main(argv=None):

    parser = argparse.ArgumentParser(
        description='Simulates future matches.')
    parser.add_argument('path', metavar='PATH', help='database path')
    parser.add_argument('--number', dest='iterations', action='store',
        type=int, default=100, help='Number of iterations')
    parser.add_argument('--profile', dest='profile', action='store_true',
            default=False, help='Enable profiling')

    args = parser.parse_args()

    data = Championship.from_directory(args.path)
    print(data.standings())
    current = data.current_ranking()

    for i, key in enumerate(sorted(current, key=lambda k: current[k], reverse=True)):
        print(i+1, key, current[key])

    acc = defaultdict(list)
    acc2 = defaultdict(lambda :defaultdict(int))

    N = args.iterations
    if args.profile:
        print("Starting profiling...")
        cProfile.runctx('simulate(data, N, acc, acc2)', globals(), locals(), filename='simulate_stats')
        print("Done profiling.")
    else:
        simulate(data, N, acc, acc2)
    # print(acc)
    results = pd.DataFrame(acc)
    print(results.describe())
    results.to_csv('data.csv')

    json_str = json.dumps(acc2, sort_keys=True, indent=4)
    print(json_str)

    with open('data.json', 'w') as handle:
        json.dump(acc2, handle, sort_keys=True, indent=4)

if __name__ == "__main__":
    main()
