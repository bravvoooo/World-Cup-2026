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

if __name__ == "__main__":
    raw = get_matches()
    parsed = parse_matches(raw['matches'])
    
    # Find a knockout match and print it
    for match_id, match_data in parsed.items():
        if match_data['stage'] != 'GROUP_STAGE':
            print(match_id, match_data)
            break