from datetime import date
from pathlib import Path

import click

from diary.config import read_config
from diary.dates import parse_date
from diary.export import export
from diary.ingest import ingest


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    ctx.ensure_object(dict)
    ctx.call_on_close(lambda: print())


@main.command(name='export')
@click.option('--start-url', default='')
@click.option('--start-date', default=date.max, type=parse_date)
@click.option('--dump', type=click.Path(path_type=Path))
@click.option('--dry-run', is_flag=True)
@click.option('--quiet', is_flag=True)
@click.pass_context
def click_export(
    ctx: click.Context,
    start_url: str,
    start_date: date,
    dump: Path | None,
    dry_run: bool,
    quiet: bool,
) -> None:
    config = read_config()
    export(config, start_url, start_date, dump, dry_run, quiet)


@main.command(name='ingest')
@click.option('--no-trim', 'trim', is_flag=True, default=True, flag_value=False)
@click.option('--target', type=parse_date)
@click.pass_context
def click_ingest(ctx: click.Context, trim: bool, target: date | None) -> None:
    config = read_config()
    ingest(config, trim, target)
