from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PublishingStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class FilePublishingResult(BaseModel):
    filename: Optional[str] = Field(default=None, description="Generated filename")
    remote_path: Optional[str] = Field(
        default=None, description="Full remote path in front office"
    )
    publishing_status: PublishingStatus = Field(
        description="Publishing success or failure status"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if publishing failed"
    )

    class Config:
        from_attributes = True


class FrontOfficePublishingResult(BaseModel):
    timestamp: str = Field(description="Timestamp when publishing was performed")
    files: List[FilePublishingResult] = Field(
        description="Detailed results for each file"
    )

    class Config:
        from_attributes = True


class FrontOfficeFileInfo(BaseModel):
    filename: str = Field(description="Name of the file in front office")
    remote_path: str = Field(description="Full remote path in front office")
    size_bytes: Optional[int] = Field(default=None, description="File size in bytes")
    modified_time: Optional[str] = Field(
        default=None, description="Last modified timestamp"
    )

    class Config:
        from_attributes = True
