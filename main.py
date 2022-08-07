import logging
import urllib.request
import json

FOLDER_ID = ""  # Идентификатор каталога
IAM_TOKEN = ""  # IAM-токен

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

VOICE = int(1)


def get_text_from_voice() -> json:
    with open("user_voice.ogg", "rb") as f:
        data = f.read()

    params = "&".join([
        "topic=general",
        "folderId=%s" % FOLDER_ID,
        "lang=ru-RU"
    ])

    url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=data)
    url.add_header("Authorization", "Bearer %s" % IAM_TOKEN)

    responseData = urllib.request.urlopen(url).read().decode('UTF-8')
    decodedData = json.loads(responseData)
    return decodedData


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    update.message.reply_text(
        'Пришлите свое голосовое сообщение',
    )
    return VOICE


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.'
    )

    return ConversationHandler.END


def voice(update: Update, context: CallbackContext) -> int:
    """Stores the voice and asks for a location."""
    user = update.message.from_user
    voice_file = update.message.voice.get_file()
    voice_file.download('user_voice.ogg')
    logger.info("voice of %s: %s", user.first_name, 'user_voice.ogg')
    update.message.reply_text(
        'Замечательно! Обрабатываю.'
    )
    decodedData = get_text_from_voice()
    if decodedData.get("error_code") is None:
        if decodedData.get("result") == '':
            update.message.reply_text('Прислано пустое сообщение!')
        else:
            update.message.reply_text(
                decodedData.get("result")
            )
            print(decodedData.get("result"))
    else:
        update.message.reply_text('Произошла ошибка, попробуйте позднее!')

    return VOICE


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, voice, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            VOICE: [MessageHandler(Filters.voice, voice)], },
        fallbacks=[CommandHandler('cancel', cancel)],

    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
