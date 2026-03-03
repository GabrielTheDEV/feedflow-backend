from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import Session, select, SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, session: Session, id) -> Optional[ModelType]:
        return session.get(self.model, id)

    def get_all(self, session: Session) -> List[ModelType]:
        return session.exec(select(self.model)).all()

    def create(self, session: Session, obj: ModelType) -> ModelType:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, obj: ModelType) -> None:
        session.delete(obj)
        session.commit()