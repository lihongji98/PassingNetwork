from mongoengine.fields import *
import mongoengine as meng


class Team(meng.DynamicDocument):
    id = ObjectIdField()
    team_id = StringField()
    team_name = StringField()

    meta = {
        'indexes': ['team_id'],
        'db_alias': 'default'
    }


class Match(meng.DynamicDocument):
    competition_id = ObjectIdField()
    home_team_id = StringField()
    away_team_id = StringField()
    home_team = StringField()
    away_team = StringField()
    match_id = StringField()
    home_players = DictField(
        id=DictField(
            known_name=StringField(),
            shirt_number=IntField(),
            position=StringField(),
            start=StringField(),
            minutes=IntField()
        )
    )
    away_players = DictField(
        id=DictField(
            known_name=StringField(),
            shirt_number=IntField(),
            position=StringField(),
            start=StringField(),
            minutes=IntField()
        )
    )

    meta = {
        'indexes': ['competition'],
        'db_alias': 'default'
    }


class Event(meng.DynamicDocument):
    id = ObjectIdField()

    event_code = IntField()
    event_type = StringField()

    team_id = StringField()

    origin_player = StringField()
    origin_pos_x = FloatField()
    origin_pos_y = FloatField()

    minute = IntField()
    second = IntField()
    period = IntField()
    time = IntField()

    match_id = StringField()  # ReferenceField(Match)

    team_name = StringField()
    player_name = StringField()

    outcome = IntField()
    pattern_of_play = IntField()
    type_detail = IntField()

    destination_pos_x = FloatField()
    destination_pos_y = FloatField()

    extra_detail = IntField()

    xthreat = FloatField(default=0.0)

    meta = {
        'indexes': ['event_type', 'origin_player', 'team'],
        'db_alias': 'default'
    }


class Player(meng.DynamicDocument):
    id = ObjectIdField()

    player_id = StringField()

    first_name = StringField()
    last_name = StringField()
    known_name = StringField()

    team_id = ListField()
    shirt_number = IntField()
    position = ListField()

    starts = IntField()
    apps = IntField()
    minutes = IntField()
    time = IntField()

    meta = {
        'indexes': ['player_id'],
        'db_alias': 'default'
    }


class Pass(meng.DynamicDocument):
    id = ObjectIdField()

    pass_id = StringField()
    match_id = StringField()
    team_id = StringField()

    minute = IntField()
    second = IntField()
    period = IntField()

    origin_player = StringField()
    destination_player = StringField()

    outcome = IntField()
    origin_pos_x = FloatField()
    origin_pos_y = FloatField()

    destination_pos_x = FloatField()
    destination_pos_y = FloatField()

    offside = IntField()
    possession = IntField()
    sequence = IntField()

    meta = {
        'indexes': ['player_id', 'team_id', 'match_id'],
        'db_alias': 'default'
    }

