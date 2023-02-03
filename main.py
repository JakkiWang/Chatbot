import logging

from telegram import __version__ as TG_VER

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonPollType, Sticker, InlineKeyboardButton, \
	InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler, CallbackQueryHandler, \
	ConversationHandler, PollAnswerHandler
from telegram.constants import ParseMode
import random
import datetime
from transformers import pipeline
import prettytable as pt
import re
import emoji
from dbhelper import DBHelper_user_value, DBHelper_user_status, DBHelper_user_dialog, DBHelper_user_result
from emoji_map import emoji_mapping, emoji_score_mapping, POS_EMO, NEU_EMO, NEG_EMO

TOKEN = "please ask jiaqi by email if necessary"


classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


SCORE, WORD, EMOJI, QUESTION, QUESTION2 = range(5)


### Deal with database ###

def get_status(user_id):
	"""
	get current status for user
	user_id: the chat id of the conversation, turn: the number of conversation
	"""
	db_connect = DBHelper_user_status()
	return db_connect.get_value(user_id)


def change_status(user_id, date, status):
	"""change current status for user"""
	db_connect = DBHelper_user_status()
	db_connect.change_value(user_id, date, status)
	return

def set_status(user_id, date, status):
	"""set status for user"""
	db_connect = DBHelper_user_status()
	db_connect.add_value(user_id, date, status)

def record_conversation(user_id, date, turn, content):
	db_connect = DBHelper_user_dialog()
	db_connect.add_value(user_id, date, turn, content)

def get_conversation(user_id, date, turn):
	db_connect = DBHelper_user_dialog()
	return db_connect.get_value(user_id, date, turn)

def record_result(user_id, date, turn, content):
	db_connect = DBHelper_user_result()
	db_connect.add_value(user_id, date, turn, content)

def get_result(user_id, date, turn):
	db_connect = DBHelper_user_result()
	return db_connect.get_value(user_id, date, turn)


def get_values(user_id, date):
	db_connect = DBHelper_user_value()
	return  db_connect.get_values_for_day(user_id, date)

def set_values(user_id, date, time, value=None):
	db_connect = DBHelper_user_value()
	if value == None:
		db_connect.add_value(user_id, date, time, value)
	else:
		db_connect.change_value(user_id, date, time, value)

def delete_values(user_id):
	db_connect_result = DBHelper_user_result()
	db_connect_result.delete_value(user_id)
	db_connect_dialog = DBHelper_user_dialog()
	db_connect_dialog.delete_value(user_id)
	db_connect_value = DBHelper_user_value()
	db_connect_value.delete_value(user_id)
	db_connect_status = DBHelper_user_status()
	db_connect_status.delete_value(user_id)



def correct_score(word_label, word_score):
	"""Calculate the score for word or sentence prediction"""
	if word_label in POS_EMO and word_score >= 0.7:
		# the bot tends to predict joy
		correct_word_score = word_score * 10
	elif word_label in NEU_EMO:
		correct_word_score = 5
	elif word_label in NEG_EMO and word_score >= 0.5:
		correct_word_score = (1-word_score) * 10;
	else:
		correct_word_score = 5
	return correct_word_score


def analysis(user_id, date, turn):
	"""The first stage evaluation."""
	records = get_conversation(user_id, date, turn)
	score, word, emoji = records
	predict = classifier(word)
	word_label = predict[0]['label']
	word_score = predict[0]['score']
	score = float(score)
	correct_word_score = correct_score(word_label, word_score)

	if emoji in list(emoji_mapping.keys()):
		mapped_emotion = emoji_mapping[emoji]
	else:
		mapped_emotion = "moderate"

	emoji_score = emoji_score_mapping[mapped_emotion]

	average_score = sum([score, correct_word_score, emoji_score]) / 3
	if abs(correct_word_score-score) > 3 or abs(emoji_score-score) > 3:
		return False, average_score
	else:
		return True, average_score


