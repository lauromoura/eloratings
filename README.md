# Elo ratings for Campeonato Brasileiro

These are a set of tools to explore using the [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system) on the
results and fixtures of the 2016 Campeonato Brasileiro Serie A. Most of it
currently written in python, with plans to offer a web page with the latest
information.

## The System

The Elo rating provides a way of predicting the expected outcome of a match
between two ranked players. After the match, the rating of the players are
updated based on the outcome. For example, if an player is expected to win and
actually loses, he'll have his rating decreased. The value of change also
depends on how large was the winning margin and how "upset" was the result. A
lower ranked team winning against a higher ranked team will give a great change
in ratings than if the higher ranked team had won.

We chose to use the World Football Elo Ratings system, with minor changes. Some
variables are provisional, subject to changes after the prediction accuracy
measurements are sorted out. As of now, the k (base match weight) is 40,
equivalent to the WC qualifier/continental tournament level for nations. Also,
home matches give a 100 points 

[World Football Elo Ratings system](http://www.eloratings.net/system.html)

## Initial ratings

For the initial ratings, the classification of the 2015 tournament was used,
with the promoted teams from Serie B placed on the bottom 4 positions. The 10th
placed team was given the "average" rating of 1500. Each position above and
below was given a 5 point increase/decreased respectively.

## On predictions

The Elo system provides a probability of 'winning' for each side of a match but
has now explicit definition for the odds of a draw. Instead, it gives half the
value for the swing value for each team. For example, if winning would give the
home team 20 points and take 20 from the away team, in case of a draw it would
change this to a 10 point swing for each side.

To account for draws probability, the results from the historical data of the
top 100 nations according to the current World Elo Ratings were analysed. The
*total* ratio of draws/game was shown to be somewhat similar for all teams,
around 25%. Higher and lower-rated teams had slight less draws than middle-rated
teams.

With this in mind, the draw ratio was modeled as a quadratic function with the
following definitions:

* Odds of draw for a game with expected elo winning probability of 0%: 5%
* Odds of draw for a game with expected elo winning probability of 100%: 5%
* Odds of draw for a game with even elo winning probability (50%): 25%

Given the draw probability, the actual winning probability for the home team is
defined as:

* elo expected win probability * (1 - draw probability)

And the away team win probability is given by

* 1 - actual home win probability - draw_probability

## Things to do

* Define a way to measure the accuracy of the predictions.
* Add support to simulate future fixtures and get the odds of future results.
* Define a persistence schema to avoid recalculate everything.
* Support neutral field matches.
