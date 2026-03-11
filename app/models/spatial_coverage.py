from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from dependencies.database import Base


class SpatialCoverage(Base):
    __tablename__ = "spatial_coverage"
    key: Mapped[str] = mapped_column(
        String, nullable=False, primary_key=True, index=True
    )
    eng_label: Mapped[str] = mapped_column(String)

    def to_dict_for_diff(self):
        data = {
            "key": self.key,
            "eng_label": self.eng_label,
        }
        return data
