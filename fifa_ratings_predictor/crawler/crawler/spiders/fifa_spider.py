import scrapy
from slugify import slugify

# scrapy crawl <spider name> -o <output file>


class winnerSpider(scrapy.Spider):
    name = "winnerodds"

    def parse(self, response):
        bet_types = response.css('div.event_path-content')

        for index, header in enumerate(response.css('h2.rollup-title').css('span::text').getall()):
            if slugify(header) == '1x2':
                matches = bet_types[index].css('tr.event')
                home_team_names = matches.css('td.outcome-1').css('span.outcomedescription::text').getall()
                away_team_names = matches.css('td.outcome-3').css('span.outcomedescription::text').getall()
                home_win_odds = matches.css('td.outcome-1').css('span.formatted_price::text').getall()
                draw_odds = matches.css('td.outcome-2').css('span.formatted_price::text').getall()
                away_win_odds = matches.css('td.outcome-3').css('span.formatted_price::text').getall()
                break

        matches = []
        for i in range(0, len(home_team_names)):
            match = []
            match.append(heb_to_eng(home_team_names[i]))
            match.append(heb_to_eng(away_team_names[i]))
            match.append(float(home_win_odds[i]))
            match.append(float(draw_odds[i]))
            match.append(float(away_win_odds[i]))
            matches.append(match)

        yield {'matches': matches}

    def start_requests(self):
        yield scrapy.Request(url='https://www.winner.co.il/mainbook/sport-%D7%9B%D7%93%D7%95%D7%A8%D7%92%D7%9C/ep-%D7%90%D7%A0%D7%92%D7%9C%D7%99%D7%94/ep-%D7%A4%D7%A8%D7%9E%D7%99%D7%99%D7%A8-%D7%9C%D7%99%D7%92', callback=self.parse)


class LineupSpider(scrapy.Spider):
    name = "matchdaylineups"

    def parse(self, response):
        matchday = response.css('div.matchday-matches')[0]
        lineups = {}
        home_teams = matchday.css('span.match-home::text').getall()
        away_teams = matchday.css('span.match-away::text').getall()
        for i, match in enumerate(matchday.css('div.loaded-lineups')):
            match_name = home_teams[i] + ',' + away_teams[i]
            lineups[match_name] = {slugify(home_teams[i]): {}, slugify(away_teams[i]): {}}
            # home lineup
            len_home_rows = len(match.css('div.homelineups').css('div.player-row'))
            for index, row in enumerate(match.css('div.homelineups').css('div.player-row')):
                unit = get_unit(index, len_home_rows)
                players_in_row = row.css('div.player::text').getall()
                add_players_to_lineup(lineups, match_name, slugify(home_teams[i]), unit, players_in_row)

            len_away_rows = len(match.css('div.awaylineups').css('div.player-row'))
            for index, row in enumerate(match.css('div.awaylineups').css('div.player-row')):
                unit = get_unit(index, len_away_rows)
                players_in_row = row.css('div.player::text').getall()
                add_players_to_lineup(lineups, match_name, slugify(away_teams[i]), unit, players_in_row)

        yield lineups

    def start_requests(self):
        yield scrapy.Request(url='https://www.sportsgambler.com/football/lineups/england-premier-league/', callback=self.parse)


