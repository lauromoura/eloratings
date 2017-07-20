import sys
import os
import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

from elo.db import Championship

def main(argv=None):

    if argv is None:
        argv = sys.argv

    try:
        path = argv[1]
    except IndexError as e:
        logging.critical("You must provide a path")
        sys.exit(1)

    data = Championship.from_directory(argv[1])
    print(data.standings())

    acc = defaultdict(list)

    N = int(argv[2])
    for n in range(N):
        print(n)
        standings = data.play_matches(n=500).standings()

        for key in standings.index:
            position = standings.index.get_loc(key) + 1

            acc[key].append(position)


    # print(acc)
    results = pd.DataFrame(acc)
    print(results.describe())
    results.to_csv('data.csv')


if __name__ == "__main__":
    main()
