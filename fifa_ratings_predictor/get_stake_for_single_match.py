from fifa_ratings_predictor.one_match_simulator import one_match_simulator
import json
import os


def get_teams():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/matchday_squads.json') as json_file:
        return json.loads(json_file.read())


def kelly_criterion(p, b):
    q = 1 - p
    b -= 1
    stake = (b * p - q) / b
    return stake


def get_single_match(home_side, away_side, odds):
    squads_json = get_teams()
    teams = squads_json['teams']
    h_team = teams[home_side]
    a_team = teams[away_side]
    h_goalkeeper = [h_team['goalkeeper']]
    h_defence = h_team['defence']
    h_midfield = h_team['midfield']
    h_attack = h_team['attack']
    a_goalkeeper = [a_team['goalkeeper']]
    a_defence = a_team['defence']
    a_midfield = a_team['midfield']
    a_attack = a_team['attack']
    prob = one_match_simulator(h_goalkeeper, h_defence, h_midfield, h_attack, a_goalkeeper, a_defence, a_midfield,
                               a_attack)
    for bet in [0, 1, 2]:
        stake = (kelly_criterion(prob[bet], odds[bet]))
        print("\nmatch: {}\nstake: {}\nprobability: {}\nodds: {}\n1X2(012): {}\n".format(home_side + ', ' + away_side,
                                                                                         stake, prob[bet], odds[bet],
                                                                                         bet))


if __name__ == '__main__':
    get_single_match("southampton", "chelsea", [4.2, 3.2, 1.6])
