from typing import Literal, List

from database.database import Match, Event
import networkx as nx


class MatchInfoRetriever:
    def __init__(self, match_id):
        self.match_id = match_id
        self.home_team: str = self._get_team_name(home_away="home")
        self.home_team_id: str = self._get_team_id(home_away="home")
        self.away_team: str = self._get_team_name(home_away="away")
        self.away_team_id: str = self._get_team_id(home_away="away")

        self.home_team_players: nx.DiGraph = nx.DiGraph()
        self.away_team_players: nx.DiGraph = nx.DiGraph()

        self._get_team_player_nodes("home")
        self._get_team_player_nodes("away")

        self.home_longest_period_start_time: int = self._get_end_time_point("home")[0]
        self.home_longest_period_end_time: int = self._get_end_time_point("home")[1]

        self.away_longest_period_start_time: int = self._get_end_time_point("away")[0]
        self.away_longest_period_end_time: int = self._get_end_time_point("away")[1]

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

    def _get_end_time_point(self, home_away: Literal["home", "away"]) -> List[int | int]:
        substitution: Event
        team_name = self.home_team if home_away == "home" else self.away_team
        substitution_events: List[Event] = Event.objects(match_id=self.match_id,
                                                         team_name=team_name,
                                                         event_type="player_off")

        current_longest_time: int = 0
        longest_time_pointer: int = 0
        duration_list: List[int] = [0]
        for index, substitution in enumerate(substitution_events):
            duration = substitution.time
            duration_list.append(duration)
            previous_duration = duration_list[index]

            time_difference = duration - previous_duration if duration > previous_duration else 0

            if time_difference > current_longest_time:
                current_longest_time = time_difference
                longest_time_pointer = index

        start_time_point = duration_list[longest_time_pointer]
        end_time_point = duration_list[longest_time_pointer + 1]
        return [start_time_point, end_time_point]

    def _get_the_longest_playtime_players(self, home_away: Literal["home", "away"]):
        end_time_point: int = self._get_end_time_point(home_away)[1]

        team_name = self.home_team if home_away == "home" else self.away_team

        player_off_events: List[Event] = Event.objects(match_id=self.match_id,
                                                       team_name=team_name,
                                                       event_type="player_off")
        player_on_events: List[Event] = Event.objects(match_id=self.match_id,
                                                      team_name=team_name,
                                                      event_type="player_on")

        player_off_events = sorted(player_off_events, key=lambda event: event.time)
        player_on_events = sorted(player_on_events, key=lambda event: event.time)

        player_on: Event
        player_off: Event
        for player_off, player_on in zip(player_off_events, player_on_events):
            assert (player_on.period == player_off.period
                    and player_on.minute == player_off.minute
                    and player_on.second == player_off.second), "The on&off substitution events are not aligned!"

            off_player_id: str = player_off.origin_player
            on_player_id: str = player_on.origin_player

            team_players: nx.DiGraph = self.home_team_players if home_away == "home" else self.away_team_players

            assert off_player_id in team_players, f"player id {off_player_id} is not in {team_name}!"
            current_substitution_time_point: int = player_off.time

            if compare_substitution_time_points(end_time_point, current_substitution_time_point):
                team_players.remove_node(off_player_id)
                team_players.add_node(on_player_id)
            else:
                break

    def _get_team_player_nodes(self, home_away: Literal["home", "away"]):
        match_info: Match = Match.objects(match_id=self.match_id).first()

        if home_away == "home":
            home_players: List[str] = match_info.home_players.keys()
            for home_player in home_players:
                if match_info.home_players[home_player]["start"] == "Start":
                    self.home_team_players.add_node(home_player)

            self._get_the_longest_playtime_players(home_away)

        else:
            away_players: List[str] = match_info.away_players.keys()
            for away_player in away_players:
                if match_info.away_players[away_player]["start"] == "Start":
                    self.away_team_players.add_node(away_player)

            self._get_the_longest_playtime_players(home_away)


def compare_substitution_time_points(end_time_point: int,
                                     current_substitution_time: int) -> bool:
    if current_substitution_time < end_time_point:
        return True

    return False
