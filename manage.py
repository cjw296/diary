from contextlib import contextmanager
from dataclasses import dataclass

import click
from sqlalchemy import create_engine, Engine, delete

from config import read_config
from models.user import User, UserCreate
from sqlmodel import Session


@dataclass
class Database:
    engine: Engine
    session: Session


@contextmanager
def database(config_path: str):
    engine = create_engine(read_config(config_path).db)
    with Session(engine) as session:
        yield Database(engine, session)


@click.group()
@click.option("--config", "config_path", type=click.Path(exists=True), default="config.yaml")
@click.pass_context
def cli(ctx: click.Context, config_path: str) -> None:
    ctx.obj = ctx.with_resource(database(config_path))


@cli.group()
def user():
    """User management"""


@user.command('add')
@click.pass_context
@click.argument('email')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--superuser', 'superuser', is_flag=True, default=False)
def user_add(ctx: click.Context, email: str, password: str, superuser: bool) -> None:
    User.create(ctx.obj.session, UserCreate(email=email, is_superuser=superuser, password=password))
    ctx.obj.session.commit()


@user.command('delete')
@click.pass_context
@click.argument('email')
def user_delete(ctx: click.Context, email) -> None:
    ctx.obj.session.exec(delete(User).where(User.email == email))
    ctx.obj.session.commit()


if __name__ == '__main__':
    cli()