async def welcome_ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Require users to provide age"""
	text = "Hi, nice to meet you. Before we start, could you please choose your age group with /age ? Thank you!"
	await update.effective_message.reply_text(text=text)     # change to effective_message


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Sends a predefined poll"""
	questions = ["9-12", "13-15", "16-18", "19-23", "24-29", "30-35", "36-40", "41-46", "47-55", "56-62"]
	message = await context.bot.send_poll(
		update.effective_chat.id,
		"Which age group do you belong to?",
		questions,
		is_anonymous=False,
		allows_multiple_answers=False,
	)
	# Save some info about the poll the bot_data for later use in receive_poll_answer
	payload = {
		message.poll.id: {
			"questions": questions,
			"message_id": message.message_id,
			"chat_id": update.effective_chat.id,
			"answers": 0,
		}
	}
	context.bot_data.update(payload)


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""On receiving polls, reply to it by a closed poll copying the received poll"""
	actual_poll = update.effective_message.poll
	# Only need to set the question and options, since all other parameters don't matter for
	# a closed poll
	await update.effective_message.reply_poll(
		question=actual_poll.question,
		options=[o.text for o in actual_poll.options],
		# with is_closed true, the poll/quiz is immediately closed
		is_closed=True,
		reply_markup=ReplyKeyboardRemove(),
	)


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Summarize a users poll vote"""
	answer = update.poll_answer
	answered_poll = context.bot_data[answer.poll_id]
	try:
		questions = answered_poll["questions"]
	# this means this poll answer update is from an old poll, we can't do our answering then
	except KeyError:
		return
	selected_options = answer.option_ids
	context.user_data['age_group'] = selected_options[0]
	user_name = update.effective_user.first_name
	chat_id = update.effective_user.id
	await context.bot.send_message(chat_id, text=f"Hi {user_name}, thank you for the information. "
									f" I would like to chat with you when you have time today. Could you please"
									f" provide the time slots that you are available? ")
	await context.bot.send_message(chat_id, text=f"Please list your available slots for later in the day in the form (start time)-(end time) with key word /set. Several slots can be split by comma.")
	await context.bot.send_message(chat_id, text=f"Example: /set 8-10, 11:35-12, 16-18:30")
	await context.bot.send_message(chat_id, text=f"You can stop the conversation at any time by using /cancel .")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send the alarm message and start a chat."""
	job = context.job
	chat_id = job.chat_id
	date, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]
	if status == 'wait_for_alarm':
		change_status(chat_id, date, 'wait_for_start_'+turn)
		await context.bot.send_message(chat_id, text=f"Hi! Are you ready for a chat?")
		button = InlineKeyboardButton("START", callback_data = "1")
		reply_markup = InlineKeyboardMarkup.from_button(button)
		await context.bot.send_message(chat_id, text="Please press START to start the conversation:", reply_markup=reply_markup)


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	""" Based on the time slots provided by the user, chatbot will set three alarms randomly. """
	raw_text = update.effective_message.text
	chat_id = update.effective_message.chat_id
	user_id = update.effective_user.id

	new_user = False
	status = get_status(chat_id)
	if status == []:
		new_user = True
	else:
		turn = status[0][-1]
		status = status[0][:-2]

	raw_text = raw_text.strip("/set").replace(" ", "")
	time_slots = raw_text.split(',')
	time_dict = {}
	factors = (60, 1)
	if new_user:
		appointment_day = datetime.datetime.now()
	else:
		appointment_day = datetime.datetime.now() + datetime.timedelta(days=1)

	for ts in time_slots:
		start, end = ts.split('-')
		if ":" in start:
			start = sum(i*j for i, j in zip(map(int, start.split(':')), factors))
		else:
			start = int(start) * 60
		if ":" in end:
			end = sum(i*j for i, j in zip(map(int, end.split(':')), factors))
		else:
			end = int(end) * 60

		time_dict[start] = 'start'
		time_dict[end] = 'end'

	available_time_slots = []
	time_points_key = list(time_dict.keys())

	while len(available_time_slots) < 3:
		time = random.randrange(0, 24*60)
		now_time = datetime.datetime.now()
		if time > min(time_points_key) and time < max(time_points_key):
			close_max = min([i for i in time_points_key if i > time])
			close_min = max([i for i in time_points_key if i < time])
			if time_dict[close_max] == 'end' and time_dict[close_min] == 'start':
				minute = time % 60
				hour = time // 60
				corrected_time = appointment_day.replace(hour=hour, minute=minute)
				if corrected_time not in available_time_slots:
					available_time_slots.append(corrected_time)

	available_time_slots = list(set(available_time_slots))

	for ats in available_time_slots:
		set_values(user_id, ats.strftime("%F"), ats.strftime("%H:%M"))

		set_t = ats - now_time
		context.job_queue.run_once(alarm, set_t, chat_id=chat_id, name=str(chat_id), data=set_t)

	if new_user:
		set_status(chat_id, appointment_day.strftime("%F") , "wait_for_alarm_1")
	else:
		change_status(chat_id, appointment_day.strftime("%F"), "wait_for_alarm_1")

	await update.effective_message.reply_text(f"Chitchat time is set. Thank you and see you later :)")


async def button_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Start the conversation by requiring user to evaluate their mood by given a score."""
	chat_id = update.effective_message.chat_id
	data, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]
	query = update.callback_query
	await query.answer()
	if query.data == '1' and status == 'wait_for_start':
		message = "Please choose a score from 0(bad) to 10(good) for your current mood."
		await query.edit_message_text(message)
		change_status(chat_id, data, "wait_for_chat_"+turn)
		return SCORE


