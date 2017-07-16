#!/usr/bin/env python

import sys
import csv
import logging
import random
from datetime import datetime, MAXYEAR, MINYEAR
import pandas as  pd
from scipy.stats.mstats import hmean

import seaborn
from matplotlib import pyplot as plt

from elo import parser
from elo import elo

def match_between(match,
                    first_date=datetime(MINYEAR,1,1),
                    last_date=datetime(MAXYEAR,1,1)):
    # print(match)
    return first_date < match['Date'] <= last_date

home_wins = 0
draws = 0
home_losses = 0

def split_matches_into_rounds(matches, rounds):
    if not rounds:
        return []

    current_round = rounds[0]

    my_matches = [match for match in matches if match['Date'] <= current_round]
    remaining_matches = [match for match in matches if match['Date'] > current_round]

    return [my_matches] + split_matches_into_rounds(remaining_matches, rounds[1:])

def process_round(matches, round_idx, current_round, previous_round, elos, points):
    global home_wins
    global draws
    global home_losses
    print()
    print("Processing round starting %s and finishing %s with index %s" %(previous_round, current_round, round_idx))

    df = pd.DataFrame(columns=['team', 'round', 'elo_after', 'elo_before',
                               'rival_elo_before', 'elo_difference',
                               'goals_for', 'goals_against', 'home'])

    round_matches = [match for match in matches if match_between(match, previous_round, current_round)]
    # print(round_matches)

    for match in round_matches:
        home = match['HomeTeam']
        away = match['AwayTeam']
        home_g = match['HomeScore']
        away_g = match['AwayScore']
        odds, _ = elo.expected_probabilities(elos[home][-1], elos[away][-1])
        # print("%s vs %s: odds home: %s" % (home, away, odds))

        if home_g > away_g:
            home_wins += 1
            points[home] += 3
        elif home_g == away_g:
            draws += 1
            points[home] += 1
            points[away] += 1
        else:
            home_losses += 1
            points[away] += 3

        outcome_ok = home_g - away_g > 0 if odds > 0.5 else True
        # print(outcome_ok)

        home_elo, away_elo = elo.play_match(elos[home][-1], elos[away][-1], home_g, away_g)

        elos[home].append(home_elo)
        elos[away].append(away_elo)

        idx = home + '_' + str(round_idx)
        df.loc[idx] = [home, round_idx, home_elo, elos[home][-2],
                       elos[away][-2], elos[home][-2] - elos[away][-2],
                       home_g, away_g, True]

        idx = away + '_' + str(round_idx)
        df.loc[idx] = [away, round_idx, away_elo, elos[away][-2],
                       elos[home][-2], elos[away][-2] - elos[home][-2],
                       away_g, home_g, False]

    return df

def future_odds(a, b, elos):
    odds, _ = elo.expected_probabilities(elos[a][-1], elos[b][-1])
    draw_chance = elo.draw_chance(odds)
    odds = elo.actual_chance_of_winning(odds, draw_chance)
    loss = 1.0 - odds - draw_chance
    print("%s, %s, %.f%%, %.f%%, %.f%%" % (a, b, odds*100, draw_chance*100, loss*100))


