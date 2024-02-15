from typing import Literal

from database.database import Match


class MatchInfoRetriever:
    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team: str = self._get_team_name(home_away="home")
        self.home_team_id: str = self._get_team_id(home_away="home")
        self.away_team: str = self._get_team_name(home_away="away")
        self.away_team_id: str = self._get_team_id(home_away="away")

    def _get_team_name(self, home_away: Literal["home", "away"]):
        current_match: Match = Match.objects(match_id=self.match_id).first()

        if home_away == "home":
            home_team = current_match.home_team
            return home_team
        else:
            away_team = current_match.away_team
            return away_team

    def _get_team_id(self, home_away: Literal["home", "away"]):
        current_match: Match = Match.objects(match_id=self.match_id).first()
        if home_away == "home":
            home_team_id = current_match.home_team_id
            return home_team_id
        else:
            away_team_id = current_match.away_team_id
            return away_team_id

