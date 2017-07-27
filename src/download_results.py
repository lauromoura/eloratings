#!/usr/bin/env python3

import os
import sys 
import requests
import argparse
from bs4 import BeautifulSoup

# URL_RESULTS = 'http://www.resultados.com/futebol/brasil/serie-a/resultados/'
# URL_SCHEDULE = 'http://www.resultados.com/futebol/brasil/serie-a/calendario/'

URLS = {
    "A": 'http://globoesporte.globo.com/servico/esportes_campeonato/responsivo/widget-uuid/1fa965ca-e21b-4bca-ac5c-bbc9741f2c3d/fases/fase-unica-seriea-2017/rodada/%d/jogos.html',
    "B": 'http://globoesporte.globo.com/servico/esportes_campeonato/responsivo/widget-uuid/c3f406c5-b3b4-4cbe-a6f4-9945b6f70b35/fases/fase-unica-serieb-2017/rodada/%d/jogos.html'
}


def main():

    parser = argparse.ArgumentParser(description='Download results from GE')
    parser.add_argument('rounds', metavar='R', type=int, nargs='+',
            help='number of rounds to get')
    parser.add_argument('--series', metavar='S', type=str,
            help='What series to be downloaded', default="A")
    parser.add_argument('--output-dir', metavar='DIR', type=str,
            help='Output directory for the files. Default current dir', default='.')

    args = parser.parse_args()

    print(args)
    # return

    if not os.path.isdir(args.output_dir):
        print("Output dir must be a valid directory")
        return -1

    for r in range(1, args.rounds[0] + 1):
        print("dowloading round ", r)

        url = URLS[args.series] % r

        req = requests.get(url)
        req.raise_for_status()

        filename = os.path.join(args.output_dir, 'results%02d.html')

        with open(filename % r, 'w') as handle:
            soup = BeautifulSoup(req.text, 'html.parser')
            handle.write(soup.prettify())

    return 0

if __name__ == '__main__':
    sys.exit(main())
