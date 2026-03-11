import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import text

# Get database URL and SSL configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# SSL Configuration
DB_SSL_MODE = os.getenv(
    "DB_SSL_MODE", "disable"
)  # disable, require, verify-ca, verify-full
DB_SSL_CERT = os.getenv("DB_SSL_CERT")  # Path to client certificate
DB_SSL_KEY = os.getenv("DB_SSL_KEY")  # Path to client private key
DB_SSL_ROOT_CERT = os.getenv("DB_SSL_ROOT_CERT")  # Path to root CA certificate


def create_database_engine():
    engine_args = {"pool_pre_ping": True, "pool_recycle": 3600}

    if DATABASE_URL.startswith("postgresql://") and DB_SSL_MODE != "disable":
        connect_args = {"sslmode": DB_SSL_MODE}

        print(f"Configuring SSL with mode: {DB_SSL_MODE}")

        if DB_SSL_CERT:
            connect_args["sslcert"] = DB_SSL_CERT
        if DB_SSL_KEY:
            connect_args["sslkey"] = DB_SSL_KEY
        if DB_SSL_ROOT_CERT:
            connect_args["sslrootcert"] = DB_SSL_ROOT_CERT

        engine_args["connect_args"] = connect_args

        engine = create_engine(DATABASE_URL, **engine_args)
        # code to test if ssl works
        # try:
        #     with engine.connect() as conn:
        #         result = conn.execute(
        #             text(
        #                 "SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid()"
        #             )
        #         )
        #         ssl_info = result.fetchone()
        #         if ssl_info:
        #             ssl_enabled, ssl_version = ssl_info
        #             if ssl_enabled:
        #                 print(f"✅ SSL Connection VERIFIED! Version: {ssl_version}")
        #             else:
        #                 print(
        #                     "⚠️ WARNING: SSL configured but connection is NOT using SSL!"
        #                 )
        #         else:
        #             print("❓ Could not verify SSL status")
        # except Exception as e:
        #     print(f"❌ SSL verification failed: {e}")

        return engine
    else:
        print("SSL disabled or not PostgreSQL - using standard connection")
        return create_engine(DATABASE_URL, **engine_args)


# Create engine with SSL support
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Session:
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def get_script_db_session() -> Session:
    return SessionLocal()
