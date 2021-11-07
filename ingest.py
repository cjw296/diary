from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint

from configurator import Config
from requests import Session, Response
from testfixtures import compare

from objects import Day
from parse import parse


@dataclass
class Client:
    url: str
    username: str
    password: str

    def __post_init__(self):
        self.session: Session = Session()
        self.session.auth = (self.username, self.password)

    def get(self, uri: str) -> Response:
        result = self.session.get(self.url+uri)
        result.raise_for_status()
        return result


def check_vm_time(client: Client):
    vm_now = datetime.strptime(client.get('/vm_now').text, '%Y-%m-%dT%H:%M:%S\n')
    local_now = datetime.now()
    if not (local_now > vm_now and local_now-vm_now < timedelta(seconds=5)):
        raise RuntimeError(f'VM time is {vm_now}, please fix!')


def main():
    config = Config.from_path('config.yaml')
    diary_path = Path(config.diary_path).expanduser()

    client = Client(**config.zope.data)

    check_vm_time(client)


if __name__ == '__main__':
    main()