class FifaSpider(scrapy.Spider):
    name = "fifastats"
    latest_season = "fifa19"

    # TODO - run this for extended period of time to get all players
    def start_requests(self):
        urls = [
            "https://www.fifaindex.com/players/fifa19/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa18/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa17/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa16/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa15/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa14/?league=13&order=desc",
            "https://www.fifaindex.com/players/fifa13/?league=13&order=desc"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for player_row in response.css("tr"):
            link = player_row.css("figure.player a::attr(href)").get()
            if link:
                if "/player/" in link:
                    # extract team
                    team = player_row.css("a.link-team")
                    if team:
                        # only add if player has a team
                        team_name = team.attrib["title"]
                        request = response.follow(link, callback=self.parse_player)
                        # pass additional parameter for the player
                        request.meta["team"] = team_name
                        yield request

        for page_link in response.css(".pagination a.page-link"):
            text = page_link.css("::text").get()
            next = page_link.attrib["href"]
            if "Next" in text:
                print("Next page:", next)
                yield response.follow(next, callback=self.parse)

    def parse_player(self, response):
        name = response.css("img.player").attrib["title"]
        
        team = response.meta["team"]
        if not team:
            # gives the title of the first occurence
            team = (
                response.css("div.team")
                .css("a.link-team")
                .attrib["title"]
            )

        number = (
            response.css("div.team")    # multiple results when multiple teams !
            .css("span.float-right::text")
            .get()
        )

        position = (
            response.css("div.team")    # multiple results when multiple teams !
            .css("a.link-position")
            .attrib["title"]
        )

        rating = response.css(".card-header span.rating::text").get() # first: total, second: potential

        nationality = response.css("a.link-nation").attrib["title"]

        url = response.request.url

        season = url.split("/")[-2]
        if "/fifa" not in url:
            season = self.latest_season

        yield {
            "name": slugify(name),
            "info": {
                "raw team": team,
                "team": slugify(team),
                "position": position,
                "raw name": name,
                "rating": int(rating),
                "kit number": number,
                "nationality": slugify(nationality),
                "season": season,
                "url": url,
            },
        }


class MatchSpider(scrapy.Spider):
    name = "matchlineups"

    # TODO - want the other names - not full names

    def start_requests(self):
        urls_france = [
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2018-2019/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2017-2018/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2016-2017/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2015-2016/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2014-2015/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2013-2014/",
            "http://www.betstudy.com/soccer-stats/c/france/ligue-1/d/results/2012-2013/"
        ]
        urls_england = [
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2018-2019/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2017-2018/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2016-2017/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2015-2016/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2014-2015/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2013-2014/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/results/2012-2013/"
        ]
        urls_germany = [
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2018-2019/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2017-2018/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2016-2017/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2015-2016/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2014-2015/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2013-2014/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/2012-2013/"
        ]
        urls = urls_england
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_fixtures_page)

    def parse_fixtures_page(self, response):
        for info_button in response.css("ul.action-list").css("a::attr(href)"):
            url = info_button.get()
            yield response.follow(url, self.parse_match_page)

    def parse_match_page(self, response):

        home_team, away_team = response.css("div.player h2 a::text").getall()

        date = response.css("em.date").css("span.timestamp::text").get()

        url = response.request.url

        match_number = response.request.url.split("-")[-1].split("/")[0]

        home_goals, away_goals = (
            response.css("div.info strong.score::text").get().split("-")
        )

        for table in response.css("div.table-holder"):
            if table.css("h2::text").get() == "Lineups and subsitutes":
                lineups = table

        home_lineup_css = lineups.css("table.info-table")[0]
        away_lineup_css = lineups.css("table.info-table")[1]

        home_lineup_raw = [
            slugify(x)
            for x in home_lineup_css.css("tr td.left-align")
            .css("a::attr(title)")
            .extract()
        ]
        away_lineup_raw = [
            slugify(x)
            for x in away_lineup_css.css("tr td.left-align")
            .css("a::attr(title)")
            .extract()
        ]

        home_lineup = [
            slugify(x)
            for x in home_lineup_css.css("tr td.left-align").css("a::text").getall()
        ]
        away_lineup = [
            slugify(x)
            for x in away_lineup_css.css("tr td.left-align").css("a::text").getall()
        ]

        home_lineup_number = [
            int(x) for x in home_lineup_css.css("tr td.size23 strong::text").getall()
        ]
        away_lineup_number = [
            int(x) for x in away_lineup_css.css("tr td.size23 strong::text").getall()
        ]

        home_lineup_nationality = [
            slugify(x)
            for x in home_lineup_css.css("tr td.left-align")
            .css("img.flag-ico::attr(alt)")
            .getall()
        ]
        away_lineup_nationality = [
            slugify(x)
            for x in away_lineup_css.css("tr td.left-align")
            .css("img.flag-ico::attr(alt)")
            .getall()
        ]

        yield {
            "match number": int(match_number),
            "info": {
                "date": date,
                "home team": slugify(home_team),
                "away team": slugify(away_team),
                "home goals": int(home_goals),
                "away goals": int(away_goals),
                "home lineup raw names": home_lineup_raw,
                "away lineup raw names": away_lineup_raw,
                "home lineup names": home_lineup,
                "away lineup names": away_lineup,
                "home lineup numbers": home_lineup_number,
                "away lineup numbers": away_lineup_number,
                "home lineup nationalities": home_lineup_nationality,
                "away lineup nationalities": away_lineup_nationality,
                "url": url,
            },
        }


