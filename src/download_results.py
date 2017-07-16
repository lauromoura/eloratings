#!/usr/bin/env python3

import requests
import argparse
from bs4 import BeautifulSoup


# URL_RESULTS = 'http://www.resultados.com/futebol/brasil/serie-a/resultados/'
# URL_SCHEDULE = 'http://www.resultados.com/futebol/brasil/serie-a/calendario/'

BASE_URL = 'http://globoesporte.globo.com/servico/esportes_campeonato/responsivo/widget-uuid/1fa965ca-e21b-4bca-ac5c-bbc9741f2c3d/fases/fase-unica-seriea-2017/rodada/%d/jogos.html'


def main():

    parser = argparse.ArgumentParser(description='Download results from GE')
    parser.add_argument('rounds', metavar='R', type=int, nargs='+', help='number of rounds to get')

    args = parser.parse_args()

    for r in range(1, args.rounds[0] + 1):
        print("dowloading round ", r)

        url = BASE_URL % r

        req = requests.get(url)
        req.raise_for_status()

        with open('results%02d.html' % r, 'w') as handle:
            soup = BeautifulSoup(req.text, 'html.parser')
            handle.write(soup.prettify())

if __name__ == '__main__':
    main()
