import logging
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .state import regenerate_tournament, load_tournament
from .predictions import score_match_predictions, load_predictions, save_predictions, lock_predictions_for_match
from .formatting import compose_digest, format_match_scoring

logger = logging.getLogger(__name__)

async def poll_matches(context: ContextTypes.DEFAULT_TYPE):
    old_tournament = load_tournament()
    regenerate_tournament()
    new_tournament = load_tournament()
    predictions = load_predictions()

    for match_id, new_match in new_tournament['matches'].items():
        old_match = old_tournament['matches'].get(match_id)
        if old_match is None:        # match exists in new but not old — skip
            continue
        if old_match['status'] == 'FINISHED':   # already processed
            continue
        if datetime.now(ZoneInfo('America/New_York')) >= (datetime.fromisoformat(new_tournament['matches'][match_id]['kickoff']).astimezone(ZoneInfo('America/New_York')) - timedelta(minutes=5)):
            lock_predictions_for_match(match_id, predictions)
        if new_match['status'] != 'FINISHED':   # not done yet
            continue
        # Newly finished. Score it.
        score_match_predictions(match_id, predictions, new_tournament)
        logger.info('Match %s newly finished: %s %s-%s %s, scored', match_id, new_match['home'], new_match['score']['home'], new_match['score']['away'], new_match['away'])

        for user_id, user_data in predictions['users'].items():
            if match_id in user_data['predictions']:
                await _send_match_scoring_message(user_id, match_id, predictions, new_tournament)
    save_predictions(predictions)

async def daily_digest(context: ContextTypes.DEFAULT_TYPE):
    loaded_tournament = load_tournament()
    digest = compose_digest(loaded_tournament)
    predictions = load_predictions()

    for _, user_data in predictions['users'].items():
        chat_id = user_data['chat_id']
        await context.bot.send_message(chat_id=chat_id, text= digest)

async def pre_match_reminders(context: ContextTypes.DEFAULT_TYPE):
    loaded_tournament = load_tournament()
    predictions = load_predictions()

    for match_id, match_data in loaded_tournament['matches'].items():
        kickoff = datetime.fromisoformat(match_data['kickoff']).astimezone(ZoneInfo('America/New_York'))
        now = datetime.now(ZoneInfo('America/New_York'))

        if now >= kickoff - timedelta(hours=1) and now <= kickoff - timedelta(minutes=30):
            for user_id, user_data in predictions['users'].items():
                if match_id not in user_data['predictions']:
                    await context.bot.send_message(chat_id=user_data['chat_id'], text=f'Reminder: {match_data['home']} vs {match_data['away']} kicks off in ~1 hour!\n Submit your prediction: /predict {match_id} <your prediction>')


async def _send_match_scoring_message(user_id, match_id, predictions, tournament, context: ContextTypes.DEFAULT_TYPE):
    prediction = predictions['users'][user_id]['predictions'][match_id]
    match = tournament['matches'][match_id]
    points_earned = prediction['points_earned']
    breakdown = prediction['scoring_breakdown']

    match_str = format_match_scoring(match, prediction, points_earned, breakdown)
    chat_id = predictions['users'][user_id]['chat_id']

    await context.bot.send_message(chat_id=chat_id, text=match_str)