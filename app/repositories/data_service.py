from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db_session
from models.data_service import DataService, DataServiceEndpoint
from typing import List, Annotated
from sqlalchemy import desc, or_


class DataServiceRepository:
    def __init__(self, db_session: Annotated[Session, Depends(get_db_session)]):
        self._db_session = db_session

    def get_data_services(self) -> List[DataService]:
        return self._db_session.query(DataService).order_by(desc(DataService.id)).all()

    def get_data_service(self, data_service_id: int) -> DataService:
        data_service = (
            self._db_session.query(DataService)
            .filter(DataService.id == data_service_id)
            .first()
        )
        if not data_service:
            raise HTTPException(
                status_code=404, detail=f"Data Service[{data_service_id}] not found"
            )
        return data_service

    def add(self, data_service: DataService) -> None:
        self._db_session.add(data_service)

    def update(self, data_service: DataService) -> None:
        self._db_session.merge(data_service)

    def add_endpoints(self, endpoints: List[DataServiceEndpoint]) -> None:
        self._db_session.add_all(endpoints)

    def get_by_title(self, title: str) -> DataService:
        return (
            self._db_session.query(DataService)
            .filter(or_(DataService.title == title))
            .first()
        )

    def commit(self) -> None:
        self._db_session.commit()

    def refresh(self, data_service: DataService) -> None:
        self._db_session.refresh(data_service)
