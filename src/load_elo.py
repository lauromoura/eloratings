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

    # print(data)
    # print(data.matches)
    # print(data.complete_matches)
    # print(data.pending_matches)

    # x = data.complete_matches
    # print(x.groupby('HomeTeam'))

    standings = data.standings()
    print(standings.sort_values(by='Points', ascending=False))

    matches = data.pending_matches
    matches = matches[matches['Round'] == 34]

    for match in matches.itertuples():
        home = standings.loc[match.HomeTeam]
        away = standings.loc[match.AwayTeam]

        print("Stats for ", match.HomeTeam, "vs", match.AwayTeam)

        home_average_goals_for = home.HomeGoalsFor / home.HomeGames
        home_average_goals_against = home.HomeGoalsAgainst / home.HomeGames
        away_average_goals_for = away.AwayGoalsFor / away.AwayGames
        away_average_goals_against = away.AwayGoalsAgainst / away.AwayGames

        # print("Home average goals for: ", home_average_goals_for)
        # print("Home average goals against: ", home_average_goals_against)
        # print("Away average goals for: ", away_average_goals_for)
        # print("Away average goals against: ", away_average_goals_against)

        print("Expected home goals for:", home_average_goals_for * away_average_goals_against)
        print("Expected away goals for:", away_average_goals_for * home_average_goals_against)
        print("Expected TOTAL goals for:", home_average_goals_for * away_average_goals_against + away_average_goals_for * home_average_goals_against)



    print()
    ratings = data.load_initial_elo()

    # latest = ratings.tail(1)
    # print(pd.melt(latest).sort_values(by="value", ascending=False))
    # plt.legend(loc=3)
    # plt.show()

    print(data.standings())

    acc = defaultdict(list)

    for n in range(100000):
        print(n)
        standings = data.play_matches(n=100).standings()

        for key in standings.index:
            position = standings.index.get_loc(key) + 1

            acc[key].append(position)


    # print(acc)
    results = pd.DataFrame(acc)
    print(results.describe())
    results.to_csv('data.csv')


if __name__ == "__main__":
    main()
