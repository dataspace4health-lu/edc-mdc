from logging.config import fileConfig

from sqlalchemy import engine_from_config, text, pool, create_engine

from alembic import context

import os
from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    load_dotenv(dotenv_path=".env")


import os

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

DATABASE_URL = os.getenv("MIGRATION_DATABASE_URL", "sqlite:///./dev.db")
if DATABASE_URL == "sqlite:///./dev.db":
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

MIGRATION_DATABASE_URL = os.getenv("MIGRATION_DATABASE_URL")
if MIGRATION_DATABASE_URL:
    # Use migration-specific SSL configuration
    DB_SSL_MODE = os.getenv("MIGRATION_DB_SSL_MODE", "disable")
    DB_SSL_CERT = os.getenv("MIGRATION_DB_SSL_CERT")
    DB_SSL_KEY = os.getenv("MIGRATION_DB_SSL_KEY")
    DB_SSL_ROOT_CERT = os.getenv("MIGRATION_DB_SSL_ROOT_CERT")
    print("Using migration-specific SSL configuration")
else:
    # Fallback to app SSL configuration
    DB_SSL_MODE = os.getenv("DB_SSL_MODE", "disable")
    DB_SSL_CERT = os.getenv("DB_SSL_CERT")
    DB_SSL_KEY = os.getenv("DB_SSL_KEY")
    DB_SSL_ROOT_CERT = os.getenv("DB_SSL_ROOT_CERT")
    print("Using app SSL configuration for migrations")


def get_ssl_config():
    ssl_config = {}

    if DATABASE_URL.startswith("postgresql://") and DB_SSL_MODE != "disable":
        ssl_config = {"sslmode": DB_SSL_MODE}

        if DB_SSL_CERT:
            ssl_config["sslcert"] = DB_SSL_CERT
        if DB_SSL_KEY:
            ssl_config["sslkey"] = DB_SSL_KEY
        if DB_SSL_ROOT_CERT:
            ssl_config["sslrootcert"] = DB_SSL_ROOT_CERT

        print(f"🔐 Alembic using SSL mode: {DB_SSL_MODE}")
        return ssl_config
    else:
        print("🔓 Alembic SSL disabled or not PostgreSQL")
        return None


config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def load_initial_data(context):
    """Reads the initial_data.sql file and executes each statement.

    Set env LOAD_INITIAL_DATA to True to execute `./initial_data.sql`. Its default value is False.
    """

    if os.getenv("LOAD_INITIAL_DATA", "False") == "False":
        return

    test_data_script = open("./initial_data.sql").read()
    statements = [
        statement.strip()
        for statement in test_data_script.split(";")
        if statement.strip()
    ]
    for statement in statements:
        escaped_sql = text(statement)
        context.execute(escaped_sql)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
        load_initial_data(context)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    ssl_config = get_ssl_config()

    # Create engine with SSL support only if SSL is configured
    if ssl_config:
        # Create engine with SSL configuration
        print("🔐 Creating SSL-enabled engine for migrations")
        engine = create_engine(
            DATABASE_URL, poolclass=pool.NullPool, connect_args=ssl_config
        )
        connectable = engine
    else:
        # Use the standard alembic approach for non-SSL connections
        print("🔓 Creating standard engine for migrations")
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
            load_initial_data(context)
            connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
