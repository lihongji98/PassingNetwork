from mongoengine.fields import *
import mongoengine as meng


class Team(meng.DynamicDocument):
    team_id = ObjectIdField(required=True)
    team_name = StringField()

    meta = {
        'indexes': ['team_id'],
        'db_alias':'default'
    }


# class Match(meng.DynamicDocument):
#     competition = ObjectIdField()
#     home_team = ReferenceField(Team)
#     away_team = ReferenceField(Team)
#     halves = ListField(DictField())
#     match_id = IntField()
    
#     meta = {
#         'indexes': ['competition'],
#         'db_alias':'default'
#     }


class Event(meng.DynamicDocument):
    event_id = ObjectIdField()

    event_code = IntField()    
    event_type = StringField()
    
    team_id = ReferenceField(Team)

    origin_player = IntField()
    origin_pos_x = FloatField()
    origin_pos_y = FloatField()

    minute = IntField()
    second = IntField()
    period = IntField()
    
    match_id = StringField() #ReferenceField(Match)

    team_name = StringField()
    player_name = StringField()
    
    outcome = BooleanField()
    pattern_of_play = IntField() 
    type_detail = IntField()  
    
    destination_pos_x = FloatField()
    destination_pos_y = FloatField()

    extra_detail = IntField() 

    meta = {
        'indexes': ['event_type','origin_player','team'],
        'db_alias':'default'
    }


class Player(meng.DynamicDocument):
    player_id = ObjectIdField()

    first_name = StringField()
    last_name = StringField()
    known_name = StringField()

    team_id = ListField()
    shirt_number = ListField()
    position = ListField()

    starts = IntField()
    minutes = IntField()

    meta = {
        'indexes': ['event_type','origin_player','team'],
        'db_alias':'default'
    }
    
