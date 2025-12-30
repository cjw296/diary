from collections.abc import Iterator

import pytest
from testfixtures import Replacer


@pytest.fixture()
def replace() -> Iterator[Replacer]:
    with Replacer() as replace_:
        yield replace_
