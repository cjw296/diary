from argparse import Namespace, ArgumentParser
from datetime import datetime, timedelta, date
from pathlib import Path

from config import read_config
from dates import previous_sunday, parse_date
from export import dump
from objects import Period
from parse import parse
from zope import Client


def check_vm_time(client: Client):
    vm_now = datetime.strptime(client.get('/vm_now').text, '%Y-%m-%dT%H:%M:%S\n')
    local_now = datetime.now()
    delta = abs(local_now-vm_now)
    if delta > timedelta(seconds=5):
        raise RuntimeError(
            f'VM time is {vm_now} but local time is {local_now} ({delta}, please fix!'
        )


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--no-trim', dest='trim', action='store_false')
    parser.add_argument('--target', type=parse_date)
    return parser.parse_args()


def main():
    config = read_config()
    args = parse_args()
    client = config.zope

    check_vm_time(client)

    days: list[Period] = parse(config.diary_path.read_text())

    for d, d1 in zip(days, days[1:]):
        diff = (d1.date - d.date).days
        assert diff == 1, f"{d.human_date()} to {d1.human_date()} was {diff} days, not 1!"

    already_uploaded = {day.date: day.zope_id
                        for day in client.list(days[0].date - timedelta(days=3))}

    dump_path = Path(config.dump).expanduser()

    for day in days:
        dump(dump_path, day, dry_run=False)
        if not day.summary().strip():
            print(f'Skipping {day.human_date()} as empty')
            continue
        zope_id = already_uploaded.get(day.date)
        if zope_id:
            print(f'Updating {day.human_date()}')
            day.zope_id = zope_id
            client.update(day)
        else:
            print(f'Uploading {day.human_date()}')
            client.add(day)

    target_date = args.target or date.today() + timedelta(days=6)
    current = days[-1].date
    while target_date > current:
        current += timedelta(days=1)
        days.append(Period(current))

    if args.trim:
        cutoff = previous_sunday()
        days = [day for day in days if day.date > cutoff]
    config.diary_path.write_text('\n'.join(str(day) for day in days))


if __name__ == '__main__':
    main()
