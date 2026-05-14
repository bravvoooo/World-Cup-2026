import json
from pathlib import Path
from datetime import datetime, timezone, date, UTC
from api_client import get_matches, get_competition
from pprint import pprint
from zoneinfo import ZoneInfo

def parse_matches(rawlist):
    matches_key = {}
    for match in rawlist:
        matches_key[match['id']] = {
            'home': match['homeTeam']['tla'] if match['homeTeam'] else None,
            'away': match['awayTeam']['tla'] if match['awayTeam'] else None,
            'kickoff': match['utcDate'], 
            'status': match['status'],
            'score': {"home": match['score']['fullTime']['home'], "away": match['score']['fullTime']['away']},
            'stage': match['stage'],
            'group': match['group'][6:] if match['group'] else None,
            'matchday': match['matchday']
        }
    return matches_key

def print_group_matches(parsed_matches, group_letter: str):
    for match_id, match in parsed_matches.items():
        if match['group'] == group_letter:
            print(match['home'], match['away'], match['kickoff'], match['score'], match['matchday'])

def build_standings(parsed_matches):
    groups = {}
    for match in parsed_matches.values():
        if match['stage'] == 'GROUP_STAGE' and match['status'] == 'FINISHED':
            home = match['home']
            away = match['away']
            home_score = match['score']['home']
            away_score = match['score']['away']
            group_letter = match['group']
            groups.setdefault(group_letter, {"teams": {}})
            groups[group_letter]['teams'].setdefault(home, {'tla': home, 'played': 0, 'W': 0, 'D': 0 , 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'pts': 0})
            groups[group_letter]['teams'].setdefault(away, {'tla': away, 'played': 0, 'W': 0, 'D': 0 , 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'pts': 0})
            groups[group_letter]['teams'][home]['played'] += 1
            groups[group_letter]['teams'][away]['played'] += 1
            groups[group_letter]['teams'][home]['GF'] += home_score
            groups[group_letter]['teams'][away]['GF'] += away_score
            groups[group_letter]['teams'][home]['GA'] += away_score
            groups[group_letter]['teams'][away]['GA'] += home_score
            if home_score > away_score:
                groups[group_letter]['teams'][home]['W'] += 1
                groups[group_letter]['teams'][away]['L'] += 1
            elif home_score == away_score:
                groups[group_letter]['teams'][home]['D'] += 1
                groups[group_letter]['teams'][away]['D'] += 1
            else:
                groups[group_letter]['teams'][away]['W'] += 1
                groups[group_letter]['teams'][home]['L'] += 1
    for group in groups.values():
        for team in group['teams'].values():
            team['GD'] = team['GF'] - team['GA']
            team['pts'] = team['W'] * 3 + team['D'] * 1
    return groups
        
def build_tournament(parsed_matches, competition_meta):
    groups = build_standings(parsed_matches)
    knockout = {
        'round_of_32': [],
        'round_of_16': [],
        'quarter_finals': [],
        'semi_finals': [],
        'final': {}
    }
    competition = competition_meta['name']
    season = competition_meta['currentSeason']['startDate'][:4]
    tournament = {
        'competition': competition,
        'season': season, 
        'last_updated': None, #save_tournament updates this
        'groups': groups,
        'matches': parsed_matches,
        'knockout': knockout
    }
    return tournament

def save_tournament(tournament, path):
    tournament['last_updated'] = datetime.now(timezone.utc).isoformat()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as file:
        json.dump(tournament, file, indent=4)

def load_tournament(path: str = 'data/tournament.json'):
    with open(path) as f:
        return json.load(f)

def get_group_table(tournament:dict, letter: str):
    teams = tournament['groups'][letter]['teams']
    sorted_teams = sorted(teams.values(), key=lambda x: (-x['pts'], -x['GD'], -x['GF']))
    return sorted_teams

def get_team(tournament: dict, country_code: str):
    for group in tournament['groups'].values():
        if country_code in group['teams']:
            return group['teams'][country_code]
    raise KeyError(f'Team {country_code} not found in tournament.')

def get_today(tournament: dict, todays_date: date = None):
    '''#get_todays_matchs
    Input 
    tournament, the full tournament dict 
    there will actually not be a todays_date arg because i dont have a use case for it
    
    Output
    Matches that play today and can be seen in order of time
    
    Logic
    create a variable that holds todays date 
    for each match
    parse the kickoff to a UTC datetime
    Convert the timezone from utc to 'America/NewYork' with zoneinfo
    and if the local date is equal to todays date, keep it 
    sort the keepers by kickoff time
    return sorted list of (match_id, match_dict) match tuples'''
    if todays_date is None:
        todays_date = datetime.now(ZoneInfo('America/New_York')).date()
    keepers = []
    for match_id, match_data in tournament['matches'].items():
        kickoff = match_data['kickoff']
        utc_kickoff = datetime.fromisoformat(kickoff)
        local_kickoff = utc_kickoff.astimezone(ZoneInfo('America/New_York'))
        local_date = local_kickoff.date()
        if todays_date == local_date:
            keepers.append((match_id, local_kickoff, match_data))
    keepers.sort(key=lambda x: x[1])
    return keepers

if __name__ == "__main__":
#    save_tournament(build_tournament(parse_matches(get_matches()), get_competition()), 'data/tournament.json')
    loaded = load_tournament('data/tournament.json')
    print(get_today(loaded, date(2024, 7, 2)))