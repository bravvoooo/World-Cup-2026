def format_team(team, country_code):
    formatted_team = []

    formatted_team.append(f'{country_code}')
    formatted_team.append(f'Played: {team['played']}')
    formatted_team.append(f'W: {team['W']} D: {team['D']} L: {team['L']}')
    formatted_team.append(f'GF: {team['GF']} GA: {team['GA']} GD: {team['GD']}')
    formatted_team.append(f'Points: {team['pts']}')

    return '\n'.join(formatted_team)

def format_group_table(table, letter):
    formatted_table = [f'Group {letter}']

    for team in table:
        formatted_table.append(f'{team['tla']} Played: {team['played']} W: {team['W']} D: {team['D']} L: {team['L']} GF: {team['GF']} GA: {team['GA']} GD: {team['GD']:+d} PTS: {team['pts']}')

    return '\n'.join(formatted_table)

def format_leaderboard(leaderboard):
    formatted = []

    for user in leaderboard:
        formatted.append(f'{user['username']} Total Points: {user['points_earned']}')

    return '\n'.join(formatted)
    
def format_match_results(picks, loaded_tournament):
    formatted_picks = []

    for match_id, pick in picks.items():
        match = loaded_tournament['matches'][match_id]
        formatted_picks.append(f'Match {match['home']} v {match['away']}: {pick['home_score']}-{pick['away_score']} {match_id}')

    return '\n'.join(formatted_picks)
    
def format_user_summary(result):
    user_summary = []

    formatted = format(result['accuracy'], '.2%')
    user_summary.append(f'Total points : {result['total_points']}')
    user_summary.append(f'Accuracy : {formatted}')

    return '\n'.join(user_summary)

def format_yesterday_matches(matches):
    if not matches:
        return ''
    string = ['Yesterday\'s finished matches']
    for match_id, local_kickoff, match_data in matches:
        if match_data['status'] == 'FINISHED':
            score_str = f"FT {match_data['score']['home']} : {match_data['score']['away']}"
        elif match_data['status'] == 'POSTPONED':
            score_str = 'Postponed to a later date'
        else:
            score_str = f'({match_id}) Didn\'t play for unknown reason'
        string.append(f'{match_data['home']} vs {match_data['away']}  {score_str}  Stage: {match_data['stage']}  Matchday: {match_data['matchday']}')
    return '\n'.join(string)

def format_today_matches(matches):
    if not matches:
        return 'No matches are playing today :('
    string = ['Today\'s matches (America/New_York)']
    for match_id, local_kickoff, match_data in matches:
        if match_data['status'] == 'FINISHED':
            score_str = f"FT {match_data['score']['home']} : {match_data['score']['away']}"
        else:
            score_str = '(scheduled)'
        string.append(f'{match_id}  {match_data['home']} vs {match_data['away']}  {local_kickoff.strftime('%I:%M %p')}  {score_str}  Stage: {match_data['stage']}  Matchday: {match_data['matchday']}')
    return '\n'.join(string)

def compose_digest(tournament, now=None):
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from .state import get_todays_matches, get_group_table
    if now is None:
        now = datetime.now(ZoneInfo('America/New_York')).date()
    yesterday_matches = get_todays_matches(tournament, now - timedelta(days=1))
    today_matches = get_todays_matches(tournament, now)
    groups = []
    for _, _, match_data in yesterday_matches:
        if match_data['status'] == 'FINISHED':
            groups.append(match_data['group'])
    blocks = list(set(groups))
    table_list = []
    for b in blocks:
        table_list.append(format_group_table(get_group_table(tournament, b), b))
    table_str = '\n\n'.join(table_list)
    digest = format_yesterday_matches(yesterday_matches) + '\n\n' + format_today_matches(today_matches) + '\n\n' + table_str + '\n' + str(now)
    return digest