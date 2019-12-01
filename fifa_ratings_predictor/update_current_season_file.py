import json
import os


def get_new_fixtures(week):
    os.system('cd crawler && scrapy crawl todaysresults -a week={} -o temp-todaysresults.json'.format(week))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/crawler/' + 'temp-todaysresults.json', 'r') as json_file:
        output = json.loads(json_file.read())
    os.system('cd crawler && rm temp-todaysresults.json')
    return output[0]['fixtures'], output[0]['match_numbers']


def get_past_fixtures():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/lineup-data/E0/current_season.json', 'r') as json_file:
        fixtures = json.loads(json_file.read())
        match_numbers = [item['match number'] for item in fixtures]
        return fixtures, match_numbers


def add_new_fixtures(week):
    fixtures, match_numbers = get_past_fixtures()
    new_fixtures, new_match_numbers = get_new_fixtures(week)
    fixtures_to_add = []
    for index, fixture in enumerate(new_fixtures):
        if new_match_numbers[index] not in match_numbers:
            fixtures_to_add.append(fixture)
    fixtures += fixtures_to_add
    fixtures = sorted(fixtures, key=lambda item: item['match number'])
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/lineup-data/E0/current_season.json', 'w') as json_file:
        json.dump(fixtures, json_file)


if __name__ == '__main__':
    add_new_fixtures(0)


