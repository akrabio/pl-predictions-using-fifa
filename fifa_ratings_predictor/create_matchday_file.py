import os
import json


def get_odds():
    return get_from_crawler('winnerodds')[0]['matches']


def get_lineups():
    return get_from_crawler('matchdaylineups')[0]


def get_players():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/player-data/fifa20_players.json') as json_file:
        return json.loads(json_file.read())


def get_from_crawler(spider_name):
    os.system('cd crawler && scrapy crawl {} -o temp-{}.json'.format(spider_name, spider_name))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/crawler/' + 'temp-{}.json'.format(spider_name)) as json_file:
        output = json.loads(json_file.read())
    os.system('cd crawler && rm temp-{}.json'.format(spider_name))
    return output


def create_matchday_object():
    lineups = get_lineups()
    players = get_players()
    output = {'matches': get_odds(), 'teams': {}}

    for _, match in lineups.items():
        for team_name, team in match.items():
            output['teams'][team_name] = {}
            for unit, unit_players in team.items():
                output['teams'][team_name][unit] = []
                for player in unit_players:
                    found = False
                    for fifa_player in players:
                        if fifa_player['name'] == player:
                            found = True
                            if unit == 'goalkeeper':
                                output['teams'][team_name][unit] = fifa_player['info']['rating']
                            else:
                                output['teams'][team_name][unit].append(fifa_player['info']['rating'])
                            break
                    if not found:
                        print('Could not find rating for player {}, please check manually'.format(player))

    return output


def create_matchday_file(date):
    matchday_object = create_matchday_object()
    with open('./data/matchday/matchday_squads_{}.json'.format(date), 'w') as outfile:
        json.dump(matchday_object, outfile, indent=4)


if __name__ == '__main__':
    create_matchday_file('3.11.19')
