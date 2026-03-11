from sqlalchemy import String
from dependencies.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Language(Base):
    __tablename__ = "language"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)
