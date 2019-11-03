import os
import json
from fifa_ratings_predictor.league_model import LeagueTable


def get_odds():
    return get_from_crawler('winnerodds')['matches']


def get_lineups():
    return get_from_crawler('matchdaylineups')


def get_current_fixtures(week):
    return get_from_crawler('todaysresults', 'week=' + week)['fixtures']


def get_fixtures():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/lineup-data/E0/current_season.json') as json_file:
        return json.loads(json_file.read())


def get_players():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/player-data/fifa20_players.json') as json_file:
        return json.loads(json_file.read())


def get_from_crawler(spider_name, arg=None):
    os.system('cd crawler && scrapy crawl {} -o temp-{}.json'.format(spider_name, spider_name))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/crawler/' + 'temp-{}.json'.format(spider_name), 'r') as json_file:
        output = json.loads(json_file.read())
    os.system('cd crawler && rm temp-{}.json'.format(spider_name))
    return output[0]


def create_league_object():
    league = LeagueTable()
    fixtures = get_fixtures()
    for fixture in fixtures:
        fixture = fixture['info']
        league.add_result(fixture['home team'], fixture['away team'], fixture['home goals'], fixture['away goals'])
    return league


def create_matchday_object():
    league = create_league_object()
    lineups = get_lineups()
    players = get_players()
    output = {'matches': get_odds(), 'teams': {}}
    for i, match in enumerate(output['matches']):
        home_team_info = league.get_team_info(match[0])
        away_team_info = league.get_team_info(match[1])
        league_info = [home_team_info['position'], home_team_info['points'], home_team_info['played'],
                       home_team_info['goals'], home_team_info['conceded'], sum(home_team_info['form']) / 5,
                       away_team_info['position'], away_team_info['points'], away_team_info['played'],
                       away_team_info['goals'], away_team_info['conceded'], sum(away_team_info['form']) / 5]
        match.append(league_info)

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
