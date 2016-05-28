import unittest
from elo import play_match

class TestElo(unittest.TestCase):

    def test_simple_draw(self):
        # March 29th, 2016
        # Paraguay 2-2 Brazil, in Paraguay, Normal level
        expected = (1732, 1993)
        home_goals = 2
        away_goals = 2
        elo_delta = 9

        self.assertEqual(play_match(expected[0]-elo_delta,
                                    expected[1]+elo_delta,
                                    home_goals,
                                    away_goals),
                         expected)


    def test_big_home_win(self):
        # March 29th, 2016
        # Japan 5-0 Syria in Japan, Normal level (WC qualifier)
        expected = (1749, 1508)
        home_goals = 5
        away_goals = 0
        elo_delta = 11 # Change in home elo

        self.assertEqual(play_match(expected[0]-elo_delta,
                                    expected[1]+elo_delta,
                                    home_goals,
                                    away_goals),
                         expected)


    def test_narrow_away_win(self):
        # March 29th, 2016
        # Puerto Rico 0-1 Guyana in Puerto Rico, Normal level
        expected = (1054, 1244)
        home_goals = 0
        away_goals = 1
        elo_delta = -17

        self.assertEqual(play_match(expected[0]-elo_delta,
                                    expected[1]+elo_delta,
                                    home_goals,
                                    away_goals),
                         expected)


    def test_two_goal_win(self):
        # March 29, 2016
        # China 2-0 Qatar, in China, WC qualifier
        expected = (1563, 1526)
        home_goals = 2
        away_goals = 0
        elo_delta = 22

        self.assertEqual(play_match(expected[0]-elo_delta,
                                    expected[1]+elo_delta,
                                    home_goals,
                                    away_goals),
                         expected)


    def test_three_goal_win(self):
        # March 29, 2016
        # Dominica 1-4 Martinica, in Dominica, Qualifier
        expected = (966, 1449)
        home_goals = 1
        away_goals = 4
        elo_delta = -8

        self.assertEqual(play_match(expected[0]-elo_delta,
                                    expected[1]+elo_delta,
                                    home_goals,
                                    away_goals),
                         expected)


if __name__ == "__main__":
    unittest.main()