async def reply_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Deal with user's score"""
	chat_id = update.effective_message.chat_id
	data, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]

	score_answer = update.effective_message.text
	score = float(re.findall(r'\b\d*\.*\d+\b', score_answer)[0])
	record_conversation(chat_id, data, turn, score)
	# [0-3: ,3-5, 5-7, 7-10]
	if score < 3:
		message = "Take it easy, everything will be fine. "
	elif score >= 3 and score <= 5:
		message = "Doesn't look like a good day. Cheer up! "
	elif score > 5 and score <= 7:
		message = "Another peace and calm day. "
	elif score > 7:
		message = "I'm glad you have a nice day. "
	message += "If you choose ONE word to describe your mood right now, which one do you prefer?"
	change_status(chat_id, data, "wait_for_word_" + turn)
	# use effective_message
	await update.effective_message.reply_text(text=message)

	return WORD


async def reply_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""deal with user's word"""
	chat_id = update.effective_message.chat_id
	data, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]

	word_answer = update.effective_message.text
	if ' ' not in word_answer:
		record_conversation(chat_id, data, turn, word_answer)
		message = "I see. Also one emoji?"
		change_status(chat_id, data, "wait_for_emoji_" + turn)
		await update.effective_message.reply_text(text=message)
		return EMOJI
	else:
		message = "Please use only ONE word."
		await update.effective_message.reply_text(text=message)
		return WORD


