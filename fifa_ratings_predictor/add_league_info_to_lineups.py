import json
from fifa_ratings_predictor.league_model import LeagueTable
from fifa_ratings_predictor import constants


def get_lineups():
    with open("./data/lineup-data/E0/match-lineups.json") as json_file:
        return sorted(json.load(json_file), key=lambda x: x["match number"])


def add_info_to_matches(matches):
    league = LeagueTable()
    updated_matches = []
    for match in matches:
        home_team = constants.LINEUP_TO_PLAYER_TEAM_MAPPINGS["ALL"][match["info"]["home team"]]
        away_team = constants.LINEUP_TO_PLAYER_TEAM_MAPPINGS["ALL"][match["info"]["away team"]]
        home_goals_scored = match["info"]["home goals"]
        away_goals_scored = match["info"]["away goals"]
        league.add_result(home_team, away_team, home_goals_scored, away_goals_scored)
        home_team_info = league.get_team_info(home_team)
        away_team_info = league.get_team_info(away_team)
        match['info']["home position"] = home_team_info["position"]
        match['info']["away position"] = away_team_info["position"]
        match['info']["home points"] = home_team_info["points"]
        match['info']["away points"] = away_team_info["points"]
        match['info']["home goals total"] = home_team_info["goals"]
        match['info']["away goals total"] = away_team_info["goals"]
        match['info']["home conceded total"] = home_team_info["conceded"]
        match['info']["away conceded total"] = away_team_info["conceded"]
        match['info']["home played"] = home_team_info["played"]
        match['info']["away played"] = away_team_info["played"]
        match['info']["home form"] = sum(home_team_info["form"]) / len(home_team_info["form"])
        match['info']["away form"] = sum(away_team_info["form"]) / len(away_team_info["form"])
        updated_matches.append(match)

    return updated_matches


def save_to_file(data):
    path = "./data/lineup-data/E0/updated-match-lineups.json"
    with open(path, 'a') as outfile:
        json.dump(data, outfile)


def update_match_lineups():
    data = get_lineups()
    updated = add_info_to_matches(data)
    save_to_file(updated)


if __name__ == "__main__":
    update_match_lineups()





