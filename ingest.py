from datetime import datetime, timedelta, date
from pathlib import Path

from configurator import Config

from config import read_config
from objects import Day
from parse import parse
from zope import Client


def check_vm_time(client: Client):
    vm_now = datetime.strptime(client.get('/vm_now').text, '%Y-%m-%dT%H:%M:%S\n')
    local_now = datetime.now()
    if not (local_now > vm_now and local_now-vm_now < timedelta(seconds=5)):
        raise RuntimeError(f'VM time is {vm_now}, please fix!')


SUNDAY = 6
DAY = timedelta(days=1)


def previous_sunday() -> date:
    current = date.today()
    current -= DAY
    while current.weekday() != SUNDAY:
        current -= DAY
    return current


def main():
    config = read_config()
    client = config.zope

    check_vm_time(client)

    days: list[Day] = parse(config.diary_path.read_text())

    for d, d1 in zip(days, days[1:]):
        diff = (d1.date - d.date).days
        assert diff == 1, f"{d.human_date()} to {d1.human_date()} was {diff} days, not 1!"

    already_uploaded = {day.date: day.zope_id
                        for day in client.list(days[0].date - timedelta(days=3))}

    for day in days:
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

    target_date = date.today() + timedelta(days=6)
    current = days[-1].date
    while target_date > current:
        current += timedelta(days=1)
        days.append(Day(current))

    cutoff = previous_sunday()
    days = [day for day in days if day.date > cutoff]
    config.diary_path.write_text('\n'.join(str(day) for day in days))


if __name__ == '__main__':
    main()
