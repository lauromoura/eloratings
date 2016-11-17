import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from elo import elo

from datetime import timedelta


class Championship:

    @classmethod
    def from_directory(klass, path):
        obj = klass()

        matches_file = os.path.join(path, "matches.csv")
        initial_file = os.path.join(path, "initial.csv")

        matches_df = pd.read_csv(matches_file, sep=" ",
                                 parse_dates=["Date"], dayfirst=True,
                                 comment="#")

        initial_df = pd.read_csv(initial_file, sep=" ", comment="#")

        obj.path = path
        obj.matches = matches_df
        obj.initial = initial_df

        obj.load_initial_elo()

        return obj

    @property
    def complete_matches(self):
        return self.matches.dropna()

    @property
    def pending_matches(self):
        return self.matches[np.isnan(self.matches["HomeScore"])]

    def initial_for_team(self, team):
        # FIXME Do we really need the ranking? Why not just refactor
        # the initial.csv to make the teams the index?
        return self.initial[self.initial["Team"] == team].iloc[0].Rating

    def latest_elo(self, team):
        team_elos = self.ratings[team].dropna()

        x = team_elos.iloc[-1:]
        return x[0]

    def load_initial_elo(self):

        matches = self.complete_matches.sort_values(by="Date")

        initial_date = matches["Date"].min() - timedelta(days=1)

        teams = matches["HomeTeam"].unique()
        ratings = pd.DataFrame()
        self.ratings = ratings

        for team in teams:
            ratings.loc[initial_date, team] = self.initial_for_team(team)

        for match in matches.itertuples():
            home = match.HomeTeam
            away = match.AwayTeam

            pre_match_home_elo = self.latest_elo(home)
            pre_match_away_elo = self.latest_elo(away)

            home_new, away_new = elo.play_match(
                pre_match_home_elo,
                pre_match_away_elo,
                match.HomeScore,
                match.AwayScore)

            ratings.loc[match.Date, match.HomeTeam] = home_new
            ratings.loc[match.Date, match.AwayTeam] = away_new

        for i in ratings.columns:
            ratings[i].fillna(method='ffill').plot(linewidth=2)

        return ratings

    def current_ranking(self):
        data = {}
        for team in self.ratings:
            data[team] = self.latest_elo(team)

        return data

    def clone(self):
        clone = Championship()

        clone.path = self.path

        clone.matches = self.matches.copy()
        clone.initial = self.initial.copy()
        clone.ratings = self.ratings.copy()

        return clone

    def play_matches(self, n=1):
        ''' Plays the given number of matches and returns a new instance'''

        new = self.clone()

        for i in new.pending_matches.head(n).itertuples():
            # print(i)
            # print(i.HomeTeam)

            home_elo = new.latest_elo(i.HomeTeam)
            away_elo = new.latest_elo(i.AwayTeam)

            # print(home_elo + 100 - away_elo)
            home_goals, away_goals = elo.random_result(home_elo, away_elo)

            home_new_elo, away_new_elo = elo.play_match(home_elo, away_elo,
                                                        home_goals, away_goals)

            # print(home_new_elo, away_new_elo)

            new.matches.loc[i.Index, "HomeScore"] = home_goals
            new.matches.loc[i.Index, "AwayScore"] = away_goals

            new.ratings.loc[i.Date, i.HomeTeam] = home_new_elo
            new.ratings.loc[i.Date, i.AwayTeam] = away_new_elo

        return new

    def standings(self, ):
        '''Gives the standings with the current data.

        Tie break criteria:
            - Number of wins
            - Goal difference
            - Goals scored
            - Head to head
        Unused tie breaks
            - Least red cards
            - Least yellow cards
            - Drawing bets'''

        matches = self.complete_matches

        df = pd.DataFrame(columns=['Points', 'Games', 'HomeGames', 'AwayGames',
                                   'Wins', 'Draws', 'Losses',
                                   'GoalsFor', 'GoalsAgainst', 'GoalDiff',
                                   'HomeGoalsFor', 'HomeGoalsAgainst',
                                   'HomeGoalsDiff', 'AwayGoalsFor',
                                   'AwayGoalsAgainst', 'AwayGoalsDiff'])

        for team in matches['HomeTeam'].unique():

            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            points = 0
            games = 0

            home_games = 0
            away_games = 0

            home_goals_for = 0
            home_goals_against = 0

            away_goals_for = 0
            away_goals_against = 0

            is_home = matches['HomeTeam'] == team
            is_away = matches['AwayTeam'] == team
            team_matches = matches[is_home | is_away]

            for match in team_matches.itertuples():
                if match.HomeTeam == team:
                    team_goals = match.HomeScore
                    other_goals = match.AwayScore

                    home_goals_for += team_goals
                    home_goals_against += other_goals

                    home_games += 1
                else:
                    team_goals = match.AwayScore
                    other_goals = match.HomeScore

                    away_goals_for += team_goals
                    away_goals_against += other_goals

                    away_games += 1

                games += 1
                goals_for += team_goals
                goals_against += other_goals

                if team_goals > other_goals:
                    wins += 1
                    points += 3
                elif team_goals == other_goals:
                    draws += 1
                    points += 1
                else:
                    losses += 1

            df.loc[team] = [points, games, home_games, away_games,
                            wins, draws, losses,
                            goals_for, goals_against,
                            goals_for - goals_against,
                            home_goals_for, home_goals_against,
                            home_goals_for - home_goals_against,
                            away_goals_for, away_goals_against,
                            away_goals_for - away_goals_against]

        return df.sort_values(by=["Points", "Wins",
                                  "GoalDiff", "GoalsFor"], ascending=False)
