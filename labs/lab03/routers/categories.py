from typing import List
from fastapi import APIRouter , HTTPException , status
from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate , CategoryRead

router = APIRouter ( prefix = "/categories" , tags = [ "Categories" ] )


@router.get ( "" , response_model = List [ CategoryRead ] )
def get_categories ( ) :
	return repository.get_all_categories ( )


@router.post ( "" , response_model = CategoryRead , status_code = status.HTTP_201_CREATED )
def create_category ( category: CategoryCreate ) :
	try :
		return repository.create_category ( category.name )
	except Exception :
		raise HTTPException (
				status_code = status.HTTP_409_CONFLICT ,
				detail = "Категорія з такою назвою вже існує або дані некоректні."
				)


@router.delete ( "/{category_id}" , status_code = status.HTTP_204_NO_CONTENT )
def delete_category ( category_id: int ) :
	if category_id <= 0 :
		raise HTTPException ( status_code = 422 , detail = "Некоректний id категорії." )
	
	deleted = repository.delete_category ( category_id )
	if not deleted :
		all_cats = repository.get_all_categories ( )
		exists = any ( c [ "id" ] == category_id for c in all_cats )
		if not exists :
			raise HTTPException ( status_code = 404 , detail = "Категорію не знайдено." )
		else :
			raise HTTPException ( status_code = 409 , detail = "Неможливо видалити непорожню категорію." )
	return None
