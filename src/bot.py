import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from datetime import date
from .formatting import format_group_table, format_team
from .state import load_tournament, get_group_table, get_todays_matches, get_team


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USAGE = """Usage:
    /standings <group_letter>
    /today
    /predict <match_id> <prediction score>
    /team <country_code>
    /leaderboard
    /mypicks
    /summary"""

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

if __name__ == '__main__':

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    standings_handler = CommandHandler('standings', standings)
    start_handler = CommandHandler('start', start)
    today_handler = CommandHandler('today', today)
    team_handler = CommandHandler('team', team)

    application.add_handler(team_handler)
    application.add_handler(today_handler)
    application.add_handler(start_handler)
    application.add_handler(standings_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
