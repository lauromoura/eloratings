import sys
import pandas as pd
import jinja2

from elo.db import Championship

df = pd.read_csv(sys.argv[1], index_col=0)
data = Championship.from_directory(sys.argv[2])

title_teams = []

def has_title_chances(data):
    return 1 in data.index

def title_chances(data):
    try:
        return data.loc[1]
    except KeyError as e:
        return 0.0

def g_6_chances(data):
    try:
        return data.loc[6]
    except KeyError as e:
        if max(data.index) < 6:
            return 100.0
        else:
            return 0.0

def z_4_chances(data):
    try:
        return 100.0 - data.loc[16]
    except KeyError as e:
        if max(data.index) < 17:
            return 0.0
        else:
            if data.index.contains(15): # Hackish for when 16 is missing...
                return 100 - data.loc[15]
            return 100.0

def positive_class(chances):
    if chances > 80:
        return 'safe'
    elif chances > 50:
        return 'mostly_safe'
    elif chances > 25:
        return 'unlikely'
    elif chances > 10:
        return 'difficult'
    elif chances > 1:
        return 'very_difficult'
    elif chances > 0:
        return 'miracle'
    else:
        return 'impossible'

def negative_class(chances):
    if chances == 100.0:
        return 'impossible'
    elif chances > 80:
        return 'miracle'
    elif chances > 50:
        return 'very_difficult'
    elif chances > 25:
        return 'difficult'
    elif chances > 10 :
        return 'unlikely'
    elif chances > 0:
        return 'mostly_safe'
    else:
        return 'safe'

z4_teams = []
g6_teams = []

for col in df:
    print(col)
    team_data = (df[col].value_counts() / df.shape[0] * 100).sort_index()
    at_least_chances = team_data.cumsum()
    print(at_least_chances)
    title = title_chances(team_data)
    if (title > 0):
        title_teams.append({'name': col, 'chance': title,
                            'class': positive_class(title)})

    g6_teams.append({'name':col, 'chance':g_6_chances(at_least_chances),
                            'class': positive_class(g_6_chances(at_least_chances))})
    z4_teams.append({'name':col, 'chance':z_4_chances(at_least_chances),
                            'class': negative_class(z_4_chances(at_least_chances))})

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))

template = env.get_template('index_template.html')

title_teams.sort(key=lambda x: x['chance'], reverse=True)
g6_teams.sort(key=lambda x: x['chance'], reverse=True)
z4_teams.sort(key=lambda x: x['chance'])

def sorter(*args):
    print(args)
    return args

current_ranking = []
unsorted_ranking = data.current_ranking()
for key in sorted(unsorted_ranking, key=lambda k: unsorted_ranking[k], reverse=True):
    current_ranking.append({
        'name': key,
        'points': int(unsorted_ranking[key])
    })

context = {
    'current_ranking': current_ranking,
    'title_teams': title_teams,
    'g6_teams': g6_teams,
    'z4_teams': z4_teams,
}

# print(df.describe())

# print(data.current_ranking())

with open('index.html', 'w') as handle:
    handle.write(template.render(context))