def main(argv=None):

    if argv is None:
        argv = sys.argv

    try:
        path = argv[1]
    except IndexError as e:
        logging.critical("You must provide a path")
        sys.exit(1)

    rounds = parser.parse_rounds(path)
    initial = parser.parse_initial(path)
    elos = {k: [v] for k, v in initial.items()}
    points = {k: 0 for k in initial}
    matches = parser.parse_matches(path)
    fixtures = parser.parse_fixtures(path)

    rounds_played = 19

    df = pd.DataFrame()

    previous_round = datetime(MINYEAR, 1, 1)
    for i, current_round in enumerate(rounds[:rounds_played]):
        n_df = process_round(matches, i+1, current_round, previous_round, elos, points)
        previous_round = current_round
        df = pd.concat([df, n_df])

    print(df)


    sorted_data = [(v, k) for k, v in elos.items()]
    sorted_data.sort(reverse=True, key=lambda x: x[0][-1])

    for i, data in enumerate(sorted_data):
        print(i+1, "%s %s" % (data[1], data[0][-1]))

    print(elos)
    print(points)


    print("Home wins: %s" % home_wins)
    print("Draws: %s" % draws)
    print("Away wins: %s" % home_losses)

    # split = split_matches_into_rounds(fixtures, rounds[rounds_played:])
    # for round in split:
        # print(len(round))

    # next_round = split[0]

    # for match in next_round:
    #     # print(match)
    #     future_odds(match['HomeTeam'], match['AwayTeam'], elos)


    for points, team in sorted_data:
        print(points, team)
        x = range(len(points))
        plt.plot(x, points, label=team)

    futures = pd.DataFrame(columns=['Rodada', 'Team', 'Elo_Self', 'Rival', 'Elo_Rival',
                                    'Relative', 'Adjusted_relative'])

    for i, fixture in enumerate(fixtures):
        home = fixture['HomeTeam']
        away = fixture['AwayTeam']
        home_elo = elos[home][-1]
        away_elo = elos[away][-1]

        futures.loc[i*2] = [int(i/10)+16, home, home_elo, away, away_elo,
                            home_elo - away_elo, home_elo + 100 - away_elo]
        futures.loc[i*2+1] = [int(i/10)+16, away, away_elo, home, home_elo,
                              away_elo - home_elo, away_elo - (home_elo + 100)]

    print(futures)

    x = futures.pivot(index='Rodada', columns='Team', values='Elo_Rival')
    print(x)
    print(x.describe())

    print("Media")
    print(x.mean().sort_values(ascending=False))

    print("Harmean")
    y = x.apply(hmean)
    print(y.sort_values(ascending=False))
    # print(x.mean().sort_values(ascending=False))

    jogos_sport = df[df["team"] == "Palmeiras"]

    resultados_sport = jogos_sport['goals_for'] - jogos_sport['goals_against']

    def calc_pontos(diff):
        if diff > 0:
            return 3
        elif diff < 0:
            return 0
        else:
            return 1

    d = resultados_sport.apply(calc_pontos).sum()
    print(d)

    points = pd.DataFrame(columns=["team", "points"])
    elos_df = pd.DataFrame(columns=["team", "elo"])

    for team in df["team"].unique():
        jogos = df[df['team'] == team]
        resultados = jogos['goals_for'] - jogos['goals_against']
        points.loc[team] = [team, resultados.apply(calc_pontos).sum()]
        elos_df.loc[team] = [team, elos[team][-1]]

    print(points)
    print(elos_df)

    simulations_df = pd.DataFrame(columns=df["team"].unique())

    iterations = 1000

    for it in range(iterations):
        if it % 10 == 0:
            print("Simulating iteration ", it)
        simulation_points = points.copy()
        simulations_elo = elos_df.copy()
        # simulations_df.loc[it] = []
        for fixture in fixtures:
            home = fixture["HomeTeam"]
            home_elo = simulations_elo.loc[home]["elo"]
            away = fixture["AwayTeam"]
            away_elo = simulations_elo.loc[away]["elo"]

            # Get outcomes
            home_prob, _away_prob = elo.expected_probabilities(home_elo, away_elo)

            draw_prob = elo.draw_chance(home_prob)
            actual_home_prob = elo.actual_chance_of_winning(home_prob, draw_prob)
            actual_away_prob = 1.0 - actual_home_prob - draw_prob

            # Surprise, modefoca
            pick = random.random()

            if pick <= actual_away_prob:
                home_g = 0
                away_g = 1

                current_points = simulation_points.loc[away]["points"]
                simulation_points.set_value(away, "points", current_points + 3)

            elif pick <= (actual_away_prob + draw_prob):
                home_g = 0
                away_g = 0
                current_points = simulation_points.loc[away]["points"]
                simulation_points.set_value(away, "points", current_points + 1)
                current_points = simulation_points.loc[home]["points"]
                simulation_points.set_value(home, "points", current_points + 1)
            else:
                home_g = 1
                away_g = 0
                current_points = simulation_points.loc[home]["points"]
                simulation_points.set_value(home, "points", current_points + 3)

            home_new_elo, away_new_elo = elo.play_match(home_elo, away_elo, home_g, away_g)

            simulations_elo.set_value(home, "elo", home_new_elo)
            simulations_elo.set_value(away, "elo", away_new_elo)



            # Update elo and points


        for team in simulation_points["team"]:
            simulations_df.set_value(it, team,
                                     simulation_points.loc[team]["points"])

    # print(simulations_df)


    simulations_df.to_csv("simulation.csv")


    # seaborn.boxplot(data=simulations_df)
    # plt.show()




    # x.plot()

    # x.summary()

    # seaborn.boxplot(x="Team", y="Adjusted_relative", data=futures)
    # futures.plot()
    # plt.show()

    plt.legend(loc=6)
    plt.show()
    # plt.close()

    # seaborn.boxplot(x="time", y="elo", data=xdf)
    # plt.show()

    # seaborn.boxplot(x="team", y="elo_difference",
    #                 data=df.loc[df['home'] == False])
    # plt.show()
    # plt.close()

    # df.loc[df['home']==True].plot(kind='scatter', x="goals_for", y="goals_against")
    # seaborn.heatmap(df)
    # plt.show()

if __name__ == "__main__":
    main()
