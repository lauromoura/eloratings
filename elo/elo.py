'''elo.py - Calculate elo ratings based on World Football Elo'''

HOME_FACTOR = 100

WIN = 1.0
DRAW = 0.5
LOSS = 0.0


def expected_probabilities(home_elo, away_elo):
    '''Calculates the probabilities of winning for each elo rating.'''
    difference = (away_elo - (home_elo + HOME_FACTOR)) / 400.0
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


def play_match(home_elo, away_elo, home_goals, away_goals, level=40):
    '''Evaluates a match and returns the updated elo ratings'''

    home_prob, away_prob = expected_probabilities(home_elo, away_elo)

    goal_difference = abs(home_goals - away_goals)

    k = level * goal_difference_factor(goal_difference)

    home_outcome, away_outcome = outcomes_factor(home_goals, away_goals)

    home_new = new_ratings(home_elo, home_outcome, home_prob, k)
    away_new = new_ratings(away_elo, away_outcome, away_prob, k)

    return round(home_new), round(away_new)
