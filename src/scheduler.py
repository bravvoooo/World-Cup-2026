import logging
from telegram.ext import ContextTypes
from .state import regenerate_tournament, load_tournament
from .predictions import score_match_predictions, load_predictions, save_predictions

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
    save_predictions(predictions)