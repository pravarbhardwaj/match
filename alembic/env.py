from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from models import Base  # Ensure Base is imported correctly from models
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Fetch DATABASE_URL from environment variables and set it to alembic config if available
db_url = os.getenv("MIGRATION_URL")
if db_url:
    print(f"MIGRATION_URL URL found: {db_url}")
    config.set_main_option("sqlalchemy.url", db_url)
else:
    print("No MIGRATION_URL found in environment variables.")
    raise ValueError("MIGRATION_URL not found in environment variables!")

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Specify the target_metadata for 'autogenerate' support
target_metadata = Base.metadata

# This function runs migrations in 'offline' mode (without connecting to the database)
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")  # Get URL from alembic config
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# This function runs migrations in 'online' mode (connecting to the database)
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Use engine_from_config to create an engine based on the configuration
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Run the appropriate migration function based on Alembic's mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