async def reply_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Deal with user's emoji. Then select one question for the user based on the self-evaluated score."""
	chat_id = update.effective_message.chat_id
	date, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]
	emoji_decode = emoji.demojize(update.effective_message.text)
	if emoji_decode in list(emoji_mapping.keys()):
		mapped_emotion = emoji_mapping[emoji_decode]
	else:
		mapped_emotion = "moderate"
	record_conversation(chat_id, date, turn, emoji_decode)
	record_result(chat_id, date, turn, mapped_emotion)

	consistent, final_score = analysis(chat_id, date, turn)
	context.chat_data["user_first_score"] = final_score
	context.chat_data["consistent"] = consistent

	user_age_group = context.user_data['age_group']
	if user_age_group in [0,1,2]:
		if final_score < 3:
			question = "Oh, I am sorry to hear that. Is something unhappy happend in the school?"
		elif final_score >= 3 and final_score < 5:
			question = "A not-so-delight-day. Well, any news from school?"
		elif final_score >= 5 and final_score < 7:
			question = "Well, is everything just normal at school?"
		else:
			question = "It looks like something good is happening! In the school or family?"
	elif user_age_group == 3:
		if final_score < 3:
			question = "Oh no, is something unhappy happend in the university of college? Deadline is coming?"
		elif final_score >= 3 and final_score < 5:
			question = "A not-so-delight-day. Well, any news from university?"
		elif final_score >= 5 and final_score < 7:
			question = "Surviving the courses and assignments! Any news from university?"
		else:
			question = "Looking good, are you going to a party? Or you just finish an assignment?"
	elif user_age_group in [4, 5, 6, 7, 8]:
		if final_score  < 3:
			question = "Not in a good mood, is it because of stress at work?"
		elif final_score >= 3 and final_score < 5:
			question = "A not-so-delight-day. Well, any news from work or family?"
		elif final_score >= 5 and final_score < 7:
			question = "Not bad! Any news from work?"
		else:
			question = "Cool, how is yous day at work? Quite nice?"
	elif user_age_group == 9:
		if final_score < 3:
			question = "Don't worry. Did something happen?"
		elif final_score >=3 and final_score < 5:
			question = "Not a lucky day. Well, any news from family?"
		elif final_score >= 5 and final_score < 7:
			question = "Not bad! Any news from family?"
		else:
			question = "Sounds nice! How is your day? I guess it would be quite great!"
	change_status(chat_id, date, "wait_for_question_" + turn)
	await update.message.reply_text(text=question)

	return QUESTION


async def reply_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Generate another question based on the score from the received reply."""
	chat_id = update.effective_message.chat_id
	data, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]
	final_score = context.chat_data["user_first_score"]
	answer = update.effective_message.text
	predict = classifier(answer)
	predict_label = predict[0]['label']
	predict_score = predict[0]['score']
	record_conversation(chat_id, data, turn, answer)
	record_result(chat_id, data, turn, predict_label + " " + str(predict_score))
	context.chat_data["answer_mood"] = predict_label
	context.chat_data["answer_score"] = predict_score

	if predict_label in NEG_EMO and predict_score > 0.5 and final_score < 0.5:
		message = "You don't seem to be in a good mood now, is something bothering you?"
	elif predict_label in NEG_EMO and predict_score > 0.5 and final_score >= 0.5:
		message = "Take it easy, what are your plans for later?"
	elif (predict_label in NEG_EMO and predict_score <= 0.5 and final_score < 0.5) or (predict_label in NEU_EMO and
																					   final_score < 0.5):
		message = "Do you want to do something to relax yourself later?"
	elif (predict_label in NEG_EMO and predict_score <= 0.5 and final_score >= 0.5) or (predict_label in NEU_EMO and
																						final_score >= 0.5):
		message = "Relax, do you want to tell me more about that?"
	elif predict_label in POS_EMO and predict_score > 0.7 and final_score >= 0.7:
		message = "You look in a good mood, do you have something happy to share?"
	elif predict_label in POS_EMO and predict_score <= 0.7 and final_score >= 0.7:
		message = "Do you want to share some stories happend today?"
	else:
		message = "Hey, cheer up! Do you have some plans for later?"
	change_status(chat_id, data, "wait_for_question2_" + turn)
	await update.message.reply_text(text=message)

	return QUESTION2


async def finish_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Finish daily chitchats."""
	chat_id = update.effective_message.chat_id
	date, status = get_status(chat_id)[0]
	turn = status[-1]
	status = status[:-2]
	answer = update.effective_message.text
	predict = classifier(answer)
	predict_label = predict[0]["label"]
	predict_score = predict[0]["score"]
	record_conversation(chat_id, date, turn, answer)
	record_result(chat_id, date, turn, predict_label + " " + str(predict_score))

	if predict_label in POS_EMO:
		message = "Wow, that's good. It's nice to talk with you. See you later :)"
	elif predict_label in NEU_EMO:
		message = "Ok, I understand. Hope you will feel better when we see each other next time."
	else:
		message = "Cheer up! Hope you will feel better later. I look forward to seeing you soon."

	final_score = context.chat_data["user_first_score"] + \
				  correct_score(context.chat_data["answer_mood"], float(context.chat_data["answer_score"])) + \
				  correct_score(predict_label, predict_score)

	date_time_value = get_values(chat_id, date)
	turn_sum = len(date_time_value)
	save_value = date_time_value[int(turn) - 1]
	set_values(save_value[0], save_value[1], save_value[2], final_score)
	await update.message.reply_text(text=message)
	if int(turn) < turn_sum:
		change_status(chat_id, date, "wait_for_alarm_"+str(int(turn)+1))
	else:
		message_end = "Today's emotion tracking report is generated. You can check the latest report with /report every time you want. " \
					  "Please also use /set to set the available time slots for tomorrow."
		date = datetime.datetime.now() + datetime.timedelta(days=1)
		change_status(chat_id, date.strftime("%F"), "wait_for_setalarm_1")
		# change_status(chat_id, date, "wait_for_setalarm_1")
		await update.message.reply_text(text=message_end)


