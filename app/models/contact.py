from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from dependencies.database import Base
from typing import Optional


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    organisation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organisations.id"), nullable=False
    )
    is_deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    organisation = relationship("Organisation", back_populates="contacts")
    dataset_contacts = relationship("DatasetContact", back_populates="contact")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_deprecated": self.is_deprecated,
        }
