#!/usr/bin/env python3

import sys
import csv
from bs4 import BeautifulSoup

def write_game(i, game, writer, pending=False):

    date = game.find('div', class_='placar-jogo-informacoes')
    date = '-'.join(date.text.split()[1].split('/')[::-1])

    home_elem = game.find('span', class_='placar-jogo-equipes-mandante')
    meta = home_elem.find('meta')
    home = meta['content']

    away_elem = game.find('span', class_='placar-jogo-equipes-visitante')
    meta = away_elem.find('meta')
    away = meta['content']

    if not pending:
        home_score = int(game.find('span', class_='placar-jogo-equipes-placar-mandante').text)
        away_score = int(game.find('span', class_='placar-jogo-equipes-placar-visitante').text)


    data = {
            'Round': i,
            'Date': date,
            'HomeTeam': home,
            'AwayTeam': away,
            }

    if not pending:
        data['HomeScore'] = home_score
        data['AwayScore'] = away_score

    writer.writerow(data)

def write_file(i, filename, writer):
    '''Loads the game from a result file and write it'''
    print("Parsing %s" % filename)
    with open(filename) as handle:
        soup = BeautifulSoup(handle.read(), 'html.parser')

        games = soup.find_all('a', class_='placar-jogo-link')
        for game in games:
            write_game(i, game, writer)

        for game in soup.find_all('div', class_='placar-jogo'):
            if not game.find_all('a'):
                write_game(i, game, writer, pending=True)


def main():

    filenames = sys.argv[1:]

    print(filenames)
    keys = ['Round', 'Date', 'HomeTeam', 'AwayTeam', 'HomeScore', 'AwayScore']

    with open('out.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, keys)
        writer.writeheader()
        for i, filename in enumerate(filenames):  # Assumes round is always from the beginning
            write_file(i+1, filename, writer)

            
if __name__ == '__main__':
    main()
