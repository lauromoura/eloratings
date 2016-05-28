#!/usr/bin/env python

import sys
import csv
import logging
from datetime import datetime, MAXYEAR, MINYEAR

from elo import parser
from elo import elo

def match_between(match,
                    first_date=datetime(MINYEAR,1,1),
                    last_date=datetime(MAXYEAR,1,1)):
    return first_date < match['Date'] <= last_date

def process_round(matches, current_round, previous_round, elos):
    print()
    print("Processing round starting %s and finishing %s" %(previous_round, current_round))

    round_matches = [match for match in matches if match_between(match, previous_round, current_round)]
    print(round_matches)

    for match in round_matches:
        home = match['HomeTeam']
        away = match['AwayTeam']
        home_g = match['HomeScore']
        away_g = match['AwayScore']
        odds, _ = elo.expected_probabilities(elos[home][-1], elos[away][-1])

        outcome_ok = home_g - away_g > 0 if odds > 0 else True
        print(outcome_ok)

        home_elo, away_elo = elo.play_match(elos[home][-1], elos[away][-1], home_g, away_g)
        print("%s vs %s: odds home: %s" % (home, away, odds))

        elos[home].append(home_elo)
        elos[away].append(away_elo)

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
    matches = parser.parse_matches(path)
    print(rounds)
    print(matches)
    print(elos)

    first_round = rounds[0]

    previous_round = datetime(MINYEAR, 1, 1)
    for current_round in rounds:
        process_round(matches, current_round, previous_round, elos)
        previous_round = current_round

    # for match in first_matches:
    #     home = match['HomeTeam']
    #     away = match['AwayTeam']
    #     home_g = match['HomeScore']
    #     away_g = match['AwayScore']
    #     odds, _ = elo.expected_probabilities(initial[home], initial[away])

    #     outcome_ok = home_g - away_g > 0 if odds > 0 else True
    #     print(outcome_ok)

    #     home_elo, away_elo = elo.play_match(initial[home], initial[away], home_g, away_g)
    #     print("%s vs %s: odds home: %s" % (home, away, odds))

    #     initial[home] = home_elo
    #     initial[away] = away_elo
    #     elos[home].append(home_elo)
    #     elos[away].append(away_elo)

    sorted_data = [(v, k) for k, v in elos.items()]
    sorted_data.sort(reverse=True, key=lambda x: x[0][-1])

    for i, data in enumerate(sorted_data):
        print(i+1, data)

    print(elos)

    def future_odds(a, b):
        odds, _ = elo.expected_probabilities(elos[a][-1], elos[b][-1])
        print("Chances de %s vencer %s em casa: %.f%%" % (a, b, odds*100))

    future_odds('Cruzeiro', 'AmericaMG')
    future_odds('AtleticoPR', 'Figueirense')
    future_odds('Chapecoense', 'SantaCruz')
    future_odds('PontePreta', 'Flamengo')
    future_odds('Sport', 'Corinthians')
    future_odds('Vitoria', 'AtleticoMG')
    future_odds('Fluminense', 'Botafogo')
    future_odds('SaoPaulo', 'Palmeiras')
    future_odds('Santos', 'Internacional')
    future_odds('Gremio', 'Coritiba')

if __name__ == "__main__":
    main()
