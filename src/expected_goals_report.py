#!/usr/bin/env python3

import sys
import os
import logging
from math import sqrt

import pandas as pd
import numpy as np

from collections import defaultdict

from elo.db import Championship


def harmmean(a, b):
    return 2 / ((a**(-1)) + (b**(-1)))


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
    matches = matches[matches['Round'] == int(argv[2])]

    attack = {}
    defense = {}
    diff = {}

    team_data = {}

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

        # Maybe multiplication is not the best option for expected results
        # due to zero
        if home_average_goals_for == 0:
            home_average_goals_for = 0.1
        if home_average_goals_against == 0:
            home_average_goals_against = 0.1
        if away_average_goals_for == 0:
            away_average_goals_for = 0.1
        if away_average_goals_against == 0:
            away_average_goals_against = 0.1
        expected_home_for = sqrt(home_average_goals_for * away_average_goals_against)
        expected_away_for = sqrt(away_average_goals_for * home_average_goals_against)
        harm_expected_home_for = harmmean(home_average_goals_for, away_average_goals_against)
        harm_expected_away_for = harmmean(away_average_goals_for, home_average_goals_against)
        print("Expected home goals factor for: %0.1f" % expected_home_for)
        print("Expected away goals factor for: %0.1f" % expected_away_for)
        print("NEW Expected home goals factor for: %0.1f" % harm_expected_home_for)
        print("NEW Expected away goals factor for: %0.1f" % harm_expected_away_for)

        print()

        attack[match.HomeTeam] = expected_home_for
        attack[match.AwayTeam] = expected_away_for
        defense[match.HomeTeam] = expected_away_for
        defense[match.AwayTeam] = expected_home_for
        diff[match.HomeTeam] = expected_home_for - expected_away_for
        diff[match.AwayTeam] = expected_away_for - expected_home_for

        team_data[match.HomeTeam] = (attack[match.HomeTeam], defense[match.HomeTeam], diff[match.HomeTeam])
        team_data[match.AwayTeam] = (attack[match.AwayTeam], defense[match.AwayTeam], diff[match.AwayTeam])


    def sorted_dict_by_value(d, reverse=False):
        return sorted(d, key=lambda k: d[k], reverse=reverse)


    mask = '%.1f'
    print("Best attacks")
    for k in sorted_dict_by_value(attack, reverse=True):
        print(k, mask % attack[k])
    print()

    print("Best defenses")
    for k in sorted_dict_by_value(defense):
        print(k, mask % defense[k])
    print()

    print("Best diff")

    for k in sorted_dict_by_value(diff, reverse=True):
        print(k, mask % diff[k])

    print("{:<10}\t{:>5}\t{:>5}\t{:>5}".format("Team", "Attack", "Defense", "Diff"))
    for k in team_data:
        d = team_data[k]
        print("{:<10}\t{:5.1f}\t{:5.1f}\t{:5.1f}".format(k, d[0], d[1], d[2]))

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

