from datetime import datetime
from typing import Final

import pytz
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN: Final = '6875683083:AAHLjH_Eju7CpN3y-m4mdos7afnvGM8d9dY'

BOT_USERNAME: Final = '@Badminton_Slot_helper_bot'

PLAY_MANIA_ID = "a30f4a85-0980-4a7c-b09e-da4b3ab98d9e"
INFINITY_ID = "e5ef8ac2-e606-4c7a-96ba-561b73f64684"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks fro chatting with me! I am banana')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am banana! Please type something so I can respond!')


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')


async def slots_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(handle_slot_response("PLAY_MANIA", PLAY_MANIA_ID), parse_mode=ParseMode.HTML)
    await update.message.reply_text(handle_slot_response("INFINITY_BADMINTON_ARENA", INFINITY_ID),
                                    parse_mode=ParseMode.HTML)


def handle_slot_response(venue: str, venue_id: str) -> str:
    utc_now = datetime.utcnow()
    india_timezone = pytz.timezone('Asia/Kolkata')
    india_now = utc_now.astimezone(india_timezone)
    current_date = india_now.strftime("%Y-%m-%d")
    url = (f'https://playo.club/book-api/v5/availability/{venue_id}/SP5/{current_date}'
           '/?userId=8871905885&deviceType=99')
    headers = {
        'Authorization': 'b4ee93df154de37b0e38aa6a5dfda071aa751bfa'
    }
    message: str = ""
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        fulldata = response.json()
        data = fulldata['data']
        court_list = data.get('courtList', [])
        current_time = india_now.strftime("%H")
        hours_to_check = range(int(current_time)+1, 23)
        message += f"<b>{venue}</b>\n\n"
        for hour in hours_to_check:
            courts_with_status_1 = []

            # Format the hour to match the time format in the data
            target_time = f"{hour:02d}:00:00"

            # Iterate through each court
            for court in court_list:
                court_name = court.get('courtName')
                slot_info = court.get('slotInfo', [])

                # Find the slot corresponding to the target time
                target_slot = next((slot for slot in slot_info if slot.get('time') == target_time), None)

                # Check if the slot exists and its status is 1
                if target_slot and target_slot.get('status') == 1:
                    courts_with_status_1.append(court_name)

            # Print the result for the hour
            if courts_with_status_1:
                hour_message = f"<b>{hour} to {hour + 1} :</b>\n"
                courts_message = '\n'.join(courts_with_status_1)

                # Combine and append to the main message
                message += f"{hour_message}{courts_message}\n\n"
                
            else:
                message += f"<b>{hour} to {hour + 1} :</b> \nNo courts available\n\n"
    else:
        print(f"Request failed with status code {response.status_code}")

    return message


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I am good!'

    return 'Stop wasting time. Check why you opened this chat....'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    counter = 0
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('slots', slots_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
