import datetime

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello. Welcome to iGo, the application that will allow you to go from one place in Barcelona to another in the shortest possible time. Let's get started!")

def where_map(update, context):
    lat, lon = update.message.location.latitude, update.message.location.longitude
    context.user_data['loc'] = (lat, lon)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Ets a les coordenades %f %f, user_id : %i' % (lat, lon, update.effective_chat.id))

def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Here is a guide to the orders you will use. \n ·/authors will show you the name of the authors of the project. \n · /go DESTINATION will show you a map where it will show you the shortest way to go from one place in the city of Barcelona to another taking into account the concept of iSpeed. \n ")

def authors(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="The authors of that app are Àngel Mola Audí and David Benedicto Sedas.")
def pos(update, context):
    query = update.message.text[5:]
    #
    query_splitted = query.split()
    try:
        if len(query_splitted) == 2 and float(query_splitted[0]) and float(query_splitted[1]):
            lat = float(query_splitted[0])
            lon = float(query_splitted[1])
            context.user_data['loc'] = (lat, lon)

    except ValueError:
        #lat, lon =

        pass

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ubicacio actualitzada")


def go(update,context):
    query = update.message.text[4:]
    if not context.user_data:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Envia la teva ubicacio primer!")
    else:
        fitxer = "{}.png".format(update.effective_chat.id)
        #get_shortest_path_with_ispeeds_lat_lon(context.user_data['loc'][0], context.user_data['loc'][1], msg)
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(fitxer, 'rb'))
        os.remove(fitxer)

def where(update, context):
    if context.user_data:
        msg = f"{context.user_data['loc'][0]}, {context.user_data['loc'][1]}"
    else:
        msg = "Has d'enviar la teva ubicacio abans"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg)

TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(MessageHandler(Filters.location, where_map))
dispatcher.add_handler(CommandHandler('pos', pos))
dispatcher.add_handler(CommandHandler('where', where))



updater.start_polling()
