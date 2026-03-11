import os
import boto3
import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from typing import Annotated
from services.catalogue import CatalogueService
from schemas.catalogue import CatalogueFormat
from models.identity_context import IdentityContext
from routes.auth import validate_and_retrieve_identity_context
from utils.error_responses import ErrorResponse

router = APIRouter()

S3_BUCKET = os.getenv("S3_BUCKET")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


@router.get(
    "/api/v1/catalogue.{format}",
    tags=["catalogue"],
)
def retrieve_catalogue(
    service: Annotated[CatalogueService, Depends(CatalogueService)],
    format: CatalogueFormat,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["catalogue:generate-rdf"])
    ),
) -> Response:
    try:
        media_type, content = service.get_catalogue(format)
        return Response(
            content=content,
            media_type=media_type,
            status_code=200,
        )
    except Exception:
        return ErrorResponse.create(
            status_code=500,
            detail="Failed to retrieve catalogue due to an internal error.",
            title="Catalogue Retrieval Error",
        )


def upload_to_s3(content: str, format: str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{current_date}.lnds.{format.lower()}"
    s3_client = get_s3_client()
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=content.encode("utf-8"),
        ContentType=f"text/{format.lower()}",
    )
    return filename


@router.get(
    "/api/v1/catalogue/{format}/upload",
    tags=["catalogue"],
    status_code=status.HTTP_201_CREATED,
)
def retrieve_catalogue_and_upload_s3(
    service: Annotated[CatalogueService, Depends(CatalogueService)],
    format: CatalogueFormat,
    identity: IdentityContext = Depends(
        validate_and_retrieve_identity_context(["catalogue:upload-rdf:s3"])
    ),
) -> JSONResponse:
    try:
        _, content = service.get_catalogue(format)
        filename = upload_to_s3(content, format.value.lower())
        location = f"s3://{S3_BUCKET}/{filename}"
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Catalogue successfully uploaded to S3",
                "location": location,
            },
            headers={"Location": location},
        )
    except Exception:
        return ErrorResponse.create(
            status_code=500,
            detail="Failed to retrieve catalogue or upload to S3 due to an internal error.",
            title="Catalogue Upload Error",
        )
