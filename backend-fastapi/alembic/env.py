import sys
import os
from pathlib import Path
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(str(Path(__file__).parent.parent))

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from src.database import Base
from src.user import models
from src.store import models
from src.sales_panel import models

config = context.config

database_host = os.getenv("DB__HOST")
database_port = os.getenv("DB__PORT")
database_name = os.getenv("DB__NAME")
database_password = os.getenv("DB__PASSWORD")

database_url = f"postgresql://postgres:{database_password}@{database_host}:{database_port}/{database_name}"
config.set_main_option("sqlalchemy.url", database_url)

print(f"Alembic using PostgreSQL: {database_url}")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
