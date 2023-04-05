from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from typing import List, Optional

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Post']
)

@router.get("/", 
         response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    
    # (get_post) podle ID prihlaseneho uzivatele
    # posts_to_get = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    # if not posts_to_get:
    #     raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    posts_to_get = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts_to_get

@router.post("/", 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_to_create = models.Post(
        owner_id = current_user.id, **post.dict()
    )

    db.add(post_to_create)
    db.commit()
    db.refresh(post_to_create)

    return post_to_create

@router.get("/{id}", 
         response_model = schemas.Post)
def get_post_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_to_get = db.query(models.Post).filter(models.Post.id == id).first()

    if post_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Post with id: {%d} not found." % (id)))
    
    # get_post_by_id podle prihlaseneho uzivatele
    # if post_to_get.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=("Not authorized to perform requested action!"))
    
    return post_to_get


@router.delete("/{id}")
def delete_post(id: int, db: Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=("Post with id: {%d} not found." % (id)))
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=("Not authorized to perform requested action!"))
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",  
         response_model=schemas.Post)
def update_post(id: int, post_to_create: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = ("Post with id: {%d} not found." % (id)))

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=("Not authorized to perform requested action!"))
    
    
    post_query.update(post_to_create.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()