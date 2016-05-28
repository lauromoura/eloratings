import csv
import os
import logging
from datetime import datetime


DATE_FORMAT = "%d/%m/%Y"


def parse_date(date_str):
    '''Converts the datestring to a datetime object'''
    return datetime.strptime(date_str, DATE_FORMAT)


def parse_value(val):
    '''Try to guess a value from a string and convert it'''

    try:
        return parse_date(val)
    except ValueError as e:
        pass

    try:
        return int(val)
    except ValueError as e:
        pass

    return val.strip()


def parse_match(match_str, keys):
    '''Converts the match string to a dict'''
    return {k: parse_value(v) for k, v in zip(keys, match_str)}


def parse_rounds(path):
    '''Parse the rounds, returning a list with the dates of the rounds'''

    filename = os.path.join(path, 'rounds.csv')
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        next(reader)  # Skip header
        return [parse_date(date_str) for (_, date_str) in reader]


def parse_matches(path):
    '''Parse the matches, returning a list of them'''

    filename = os.path.join(path, 'matches.csv')
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        keys = next(reader)  # Skip header
        return [parse_match(row, keys) for row in reader if row]

def parse_initial(path):
    '''Parse the initial ratings. Returning a dict with the team as key'''

    filename = os.path.join(path, 'initial.csv')
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        keys = next(reader)  # Skip header
        return {t: int(r) for _, t, r in reader}
