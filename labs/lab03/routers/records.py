from typing import List , Optional
from fastapi import APIRouter , HTTPException , Query , status
from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate , RecordRead , RecordReplace

router = APIRouter ( prefix = "/records" , tags = [ "Records" ] )


@router.get ( "" , response_model = List [ RecordRead ] )
def get_records (
		category_id: Optional [ int ] = Query ( None , gt = 0 ) ,
		status: Optional [ str ] = None ,
		min_value: Optional [ float ] = None ,
		q: Optional [ str ] = Query ( None , min_length = 1 , max_length = 120 ) ,
		limit: int = Query ( 20 , ge = 1 , le = 100 ) ,
		offset: int = Query ( 0 , ge = 0 )
		) :
	return repository.get_records (
			category_id = category_id ,
			status = status ,
			min_value = min_value ,
			q = q ,
			limit = limit ,
			offset = offset
			)


@router.get ( "/{record_id}" , response_model = RecordRead )
def get_record ( record_id: int ) :
	if record_id <= 0 :
		raise HTTPException ( status_code = 422 , detail = "Некоректний id запису." )
	record = repository.get_record_by_id ( record_id )
	if not record :
		raise HTTPException ( status_code = 404 , detail = "Запис не знайдено." )
	return record


@router.post ( "" , response_model = RecordRead , status_code = status.HTTP_201_CREATED )
def create_record ( record: RecordCreate ) :
	categories = repository.get_all_categories ( )
	if not any ( c [ "id" ] == record.category_id for c in categories ) :
		raise HTTPException ( status_code = 404 , detail = "Вказана категорія не існує." )
	
	try :
		return repository.create_record (
				code = record.code ,
				title = record.title ,
				category_id = record.category_id ,
				value = record.value ,
				status = record.status
				)
	except Exception :
		raise HTTPException ( status_code = 409 , detail = "Запис із таким кодом вже існує." )


@router.put ( "/{record_id}" , response_model = RecordRead )
def update_record ( record_id: int , record: RecordReplace ) :
	if record_id <= 0 :
		raise HTTPException ( status_code = 422 , detail = "Некоректний id запису." )
	
	categories = repository.get_all_categories ( )
	if not any ( c [ "id" ] == record.category_id for c in categories ) :
		raise HTTPException ( status_code = 404 , detail = "Вказана категорія не існує." )
	
	updated = repository.update_record (
			record_id = record_id ,
			code = record.code ,
			title = record.title ,
			category_id = record.category_id ,
			value = record.value ,
			status = record.status
			)
	if not updated :
		raise HTTPException ( status_code = 404 , detail = "Запис не знайдено або конфлікт." )
	return updated


@router.delete ( "/{record_id}" , status_code = status.HTTP_204_NO_CONTENT )
def delete_record ( record_id: int ) :
	if record_id <= 0 :
		raise HTTPException ( status_code = 422 , detail = "Некоректний id запису." )
	success = repository.delete_record ( record_id )
	if not success :
		raise HTTPException ( status_code = 404 , detail = "Запис не знайдено." )
	return None


@router.post ( "/bulk" , response_model = List [ RecordRead ] , status_code = status.HTTP_201_CREATED )
def bulk_create_records ( records: List [ RecordCreate ] ) :
	if not (1 <= len ( records ) <= 100) :
		raise HTTPException ( status_code = 422 , detail = "Кількість має бути від 1 до 100." )
	
	categories = repository.get_all_categories ( )
	cat_ids = { c [ "id" ] for c in categories }
	
	codes_seen = set ( )
	for r in records :
		if r.category_id not in cat_ids :
			raise HTTPException ( status_code = 404 , detail = f"Категорія з id {r.category_id} не існує." )
		if r.code in codes_seen :
			raise HTTPException ( status_code = 409 , detail = f"Дублікат коду {r.code}." )
		codes_seen.add ( r.code )
	
	records_data = [
			{
					"code" : r.code ,
					"title" : r.title ,
					"category_id" : r.category_id ,
					"value" : r.value ,
					"status" : r.status
					}
			for r in records
			]
	
	try :
		return repository.bulk_create_records ( records_data )
	except Exception :
		raise HTTPException ( status_code = 409 , detail = "Конфлікт даних у базі." )
	