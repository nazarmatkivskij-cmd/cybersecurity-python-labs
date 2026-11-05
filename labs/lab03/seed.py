import json
import sqlite3
from pathlib import Path
from labs.lab03.database import get_connection , initialize_database

BASE_DIR = Path ( __file__ ).resolve ( ).parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database ( ) -> None :
	"""Прочитати seed.json та заповнити базу даних в одній транзакції."""
	initialize_database ( )
	
	if not SEED_PATH.exists ( ) :
		print ( f"Файл початкових даних не знайдено: {SEED_PATH}" )
		return
	
	data = json.loads ( SEED_PATH.read_text ( encoding = "utf-8" ) )
	
	connection = get_connection ( )
	try :
		with connection :
			# Перевіряємо, чи база вже заповнена
			cursor = connection.cursor ( )
			cursor.execute ( "SELECT COUNT(*) FROM categories" )
			categories_count = cursor.fetchone ( ) [ 0 ]
			
			if categories_count > 0 :
				print ( "База даних вже містить дані. Повторне заповнення пропущено без дублювання." )
				return
			
			# Вставляємо категорії
			for cat in data.get ( "categories" , [ ] ) :
				connection.execute (
						"INSERT INTO categories (id, name) VALUES (?, ?)" ,
						(cat [ "id" ] , cat [ "name" ])
						)
			
			# Вставляємо записи
			for rec in data.get ( "records" , [ ] ) :
				connection.execute (
						"""
						INSERT INTO records (code, title, category_id, value, status)
						VALUES (?, ?, ?, ?, ?)
						""" ,
						(
								rec [ "code" ] ,
								rec [ "title" ] ,
								rec [ "category_id" ] ,
								rec [ "value" ] ,
								rec [ "status" ]
								)
						)
		print ( "Початкові дані успішно додано до бази даних!" )
	except sqlite3.IntegrityError as e :
		print ( f"Порушення цілісності даних (транзакцію скасовано): {e}" )
		raise
	finally :
		connection.close ( )


if __name__ == "__main__" :
	seed_database ( )
	