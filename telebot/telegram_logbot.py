from telegram.ext import Updater, CommandHandler
import requests


class Telebot:

    def __init__(self, token):
        self.token = token
        self.chat_ids = self.import_chat_ids()
        print("Chat ids: ")
        for c_id in self.chat_ids:
            print(c_id)
        self.bot_text = "Not started yet"

    @staticmethod
    def import_chat_ids():
        chat_ids = []
        with open("telebot/users.txt", "r") as f:
            for line in f.readlines():
                chat_ids.append(line)
        return chat_ids

    def save_chat_ids(self):
        with open("telebot/users.txt", "w") as f:
            for c_id in self.chat_ids:
                f.write(str(c_id))

    def main(self):
        updater = Updater(token=self.token, use_context=True)
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)
        situation_handler = CommandHandler('situation', self.situation)
        dispatcher.add_handler(situation_handler)
        abort_handler = CommandHandler('abort', self.abort)
        dispatcher.add_handler(abort_handler)
        updater.start_polling()

    def start(self, update, context):
        text = "Ok! I will now start giving you updates about the test!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        if update.effective_chat.id in self.chat_ids:
            pass
        else:
            self.chat_ids.append(update.effective_chat.id)
        self.save_chat_ids()

    def stop(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ok!I won't bother you anymore....")
        if update.effective_chat.id in self.chat_ids:
            pass
        else:
            self.chat_ids.append(update.effective_chat.id)
        self.save_chat_ids()

    def situation(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.bot_text)

    @staticmethod
    def abort(update, context):
        text = "ABORTED"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def send_message(self, bot_message):
        response = ""
        for cid in self.chat_ids:
            send_text = 'https://api.telegram.org/bot' + self.token + '/sendMessage?chat_id=' + cid + '&parse_mode' \
                                                                                                      '=Markdown&text' \
                                                                                                      '=' + bot_message
            response = requests.get(send_text)
        return response


if __name__ == "__main__":
    from credentials import bot_token
    t = Telebot(bot_token)
    t.main()
