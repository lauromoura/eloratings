'''elo.py - Calculate elo ratings based on World Football Elo'''

import random

HOME_FACTOR = 100

WIN = 1.0
DRAW = 0.5
LOSS = 0.0


def expected_probabilities(home_elo, away_elo, neutral=False):
    '''Calculates the probabilities of winning for each elo rating.'''
    modifier = HOME_FACTOR if not neutral else 0
    difference = (away_elo - (home_elo + modifier)) / 400.0
    home_prob = 1.0 / (1 + 10**difference)
    away_prob = 1.0 - home_prob

    return home_prob, away_prob


def goal_difference_factor(goal_diff):
    '''Returns the multiplier factor for a given score difference'''
    if goal_diff <= 1:
        return 1
    elif goal_diff == 2:
        return 1.5
    elif goal_diff == 3:
        return 1.0 + 3.0/4
    else:
        return 1.0 + 3.0/4 + (goal_diff - 3) / 8.0


def outcomes_factor(home_goals, away_goals):
    '''Returns the K multiplier for a given outcome (win/loss/draw)'''
    if home_goals > away_goals:
        return (1.0, 0.0)
    elif home_goals == away_goals:
        return (0.5, 0.5)
    else:
        return (0.0, 1.0)


def new_ratings(elo, outcome, prob, k):
    '''Returns the new ratings based on the given factors'''
    factor = outcome - prob
    return round(elo + k * factor)


def play_match(home_elo, away_elo, home_goals, away_goals, level=40,
               neutral=False):
    '''Evaluates a match and returns the updated elo ratings'''

    home_prob, away_prob = expected_probabilities(home_elo, away_elo, neutral)

    goal_difference = abs(home_goals - away_goals)

    k = level * goal_difference_factor(goal_difference)

    home_outcome, away_outcome = outcomes_factor(home_goals, away_goals)

    home_new = new_ratings(home_elo, home_outcome, home_prob, k)
    away_new = new_ratings(away_elo, away_outcome, away_prob, k)

    return round(home_new), round(away_new)


def draw_chance(elo_win_prob):
    '''Gives the chance of a draw happening given a elo win probability'''
    quadratic = -0.8
    linear = 0.8
    constant = 0.05
    return quadratic * elo_win_prob ** 2 + linear * elo_win_prob + constant


def actual_chance_of_winning(elo_win_prob, draw_prob=None):
    '''Gives the actual chance of the home team winning'''

    if not draw_prob:
        draw_prob = draw_chance(elo_win_prob)

    return elo_win_prob * (1 - draw_prob)


def random_chances(home_elo, away_elo, neutral=False):
    '''Gives the results chances as probabilities.

    Based on the two elo ratings given and whether the match is in a neutral
    field or not, this function calculates the probabilites of:

        - home team winning
        - draw
        - away team winning
    '''
    home_prob, _, = expected_probabilities(home_elo, away_elo, neutral)

    draw_prob = draw_chance(home_prob)
    home_win = actual_chance_of_winning(home_prob, draw_prob)
    away_win = 1 - draw_prob - home_win

    return home_win, draw_prob, away_win


def random_result(home_elo, away_elo, neutral=False):
    '''Returns the home and away goals for a simulated match.

    Home results are 1-0, draws 0-0, and away win 0-1.
    '''
    _, draw_prob, away_prob = random_chances(home_elo, away_elo,
                                             neutral)

    pick = random.random()

    if pick < away_prob:
        home_goals = 0
        away_goals = 1
    elif pick < away_prob + draw_prob:
        home_goals = 0
        away_goals = 0
    else:
        home_goals = 1
        away_goals = 0

    return home_goals, away_goals
