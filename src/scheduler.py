import logging
from telegram.ext import ContextTypes
from .state import regenerate_tournament, load_tournament
from .predictions import score_match_predictions, load_predictions, save_predictions
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
        if new_match['status'] != 'FINISHED':   # not done yet
            continue
        # Newly finished. Score it.
        score_match_predictions(match_id, predictions, new_tournament)
        logger.info('Match %s newly finished: %s %s-%s %s, scored', match_id, new_match['home'], new_match['score']['home'], new_match['score']['away'], new_match['away'])

        for user_id, user_data in predictions['users'].items():
            if match_id in user_data['predictions']:
                await send_match_scoring_message(user_id, match_id, predictions, new_tournament)
    save_predictions(predictions)

async def daily_digest(context: ContextTypes.DEFAULT_TYPE):
    loaded_tournament = load_tournament()
    digest = compose_digest(loaded_tournament)
    predictions = load_predictions()

    for _, user_data in predictions['users'].items():
        chat_id = user_data['chat_id']
        await context.bot.send_message(chat_id=chat_id, text= digest)

async def send_match_scoring_message(user_id, match_id, predictions, tournament, context: ContextTypes.DEFAULT_TYPE):
    prediction = predictions['users'][user_id]['predictions'][match_id]
    match = tournament['matches'][match_id]
    points_earned = prediction['points_earned']
    breakdown = prediction['scoring_breakdown']

    match_str = format_match_scoring(match, prediction, points_earned, breakdown)
    chat_id = predictions['users'][user_id]['chat_id']

    await context.bot.send_message(chat_id=chat_id, text=match_str)