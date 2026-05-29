import os
import logging
from dotenv import load_dotenv
from telegram import Update, User
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
from zoneinfo import ZoneInfo
from .formatting import format_group_table, format_team, format_match_results
from .state import load_tournament, get_group_table, get_todays_matches, get_team
from .predictions import submit_prediction, save_predictions, get_leaderboard, load_predictions
from .scheduler import poll_matches

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

USAGE = """Usage:
    /standings <group_letter>
    /today
    /predict <match_id> <prediction score>
    /team <country_code>
    /leaderboard
    /summary
    """

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name
    chat_id = update.message.chat_id
    now = datetime.now(ZoneInfo('America/New_York'))
    loaded_predictions = load_predictions()
    loaded_predictions['users'].setdefault(user_id, {'username': first_name, 'joined_at': now.isoformat(), 'chat_id': chat_id, 'predictions': {}})
    save_predictions(loaded_predictions)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome — I'm your WC 2026 tracker." + '\n' + USAGE
    )

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 1:
        loaded_tournament = load_tournament()
        letter = context.args[0]
        try:
            table = get_group_table(loaded_tournament, letter)
        except KeyError:
            first_char = min(loaded_tournament['groups'])
            last_char = max(loaded_tournament['groups'])
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"No group '{letter}' found. Try something from {first_char}-{last_char}.")
            return
        string = format_group_table(table, letter)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=string)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=USAGE)
        return

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loaded_tournament = load_tournament()
    matches = get_todays_matches(loaded_tournament)
    if not matches:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='No matches are playing today :(')
        return
    string = ['Today\'s matches (America/New_York)']
    for match_id, local_kickoff, match_data in matches:
        if match_data['status'] == 'FINISHED':
            score_str = f"FT {match_data['score']['home']} : {match_data['score']['away']}"
        else:
            score_str = '(scheduled)'
        string.append(f'{match_id}  {match_data['home']} vs {match_data['away']}  {local_kickoff.strftime('%I:%M %p')}  {score_str}  Stage: {match_data['stage']}  Matchday: {match_data['matchday']}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(string))

async def team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 1:
        loaded_tournament = load_tournament()
        country_code = context.args[0]
        try:
            team = get_team(loaded_tournament, country_code)
        except KeyError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{country_code} doesn\'t exist in this tournament unfortunately. Try another?')
            return
        await context.bot.send_message(chat_id=update.effective_chat.id, text=format_team(team, country_code))

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 2:
        loaded_tournament = load_tournament()
        loaded_predictions = load_predictions()
        match_id = context.args[0]
        score = context.args[1]
        score = score.split('-')
        if len(score) != 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Need exactly two values, like 1-2')
            return
        if not (score[0].isdigit() and score[1].isdigit()):
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Both values need to be digits.')
            return
        home = int(score[0])
        away = int(score[1])
        if home > 9 or away > 9:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Values should be 10 or less')
            return
        try:
            submitting_pred = submit_prediction( str(update.effective_user.id), match_id, home, away, loaded_tournament, loaded_predictions)
        except (KeyError, ValueError) as e:
           await context.bot.send_message(chat_id=update.effective_chat.id, text=e.args[0])
           return
        save_predictions(submitting_pred)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Prediction saved.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=USAGE)
        return

async def mypicks(update:Update, context: ContextTypes.DEFAULT_TYPE):
    loaded_tournament = load_tournament()
    loaded_predictions = load_predictions()
    picks = loaded_predictions['users'].get(str(update.effective_user.id), {}).get('predictions', {})
    if not picks:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='You haven\'t predicted yet.')
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=format_match_results(picks, loaded_tournament))

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    standings_handler = CommandHandler('standings', standings)
    start_handler = CommandHandler('start', start)
    today_handler = CommandHandler('today', today)
    team_handler = CommandHandler('team', team)
    predict_handler = CommandHandler('predict', predict)
    mypicks_handler = CommandHandler('mypicks', mypicks)

    application.job_queue.run_repeating(poll_matches, interval=1800, first=10)

    application.add_handler(mypicks_handler)
    application.add_handler(team_handler)
    application.add_handler(today_handler)
    application.add_handler(start_handler)
    application.add_handler(standings_handler)
    application.add_handler(predict_handler)
    application.add_handler(unknown_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)