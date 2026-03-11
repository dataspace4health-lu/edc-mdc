import os
from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    load_dotenv()

import uvicorn

# do not remove this import, it is needed for the tracing to work
import tracing

# Configure structured logging for Splunk
import logging_config

logging_config.configure_logging()
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    dataset,
    home,
    data_dictionary,
    dataset_relations,
    distribution,
    form_field,
    catalogue,
    auth,
    activity_logs,
    health_check,
    organisation,
    contact,
    form_fields,
    dataset_comment,
    data_service,
    user,
    user_assignment,
    role,
    authentic_source_label,
    authentic_source_assignment,
    test,
    front_office_publishing,
    qualified_attribution,
    legilux,
    eurlex,
    antivirus,
    released_datasets,
)
from services.config import ConfigService
from starlette.middleware.sessions import SessionMiddleware
from version import __version__
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from utils.encrypted_session_middleware import EncryptedSessionMiddleware

app = FastAPI(
    title="DCA - Metadata Capture",
    summary="API for metadata capture system.",
    version=__version__,
    terms_of_service="https://lnds.lu",
    contact={
        "name": "LNDS",
        "url": "https://lnds.lu",
        "email": "info@lnds.lu",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
    openapi_tags=[
        {
            "name": "dataset",
            "description": "All endpoints for dataset manipulation",
        },
        {
            "name": "data-dictionaries",
            "description": "All endpoints for data dictionaries manipulation",
        },
        {
            "name": "distributions",
            "description": "All endpoints for distributions manipulation",
        },
        {
            "name": "front-end",
            "description": "All front-end related endpoints",
        },
        {
            "name": "organisations",
            "description": "All endpoints for organisation manipulation",
        },
        {
            "name": "contacts",
            "description": "all endpoints for contact manipulation",
        },
        {
            "name": "comments",
            "description": "All endpoints for dataset comments manipulation",
        },
        {
            "name": "antivirus",
            "description": "Antivirus scanning endpoints",
        },
        {
            "name": "eurlex",
            "description": "EUR-Lex legislation search endpoints",
        },
        {
            "name": "released-datasets",
            "description": "Endpoints for polling released datasets across instances",
        },
    ],
    docs_url="/api-docs",
)

APP_URL = os.getenv("APP_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    EncryptedSessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    encryption_key=os.getenv("SESSION_ENCRYPTION_KEY"),
    max_age=1 * 24 * 60 * 60,  # 1 day in seconds
)

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app.mount(
    "/docs", StaticFiles(directory="client/public/docs", html=True), name="custom-docs"
)


@app.get("/docs", include_in_schema=False)
async def serve_docs_root():
    return RedirectResponse("/docs/")


if ENVIRONMENT != "development" and ENVIRONMENT != "test":
    app.mount("/assets", StaticFiles(directory="client/dist/assets"), name="assets")
    app.include_router(home.router)

app.include_router(auth.router)
app.include_router(catalogue.router)
app.include_router(data_dictionary.router)
app.include_router(dataset_relations.router)
app.include_router(distribution.router)
app.include_router(dataset.router)
app.include_router(form_field.router)
app.include_router(activity_logs.router)
app.include_router(health_check.router)
app.include_router(organisation.router)
app.include_router(contact.router)
app.include_router(form_fields.router)
app.include_router(dataset_comment.router)
app.include_router(data_service.router)
app.include_router(user.router)
app.include_router(user_assignment.router)
app.include_router(role.router)
app.include_router(authentic_source_label.router)
app.include_router(authentic_source_assignment.router)
app.include_router(front_office_publishing.router)
app.include_router(qualified_attribution.router)
app.include_router(legilux.router)
app.include_router(eurlex.router)
app.include_router(antivirus.router)
app.include_router(released_datasets.router)

if ENVIRONMENT == "end2end":
    app.include_router(test.router)


@app.get("/favicon.svg", response_class=Response, tags=["front-end"])
async def public_svg_files(request: Request):
    return Response(
        content=open("client/dist/favicon.svg").read(),
        media_type="image/svg+xml",
        status_code=200,
    )


@app.get("/data-dictionary-template.csv", response_class=Response, tags=["front-end"])
async def public_csv_files(request: Request):
    return Response(
        content=open("client/dist/data-dictionary-template.csv").read(),
        media_type="text/csv",
        status_code=200,
    )


@app.get("/fonts/{font_name}", tags=["front-end"])
async def public_fonts(font_name: str):
    font_path = f"client/dist/fonts/{font_name}"

    if not os.path.exists(font_path):
        raise HTTPException(status_code=404, detail="Font not found")

    if font_name.endswith(".woff"):
        media_type = "font/woff"
    elif font_name.endswith(".woff2"):
        media_type = "font/woff2"
    else:
        raise HTTPException(status_code=400, detail="Unsupported font format")

    return FileResponse(path=font_path, media_type=media_type)


@app.get("/api/docs/config", tags=["front-end"])
async def docs_config(request: Request):
    """Serve configuration for documentation feature flags"""
    service = request.app.state.config_service
    return {"feature_flags": service.get_feature_flags()}


templates = Jinja2Templates(directory="client/dist")


@app.get("/{full_path:path}", response_class=HTMLResponse, tags=["front-end"])
async def not_found(request: Request, full_path: str):
    service = request.app.state.config_service
    app_title = service.get_app_title()
    return templates.TemplateResponse(
        "index.html", {"request": request, "app_title": app_title}
    )


OTL_URL = os.getenv("OTL_URL")
if OTL_URL:
    # Exclude health checks and other noisy endpoints from tracing
    # excluded_urls accepts comma-delimited regex patterns
    FastAPIInstrumentor().instrument_app(
        app, excluded_urls="/api/health,/favicon\\.svg,/api-docs.*"
    )


@app.on_event("startup")
async def startup_event():
    CONFIG_PATH = os.getenv("CONFIG_PATH", "./config.json")
    app.state.config_service = ConfigService(CONFIG_PATH)


if __name__ == "__main__":
    # Use log_config=None to prevent uvicorn from overriding our logging configuration
    # Only when we've configured custom logging (not in 'default' mode)
    log_format = os.getenv("LOG_FORMAT", "default")
    if log_format == "default" and not os.getenv("LOG_FILE_PATH"):
        # Let uvicorn use its default colored logging
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Use our custom logging configuration
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
