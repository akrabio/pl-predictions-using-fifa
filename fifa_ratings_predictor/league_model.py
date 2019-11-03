from collections import OrderedDict


class LeagueTable:
    def __init__(self):
        self.__table = {}

    def add_result(self, home_team, away_team, home_team_goals, away_team_goals):
        for team in [home_team, away_team]:
            if team not in self.__table:
                self.__table[team] = {"position": -1, "points": 0, "goals": 0, "conceded": 0, "played": 0, "win": 0,
                                      "draw": 0, "lose": 0, "form": []}
        if home_team_goals > away_team_goals:
            self.__table[home_team]["points"] += 3
            self.__table[home_team]["win"] += 1
            self.__table[away_team]["lose"] += 1
            update_form(self.__table, home_team, 1)
            update_form(self.__table, away_team, -1)
        elif home_team_goals < away_team_goals:
            self.__table[away_team]["points"] += 3
            self.__table[home_team]["lose"] += 1
            self.__table[away_team]["win"] += 1
            update_form(self.__table, away_team, 1)
            update_form(self.__table, home_team, -1)
        else:
            self.__table[home_team]["points"] += 1
            self.__table[away_team]["points"] += 1
            self.__table[home_team]["draw"] += 1
            self.__table[away_team]["draw"] += 1
            update_form(self.__table, away_team, 0)
            update_form(self.__table, home_team, 0)

        self.__table[home_team]["goals"] += home_team_goals
        self.__table[home_team]["conceded"] += away_team_goals
        self.__table[away_team]["goals"] += away_team_goals
        self.__table[away_team]["conceded"] += home_team_goals

        self.__table[away_team]["played"] += 1
        self.__table[home_team]["played"] += 1

        self.__table = OrderedDict(sorted(self.__table.items(), key=lambda item: item[1]['points'], reverse=True))
        for index, team in enumerate(self.__table):
            self.__table[team]["position"] = index + 1

    def get_team_info(self, team_name):
        return self.__table[team_name] if team_name in self.__table else None


def update_form(table, team, value):
    form = table[team]["form"]
    form.insert(0, value)
    if len(form) > 5:
        form.pop()

    table[team]["form"] = form


if __name__ == "__main__":
    league = LeagueTable()
    league.add_result("liverpool", "man united", 3, 1)
    league.add_result("newcastle", "arsenal", 3, 1)
    league.add_result("newcastle", "arsenal", 1, 1)
    league.add_result("newcastle", "arsenal", 3, 5)
    league.add_result("newcastle", "arsenal", 3, 3)
    league.add_result("newcastle", "arsenal", 3, 9)
    league.add_result("newcastle", "arsenal", 3, 4)
