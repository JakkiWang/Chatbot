import sqlite3

class DBHelper_user_value:
	def __init__(self, dbname="resources/user.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def add_value(self, name, date, time, value=None):
		stmt = "INSERT INTO user_value (name, date, time, value) VALUES (?, ?, ?, ?)"
		args = (name, date, time, value)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def change_value(self, name, date, time, value):
		stmt = "UPDATE user_value SET value = (?) WHERE name = (?) and date = (?) and time = (?)"
		args = (value, name, date, time)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def delete_value(self, item_text):
		stmt = "DELETE FROM user_value WHERE name = (?)"
		args = (item_text, )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def get_values_for_day(self, name, date):
		stmt = "SELECT * FROM user_value where name = (?) and date = (?)"
		args = (name, date)
		rows = self.conn.execute(stmt, args)
		results = rows.fetchall()

		return results


class DBHelper_user_status:
	"""
	table:
	chat_id | status
	example:
	test | wait_for_start_1
	status is composed of two parts: first part ([:-2]) represents the status, and last number represents the number of conversation
	"""
	def __init__(self, dbname="resources/user.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def add_value(self, chat_id, date, status):
		stmt = "INSERT INTO user_status (chat_id, date, status) VALUES (?, ?, ?)"
		args = (chat_id, date, status)
		self.conn.execute(stmt, args)
		self.conn.commit()
		# self.conn.close()

	def get_value(self, chat_id):
		stmt = "SELECT date, status FROM user_status where chat_id = (?)"
		args = (chat_id, )
		rows = self.conn.execute(stmt, args)
		# results = [r for r in rows]
		results = rows.fetchall()
		return results

	def delete_value(self, item_text):
		stmt = "DELETE FROM user_status WHERE chat_id = (?)"
		args = (item_text, )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def change_value(self, chat_id, date, status):
		stmt = "UPDATE user_status SET status = (?) WHERE chat_id = (?) and date = (?)"
		args = (status, chat_id, date)
		self.conn.execute(stmt, args)
		self.conn.commit()


class DBHelper_user_dialog:
	def __init__(self, dbname="resources/user.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def add_value(self, chat_id, date, turn, content):
		stmt = "INSERT INTO user_dialog (chat_id, date, turn, content) VALUES (?, ?, ?, ?)"
		args = (chat_id, date, int(turn), content)
		self.conn.execute(stmt, args)
		self.conn.commit()
		# self.conn.close()

	def get_value(self, chat_id, date, turn):
		stmt = "SELECT content FROM user_dialog where chat_id = (?) and date = (?) and turn = (?)"
		args = (chat_id, date, int(turn))
		rows = self.conn.execute(stmt, args)
		results = [r[0] for r in rows]

		return results

	def delete_value(self, item_text):
		stmt = "DELETE FROM user_dialog WHERE chat_id = (?)"
		args = (item_text,)
		self.conn.execute(stmt, args)
		self.conn.commit()


class DBHelper_user_result:
	def __init__(self, dbname="resources/user.db"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def add_value(self, chat_id, date, turn, content):
		stmt = "INSERT INTO user_result (chat_id, date, turn, content) VALUES (?, ?, ?, ?)"
		args = (chat_id, date, int(turn), content)
		self.conn.execute(stmt, args)
		self.conn.commit()
		# self.conn.close()

	def get_value(self, chat_id, date, turn):
		stmt = "SELECT content FROM user_result where chat_id = (?) and date = (?) and turn = (?)"
		args = (chat_id, date, int(turn))
		rows = self.conn.execute(stmt, args)
		results = [r[0] for r in rows]
		return results

	def delete_value(self, item_text):
		stmt = "DELETE FROM user_result WHERE chat_id = (?)"
		args = (item_text,)
		self.conn.execute(stmt, args)
		self.conn.commit()


if __name__ == '__main__':
	# test
	conn = DBHelper_user_status()
	print(conn.get_value("6105967326"))
	conn.change_value("6105967326", "wait_for_alarm")