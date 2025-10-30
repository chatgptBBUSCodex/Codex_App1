from __future__ import with_statement

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logger = logging.getLogger('alembic.env')
else:
    logger = logging.getLogger('alembic.env')

def get_engine():
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except TypeError:
        return current_app.extensions['migrate'].db.engine


def get_session():
    return current_app.extensions['migrate'].db.session


def run_migrations_offline() -> None:
    url = current_app.extensions['migrate'].db.get_engine().url
    context.configure(
        url=str(url).replace('%', '%%'),
        target_metadata=current_app.extensions['migrate'].db.metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=current_app.extensions['migrate'].db.metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


if current_app.config.get('SQLALCHEMY_DATABASE_URI') is None:
    logger.error('SQLALCHEMY_DATABASE_URI is not set. Cannot run migrations.')
else:
    run_migrations()
