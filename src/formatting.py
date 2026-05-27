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