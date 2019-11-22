import json
import os


def get_new_fixtures(week):
    os.system('cd crawler && scrapy crawl todaysresults -a week={} -o temp-todaysresults.json'.format(week))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/crawler/' + 'temp-todaysresults.json', 'r') as json_file:
        output = json.loads(json_file.read())
    os.system('cd crawler && rm temp-todaysresults.json')
    return output[0]['fixtures']


def get_past_fixtures():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/lineup-data/E0/current_season.json', 'r') as json_file:
        return json.loads(json_file.read())


def add_new_fixtures(week):
    fixtures = get_past_fixtures()
    new_fixtures = get_new_fixtures(week)
    fixtures += new_fixtures
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/lineup-data/E0/current_season.json', 'w') as json_file:
        json.dump(fixtures, json_file)


if __name__ == '__main__':
    add_new_fixtures(12)


