from api_client import get_matches

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
            groups[group_letter]['teams'].setdefault(home, {'played': 0, 'W': 0, 'D': 0 , 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'pts': 0})
            groups[group_letter]['teams'].setdefault(away, {'played': 0, 'W': 0, 'D': 0 , 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'pts': 0})
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
        

if __name__ == "__main__":
    pass