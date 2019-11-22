from fifa_ratings_predictor.one_match_simulator import one_match_simulator
import os
import json
import itertools


def get_teams(date):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + '/data/matchday/matchday_squads_' + date + '.json') as json_file:
        return json.loads(json_file.read())


def kelly_criterion(p, b):
    q = 1 - p
    b -= 1
    stake = (b * p - q) / b
    return stake


def extended_kelly_criterion(all_bets):
    best = -100
    best_bet = None
    sec_best_bet = None
    sec_best_stake = None
    third_best_bet = None
    third_best_stake = None
    for bet in all_bets:
        p = bet[1]
        b = bet[2]
        stake = kelly_criterion(p, b)
        if stake > best:
            if best_bet:
                if sec_best_bet:
                    third_best_bet = sec_best_bet
                    third_best_stake = sec_best_stake
                sec_best_bet = best_bet
                sec_best_stake = best
            best = stake
            best_bet = bet

            print('current best stake: {}\ncurrent matches: {}\nbet: {}'.format(best, bet[0],bet[3]))

    return [(best, best_bet), (sec_best_stake, sec_best_bet), (third_best_stake, third_best_bet)]


def get_all_bets_for_single_match(match_name, match):
    bets = []
    prob = match[0]
    odds = match[1][2:]
    for bet in [0, 1, 2]:
        p = prob[bet]
        b = odds[bet]
        bets.append((match_name, p, b, bet))
    return bets


def get_all_possible_bets(matches, number_of_bets=1):
    possible_bets_per_match = {}
    valid_bets = []
    for match in matches:
        match_name = ', '.join(match[1][:2])
        possible_bets_per_match[match_name] = get_all_bets_for_single_match(match_name, match)
    if number_of_bets == 1:
        for match in possible_bets_per_match:
            valid_bets += possible_bets_per_match[match]
        return valid_bets
    for combination in itertools.combinations(possible_bets_per_match, number_of_bets):
        all_bets_for_matches = []
        for match in combination:
            all_bets_for_matches += possible_bets_per_match[match]
        all_possible_bets_for_combination = itertools.combinations(all_bets_for_matches, number_of_bets)
        for bet in all_possible_bets_for_combination:
            matches_names = [a[0] for a in bet]
            if len(matches_names) == len(set(matches_names)):
                valid_bets.append(bet)
    return valid_bets


def extract_coefficients_from_bets(all_bets, number_of_bets):
    all_bets_reduced = []
    for bet in all_bets:
        if number_of_bets > 1:
            p = 1
            b = 1
            matches = []
            x = []
            for item in bet:
                p *= item[1]
                b *= item[2]
                matches.append(item[0])
                x.append(item[3])
            all_bets_reduced.append((matches, p, b, x))
        else:
            all_bets_reduced.append(bet)
    return all_bets_reduced


def run_kelly_on_squads(number_of_bets, date):
    squads_json = get_teams(date)
    teams = squads_json['teams']
    matches = squads_json['matches']
    probs = []
    for match in matches:
        h_team = teams[match[0]]
        a_team = teams[match[1]]
        match_info = match[5]
        h_goalkeeper = [h_team['goalkeeper']]
        h_defence = h_team['defence']
        h_midfield = h_team['midfield']
        h_attack = h_team['attack']
        a_goalkeeper = [a_team['goalkeeper']]
        a_defence = a_team['defence']
        a_midfield = a_team['midfield']
        a_attack = a_team['attack']
        prob = one_match_simulator(h_goalkeeper, h_defence, h_midfield, h_attack, a_goalkeeper, a_defence, a_midfield, a_attack, match_info)
        probs.append(prob)
    all_bets = get_all_possible_bets(list(zip(probs, matches)), number_of_bets=number_of_bets)
    all_bets_reduced = extract_coefficients_from_bets(all_bets, number_of_bets)
    results = extended_kelly_criterion(all_bets_reduced)
    for result in results:
        if result[0]:
            print('\nstake: {}\nmatches: {}\nprobability of outcome: {}\nodds: {}\n1X2(012): {}\n'.format(result[0], result[1][0],
                                                                                              result[1][1],
                                                                                              result[1][2],
                                                                                              result[1][3]))


if __name__ == '__main__':
    run_kelly_on_squads(2, '9.11.19')