class FifaIndexTeamScraper(scrapy.Spider):
    name = "fifa-index-team"
    latest_season = "fifa19"

    # TODO - run this for extended period of time to get all players

    def start_requests(self):
        urls = [
            "https://www.fifaindex.com/teams/fifa19/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa18/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa17/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa16/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa15/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa14/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa13/?league=13&order=desc",
            "https://www.fifaindex.com/teams/fifa12/?league=13&order=desc",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for team_row in response.css("table.table-teams tr"):
            link = team_row.css("td a.link-team::attr(href)").get()
            if link:
                if "/team/" in link:
                    yield response.follow(link, callback=self.parse_team)

        for page_link in response.css(".pagination a.btn"):
            text = page_link.css("::text").get()
            next = page_link.attrib["href"]
            if "Next" in text and int(next.split("/")[-2]) < 10:    # < 10 for 1. Bundesliga, < 15 for 2. Bundesliga
                print("Next page:", next)
                yield response.follow(next, callback=self.parse)

    def parse_team(self, response):
        team = slugify(response.css("div h1::text").get())
        print(team)

        players_table = response.css('table.table-players')[0]
        for player in players_table.css('tbody tr'):
            player_name_link = player.css("td:nth-child(6) a.link-player")

            name = player_name_link.attrib["title"]

            url = player_name_link.attrib["href"]

            season = url.split("/")[-2]
            if "/fifa" not in url:
                season = self.latest_season

            number = int(player.css("td:nth-child(1)::text").get())
            
            nationality = player.css("td:nth-child(4) a::attr(title)").get()

            for position_option in player.css("span.position::text").getall():
                if position_option not in ["Sub", "Res"]:
                    position = position_option
                    break

            rating = player.css("td:nth-child(5) span.rating::text").get()
            
            yield {
                "name": slugify(name),
                "team": team,
                "position": position,
                "rating": int(rating),
                "number": number,
                "nationality": slugify(nationality),
                "season": season,
                "url": url,
            }

class FixturesSpider(scrapy.Spider):
    name = "fixtures"

    # TODO - want the other names - not full names

    def start_requests(self):
        more_urls = [
            "https://www.betstudy.com/soccer-stats/c/germany/bundesliga/d/fixtures/",
            "http://www.betstudy.com/soccer-stats/c/england/premier-league/d/fixtures/"
        ]
        urls = [
            "https://www.betstudy.com/soccer-stats/c/france/ligue-1/d/fixtures/"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_fixtures)

    @staticmethod
    def parse_fixtures(response):
        for fixture in response.css("tr")[1:]:
            home_team = fixture.css("td.right-align a::text").get()
            away_team = fixture.css("td.left-align a::text").get()
            date = fixture.css("td::text").get()
            yield {
                "date": date,
                "home team": slugify(home_team),
                "away team": slugify(away_team),
                "url": response.request.url,
            }


def get_unit(i, lines_num):
    i = i % lines_num
    if i == 0:
        return 'goalkeeper'
    elif i == 1:
        return 'defence'
    elif i == lines_num - 1:
        return 'attack'
    else:
        return 'midfield'


def add_players_to_lineup(lineups, match_name, team_name, unit, players_in_row):

    for i in range(0, len(players_in_row)):
        players_in_row[i] = slugify(players_in_row[i])

    if match_name in lineups and unit in lineups[match_name][team_name]:
        lineups[match_name][team_name][unit] += players_in_row
    else:
        lineups[match_name][team_name][unit] = players_in_row


def heb_to_eng(team_name):
    translations = {
        "קריסטל פאלאס": 'crystal palace',
        "לסטר": "leicester",
        "אברטון": 'everton',
        "טוטנהאם": 'tottenham',
        "ליברפול": 'liverpool',
        "מנצ׳סטר סיטי": 'man city',
        "צ׳לסי": 'chelsea',
        "ארסנל": 'arsenal',
        "שפילד יונייטד": 'sheffield united',
        "בורנמות׳": 'bournemouth',
        "ברייטון": 'brighton',
        "מנצ׳סטר יונייטד": 'man united',
        "וולבס": 'wolves',
        "ווסטהאם": 'west ham',
        "ברנלי": 'burnley',
        "ניוקאסל": 'newcastle',
        "אסטון וילה": 'aston villa',
        "סאות׳המפטון": 'southampton',
        "נוריץ׳ סיטי": 'norwich',
        "ווטפורד": 'watford'
    }
    return slugify(translations[team_name])