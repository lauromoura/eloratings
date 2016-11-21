import sys
import os
import logging
from math import sqrt

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

    standings = data.standings(Championship.COMPLETE)
    print(standings.sort_values(by='Points', ascending=False))

    matches = data.pending_matches
    # FIXME Detect automatically the next matches
    matches = matches[matches['Round'] == 36]

    attack = {}
    defense = {}
    diff = {}

    for match in matches.itertuples():
        home = standings.loc[match.HomeTeam]
        away = standings.loc[match.AwayTeam]

        print("Stats for ", match.HomeTeam, "vs", match.AwayTeam)

        home_average_goals_for = home.HomeGoalsFor / home.HomeGames
        home_average_goals_against = home.HomeGoalsAgainst / home.HomeGames
        away_average_goals_for = away.AwayGoalsFor / away.AwayGames
        away_average_goals_against = away.AwayGoalsAgainst / away.AwayGames

        print("Home average goals for: %0.1f" % home_average_goals_for)
        print("Home average goals against: %0.1f" % home_average_goals_against)
        print("Away average goals for: %0.1f" % away_average_goals_for)
        print("Away average goals against: %0.1f" % away_average_goals_against)

        expected_home_for = sqrt(home_average_goals_for * away_average_goals_against)
        expected_away_for = sqrt(away_average_goals_for * home_average_goals_against)
        print("Expected home goals factor for: %0.1f" % expected_home_for)
        print("Expected away goals factor for: %0.1f" % expected_away_for)
        print("Expected TOTAL goals for: %0.1f" % (home_average_goals_for * away_average_goals_against + away_average_goals_for * home_average_goals_against))

        print()

        attack[match.HomeTeam] = expected_home_for
        attack[match.AwayTeam] = expected_away_for
        defense[match.HomeTeam] = expected_away_for
        defense[match.AwayTeam] = expected_home_for
        diff[match.HomeTeam] = expected_home_for - expected_away_for
        diff[match.AwayTeam] = expected_away_for - expected_home_for


    def sorted_dict_by_value(d, reverse=False):
        return sorted(d, key=lambda k: d[k], reverse=reverse)

    print("Best attacks")
    for k in sorted_dict_by_value(attack, reverse=True):
        print(k, attack[k])
    print()

    print("Best defenses")
    for k in sorted_dict_by_value(defense):
        print(k, defense[k])
    print()

    print("Best diff")

    for k in sorted_dict_by_value(diff, reverse=True):
        print(k, diff[k])

    # print()
    # ratings = data.load_initial_elo()

    # latest = ratings.tail(1)
    # print(pd.melt(latest).sort_values(by="value", ascending=False))
    # plt.legend(loc=3)
    # plt.show()

    # print(data.standings())

if __name__ == "__main__":
    # import cProfile
    # cProfile.run('main()', sort='cumtime')
    main()

