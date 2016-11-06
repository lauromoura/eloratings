import sys
import os
import logging

import pandas as pd
import numpy as np

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

    print(data)
    print(data.matches)

    for match in data.matches.itertuples():
        back_round = 19 + match.Round
        back_date = data.rounds.get_value(back_round, "Date")
        back_match = pd.DataFrame(columns=data.matches.columns)
        back_match.loc[0] = [back_round, back_date, match.AwayTeam, match.HomeTeam,
                             np.NAN, np.NAN]

        data.matches = data.matches.append(back_match, ignore_index=True)

    print(data.matches)

    data.matches.to_csv('foo.csv', sep=' ', header=True, index=False, float_format="%.0f")


if __name__ == "__main__":
    main()
