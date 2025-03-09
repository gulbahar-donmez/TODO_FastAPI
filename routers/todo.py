from fastapi import APIRouter, Depends, Path, HTTPException, status
from modals import Todos  # modals yerine models kullanıyoruz
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/todo",
    tags=["Todo"]
)

class Todorequest(BaseModel):
    title: str = Field(min_length=3)
    des: str = Field(min_length=10)
    priority: int = Field(gt=0, lt=6)
    complete: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

# Tüm Todo'ları getir
@router.get("/read_all")
async def read_all(db: dbDep):
    return db.query(Todos).all()

# Belirli ID'ye sahip Todo'yu getir
@router.get("/read_one_id/{todo_id}")
async def read_one_id(db: dbDep, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

# Yeni Todo oluştur
@router.post("/create_todo")
async def create_todo(db: dbDep, todorequest: Todorequest):
    new_todo = Todos(**todorequest.model_dump())  # .dict() yerine .model_dump()
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {"message": "Todo created successfully", "todo": new_todo}

# Todo güncelle
@router.put("/update_todo/{todo_id}")
async def update_todo(db:dbDep,
                    todorequest=Todorequest,
                      todo_id:int=Path(gt=0)):
    todo =db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo.title = todorequest.title
    todo.des = todorequest.des
    todo.complete = todorequest.complete
    todo.priority = todorequest.priority

    db.commit()
    db.refresh(todo)
    return {"message": "Todo updated successfully", "todo": todo}

# Todo sil
@router.delete("/delete_todo/{todo_id}")
async def delete_todo(db: dbDep, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}