async def create_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
	"""Generate the report. It can be called when all chitchats are finished or the user input /report."""
	chat_id = update.effective_message.chat_id
	date, status = get_status(chat_id)[0]
	turn = status[-1]

	# create table
	table = pt.PrettyTable(['turn', 'conversation'])
	table.align['turn'] = 'l'
	table.align['conversation'] = 'l'

	for i in range(1, int(turn)+1):
		dialog = get_conversation(chat_id, date, i)

		start = True
		for c in dialog:
			if start == True:
				table.add_row([i, c])
				start = False
			else:
				table.add_row([" ", c])

	table_score = pt.PrettyTable(['turn', 'overall_score'])
	table_score.align['turn'] = 'l'
	table_score.align['conversation'] = 'l'
	score = get_values(chat_id, date)

	for (n, c) in enumerate(score):
		table_score.add_row([n+1, c[1:]])

	await update.message.reply_text(f'Please check your latest report. The first part is the saved reply and the second part is the evaluated score for each chat.')
	await update.message.reply_text(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
	await update.message.reply_text(f'<pre>{table_score}</pre>', parse_mode=ParseMode.HTML)

	return


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Cancels and ends the conversation."""
	user = update.message.from_user
	chat_id = update.effective_message.chat_id
	logger.info("User %s canceled the conversation.", user.first_name)
	delete_values(chat_id)

	await update.message.reply_text(
		"Bye! Your data is removed from dataset. I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
	)

	return ConversationHandler.END



def main() -> None:
	"""Run bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(TOKEN).build()
	application.add_handler(CommandHandler("start", welcome_ask_age, block=False))
	application.add_handler(CommandHandler("age", poll, block=False))
	application.add_handler(MessageHandler(filters.POLL, receive_poll, block=False))
	application.add_handler(PollAnswerHandler(receive_poll_answer, block=False))
	application.add_handler(CommandHandler("set", set_time, block=False))
	application.add_handler(CommandHandler('cancel', cancel, block=False))
	application.add_handler(CommandHandler("report", create_daily_report, block=False))

	chitchat_conv = ConversationHandler(
		entry_points = [
			CallbackQueryHandler(
				button_action
			)
		],
		states = {
			SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_score, block=False)],
			WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_word, block=False)],
			EMOJI: [MessageHandler(filters.ALL, reply_emoji, block=False)],
			QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_question, block=False)],
			QUESTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_chat, block=False)],
		},
		fallbacks=[CommandHandler("cancel", cancel, block=False)],
		allow_reentry=True,
	)
	application.add_handler(chitchat_conv)

	# Run the bot until the user presses Ctrl-C
	application.run_polling()


if __name__ == "__main__":
	main()