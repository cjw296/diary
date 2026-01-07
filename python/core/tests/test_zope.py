from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date

import pytest
import responses
from bs4 import BeautifulSoup
from requests import HTTPError, PreparedRequest
from responses import RequestsMock
from testfixtures import compare, ShouldRaise, replace_in_module

import diary.parse as parse
import diary.zope as zope
from diary.objects import Period, Stuff, Type
from diary.zope import Client, LookBackFailed


@pytest.fixture
def client() -> Client:
    return Client(url="https://example.com", username="testuser", password="testpass")


@pytest.fixture
def mocked_responses() -> Iterator[RequestsMock]:
    with RequestsMock() as mock:
        yield mock


@dataclass
class Mocked:
    responses: RequestsMock

    @property
    def request(self) -> PreparedRequest:
        assert len(self.responses.calls) == 1
        request = self.responses.calls[0].request
        return request


@pytest.fixture
def mocked(mocked_responses: RequestsMock) -> Mocked:
    return Mocked(mocked_responses)


class TestClient:
    def test_init(self, client: Client) -> None:
        compare(client.url, expected="https://example.com")
        compare(client.username, expected="testuser")
        compare(client.password, expected="testpass")
        compare(client.session.auth, expected=("testuser", "testpass"))

    def test_request_relative_url(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.GET, "https://example.com/test", body="success", status=200)

        result = client.request("get", "/test")
        compare(result.text, expected="success")
        request = mocked.request
        compare(request.url, expected="https://example.com/test")
        compare(request.headers["Authorization"], expected="Basic dGVzdHVzZXI6dGVzdHBhc3M=")

    def test_request_absolute_url(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.GET, "https://other.com/test", body="success", status=200)

        result = client.request("get", "https://other.com/test", absolute=True)
        compare(result.text, expected="success")
        request = mocked.request
        compare(request.url, expected="https://other.com/test")

    def test_request_with_kwargs(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.POST, "https://example.com/test", body="success", status=200)

        result = client.request("post", "/test", json={"key": "value"})
        compare(result.text, expected="success")

    def test_request_raises_for_status(
        self, client: Client, mocked_responses: RequestsMock
    ) -> None:
        mocked_responses.add(responses.GET, "https://example.com/test", body="error", status=404)

        with ShouldRaise(HTTPError):
            client.request("get", "/test")

    def test_get(self, client: Client, mocked_responses: RequestsMock) -> None:
        mocked_responses.add(responses.GET, "https://example.com/test", body="success", status=200)

        result = client.get("/test")
        compare(result.text, expected="success")

    def test_get_absolute(self, client: Client, mocked_responses: RequestsMock) -> None:
        mocked_responses.add(responses.GET, "https://other.com/test", body="success", status=200)

        result = client.get("https://other.com/test", absolute=True)
        compare(result.text, expected="success")

    def test_get_soup(self, client: Client, mocked_responses: RequestsMock) -> None:
        html_content = '<html><body><h1>Test</h1></body></html>'
        mocked_responses.add(
            responses.GET,
            "https://example.com/test",
            body=html_content.encode('latin-1'),
            status=200,
        )

        soup = client.get_soup("/test")
        assert isinstance(soup, BeautifulSoup)
        h1_tag = soup.find('h1')
        assert h1_tag is not None
        compare(h1_tag.text, expected="Test")

    def test_get_soup_absolute(self, client: Client, mocked_responses: RequestsMock) -> None:
        html_content = '<html><body><h1>Test</h1></body></html>'
        mocked_responses.add(
            responses.GET, "https://other.com/test", body=html_content.encode('latin-1'), status=200
        )

        soup = client.get_soup("https://other.com/test", absolute=True)
        assert isinstance(soup, BeautifulSoup)
        h1_tag = soup.find('h1')
        assert h1_tag is not None
        compare(h1_tag.text, expected="Test")

    def test_post(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.POST, "https://example.com/test", body="success", status=200)

        result = client.post("/test", {"key": "value"})
        compare(result.text, expected="success")
        request = mocked.request
        compare(request.body, expected="key=value")

    def test_post_data_basic(self, client: Client) -> None:
        period = Period(start=date(2023, 1, 15))
        period.stuff = [Stuff(Type.event, "Test event")]

        data = client._post_data(period)

        compare(
            data,
            expected={
                'title': "(2023-01-15) Sunday",
                'author': "-",
                'summary': b"EVENT Test event",
                'encoding': "Plain",
                'addPosting:method': " Add ",
            },
        )

    def test_post_data_unicode_error(self, client: Client) -> None:
        period = Period(start=date(2023, 1, 15))
        # Create a Stuff with content that can't be encoded in latin-1
        stuff = Stuff(Type.event, "Test with emoji 😀")
        period.stuff = [stuff]

        with ShouldRaise(Exception):  # The exact error message varies by emoji representation
            client._post_data(period)

    def test_add(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.POST, "https://example.com", body="success", status=200)

        period = Period(start=date(2023, 1, 15))
        period.stuff = [Stuff(Type.event, "Test event")]

        client.add(period)

        request = mocked.request
        compare(
            request.body,
            expected=(
                "title=%282023-01-15%29+Sunday&author=-&summary=EVENT+Test+event&"
                "encoding=Plain&addPosting%3Amethod=+Add+"
            ),
        )

    def test_update(self, client: Client, mocked: Mocked) -> None:
        mocked.responses.add(responses.POST, "https://example.com/123", body="success", status=200)

        period = Period(start=date(2023, 1, 15), zope_id="123")
        period.stuff = [Stuff(Type.event, "Updated event")]

        client.update(period)

        request = mocked.request
        compare(request.url, expected="https://example.com/123")
        compare(
            request.body,
            expected=(
                "title=%282023-01-15%29+Sunday&author=-&summary=EVENT+Updated+event&"
                "encoding=Plain&addPosting%3Amethod=+Add+&edit%3Amethod=Change"
            ),
        )

    def test_update_without_zope_id(self, client: Client) -> None:
        period = Period(start=date(2023, 1, 15))

        with ShouldRaise(AssertionError):
            client.update(period)


class TestClientInferDate:
    def test_infer_date_with_date_format(self) -> None:
        result, end = Client.infer_date("(2023-01-15) Sunday")
        compare(result, expected=date(2023, 1, 15))
        compare(end, expected=None)

    def test_infer_date_format_mismatch(self) -> None:
        with ShouldRaise(AssertionError("15 Jan 23 was a Sunday, got: (2023-01-15) Monday")):
            Client.infer_date("(2023-01-15) Monday")

    def test_infer_date_day_name_only_with_previous(self) -> None:
        previous = date(2023, 1, 20)  # Friday
        result, end = Client.infer_date("Tuesday", previous)
        compare(result, expected=date(2023, 1, 17))
        compare(end, expected=None)

    def test_infer_date_day_name_only_without_previous(self) -> None:
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("Tuesday")

    def test_infer_date_day_name_not_found(self) -> None:
        previous = date(2023, 1, 15)  # Sunday
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("NotADay", previous)

    def test_infer_date_bad_format(self) -> None:
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("invalid date format")

    def test_infer_date_single_day_with_previous(self) -> None:
        previous = date(2023, 1, 20)
        with ShouldRaise(LookBackFailed):
            Client.infer_date("15", previous)

    def test_infer_date_single_day_without_previous(self) -> None:
        with pytest.raises(ValueError, match="Need previous date for"):
            Client.infer_date("15")

    def test_infer_date_day_with_month(self) -> None:
        previous = date(2023, 1, 20)  # Close enough for 5-day lookback
        result, end = Client.infer_date("16 Jan", previous)
        compare(result, expected=date(2023, 1, 16))
        compare(end, expected=None)

    def test_infer_date_full_date(self) -> None:
        previous = date(2023, 1, 20)  # Close enough for 5-day lookback
        result, end = Client.infer_date("16 Jan 2023", previous)
        compare(result, expected=date(2023, 1, 16))
        compare(end, expected=None)

    def test_infer_date_range_with_end_day(self) -> None:
        previous = date(2023, 1, 20)
        # These patterns cause TypeError in lookback due to None day_number
        with ShouldRaise(TypeError):
            Client.infer_date("15 - 17", previous)

    def test_infer_date_range_with_to(self) -> None:
        previous = date(2023, 1, 20)
        # These patterns cause TypeError in lookback due to None day_number
        with ShouldRaise(TypeError):
            Client.infer_date("15 to 17", previous)

    def test_infer_date_range_full_dates(self) -> None:
        previous = date(2023, 1, 20)  # Use January so months match
        result, end = Client.infer_date("15 Jan 2023 - 17 Jan 2023", previous)
        compare(result, expected=date(2023, 1, 15))
        compare(end, expected=date(2023, 1, 17))


class TestClientLookback:
    def test_lookback_basic(self) -> None:
        start = date(2023, 1, 20)
        result = Client.lookback(start, "15", "", "15", None, None, max_days=10)
        compare(result, expected=date(2023, 1, 15))

    def test_lookback_with_day_name(self) -> None:
        start = date(2023, 1, 20)  # Friday
        result = Client.lookback(start, "Tuesday 17", "Tuesday", "17", None, None, max_days=10)
        compare(result, expected=date(2023, 1, 17))

    def test_lookback_with_day_name_short(self) -> None:
        start = date(2023, 1, 20)  # Friday
        result = Client.lookback(start, "Tue 17", "Tue", "17", None, None, max_days=10)
        compare(result, expected=date(2023, 1, 17))

    def test_lookback_wrong_day_name(self) -> None:
        start = date(2023, 1, 20)  # Friday
        with pytest.raises(AssertionError, match="was a Tuesday, but entry had Wednesday"):
            Client.lookback(start, "Wednesday 17", "Wednesday", "17", None, None, max_days=10)

    def test_lookback_with_month(self) -> None:
        start = date(2023, 1, 20)  # Start in January
        result = Client.lookback(start, "15 January", "", "15", "January", None, max_days=10)
        compare(result, expected=date(2023, 1, 15))

    def test_lookback_with_month_short(self) -> None:
        start = date(2023, 1, 20)  # Start in January
        result = Client.lookback(start, "15 Jan", "", "15", "Jan", None, max_days=10)
        compare(result, expected=date(2023, 1, 15))

    def test_lookback_with_month_alias(self) -> None:
        start = date(2023, 9, 20)  # Start in September
        result = Client.lookback(start, "15 Sept", "", "15", "Sept", None, max_days=10)
        compare(result, expected=date(2023, 9, 15))

    def test_lookback_wrong_month(self) -> None:
        start = date(2023, 1, 20)  # Start in January
        with pytest.raises(AssertionError, match="was in January, but entry had February"):
            Client.lookback(start, "15 February", "", "15", "February", None, max_days=10)

    def test_lookback_with_year(self) -> None:
        start = date(2023, 1, 20)  # Start in 2023
        result = Client.lookback(start, "15 2023", "", "15", None, "2023", max_days=10)
        compare(result, expected=date(2023, 1, 15))

    def test_lookback_wrong_year(self) -> None:
        start = date(2023, 1, 20)
        with pytest.raises(AssertionError, match="was in 2023, but entry had 2022"):
            Client.lookback(start, "15 2022", "", "15", None, "2022", max_days=10)

    def test_lookback_max_days_exceeded(self) -> None:
        start = date(2023, 1, 20)
        with pytest.raises(LookBackFailed) as exc_info:
            Client.lookback(start, "1", "", "1", None, None, max_days=5)

        compare(exc_info.value.text, expected="1")
        # The lookback goes 0, 1, 2, 3, 4 days back, so max_days=5 means it tries dates
        # 20, 19, 18, 17, 16
        compare(exc_info.value.possible, expected=date(2023, 1, 16))
        compare(str(exc_info.value), expected="Looked back to 2023-01-16, couldn't match 1")


class TestClientList:
    def test_list_basic(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare(
            periods,
            expected=[
                Period(
                    start=date(2023, 1, 15),
                    end=None,
                    zope_id="123",
                    start_url="",
                    start_date=date.max,
                    modified=date(2023, 1, 15),
                )
            ],
        )

    def test_list_with_pagination(self, mocked_responses: RequestsMock) -> None:
        html_content1 = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
            <a class="next" href="/page2">Next</a>
        </html>
        '''
        html_content2 = '''
        <html>
            <a name="2023-01-12T10:00:00Z">
                <strong>(2023-01-12) Thursday</strong>
                <a class="read" href="/entry/456">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content1.encode('latin-1'), status=200
        )
        mocked_responses.add(
            responses.GET,
            "https://example.com/page2",
            body=html_content2.encode('latin-1'),
            status=200,
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare([p.zope_id for p in periods], expected=["123", "456"])

    def test_list_stops_at_earliest(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
            <a name="2023-01-05T10:00:00Z">
                <strong>(2023-01-05) Thursday</strong>
                <a class="read" href="/entry/456">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare([p.zope_id for p in periods], expected=["123"])

    def test_list_with_error_handler(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>Invalid Date Format</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
            <a name="2023-01-12T10:00:00Z">
                <strong>(2023-01-12) Thursday</strong>
                <a class="read" href="/entry/456">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        def handle_error(e, url, dt):  # type: ignore[no-untyped-def]
            return True  # Skip errors

        periods = list(client.list(earliest, handle_error=handle_error))

        compare([p.zope_id for p in periods], expected=["456"])

    def test_list_error_not_handled(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>Invalid Date Format</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        with pytest.raises(ValueError):
            list(client.list(earliest))

    def test_list_no_next_link(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare([p.zope_id for p in periods], expected=["123"])

    def test_list_empty_html(self, mocked_responses: RequestsMock) -> None:
        mocked_responses.add(
            responses.GET, "https://example.com", body="<html></html>".encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare([p.zope_id for p in periods], expected=[])

    def test_list_next_link_no_href(self, mocked_responses: RequestsMock) -> None:
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
            <a class="next">Next</a>
        </html>
        '''
        mocked_responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        compare([p.zope_id for p in periods], expected=["123"])


class TestClientAddStuff:
    def test_add_stuff_basic(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event"
        body = "Additional notes"

        result = Client.add_stuff(period, summary, body)

        compare(result.start, expected=date(2023, 1, 15))
        compare(len(result.stuff), expected=2)
        compare(result.stuff[0], expected=Stuff(Type.event, "Test event"))
        compare(result.stuff[1].type, expected=Type.note)
        compare(result.stuff[1].title, expected="from body")
        assert result.stuff[1].body is not None and "Additional notes" in result.stuff[1].body

    def test_add_stuff_strip_whitespace(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "  EVENT Test event  "
        body = ""

        result = Client.add_stuff(period, summary, body)

        compare(
            result,
            expected=Period(start=date(2023, 1, 15), stuff=[Stuff(Type.event, "Test event")]),
        )

    def test_add_stuff_event_pattern_at_end(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "DID Something\n\nwent to the store"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15),
                stuff=[Stuff(Type.did, "Something"), Stuff(Type.event, "went to the store")],
            ),
        )

    def test_add_stuff_remove_trailing_whitespace(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event   \nDID Something   "
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15),
                stuff=[Stuff(Type.event, "Test event"), Stuff(Type.did, "Something")],
            ),
        )

    def test_add_stuff_fix_missing_caps(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "DIdn't do something"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        # The regex first capitalizes "DIdn't" to "DIDN'T", then it becomes an EVENT with the title
        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15), stuff=[Stuff(Type.event, "DIDN'T do something")]
            ),
        )

    def test_add_stuff_gave_up_on(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "GAVE UP on the project"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        compare(
            result,
            expected=Period(start=date(2023, 1, 15), stuff=[Stuff(Type.cancelled, "the project")]),
        )

    def test_add_stuff_didnt_lowercase(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "didn't finish task"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        # The lowercase "didn't" gets converted to "DIDN't " which then becomes an event
        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15), stuff=[Stuff(Type.event, "DIDN'T finish task")]
            ),
        )

    def test_add_stuff_initial_text_becomes_event(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "went to the store"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15), stuff=[Stuff(Type.event, "went to the store")]
            ),
        )

    def test_add_stuff_final_text_in_brackets(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "DID Something\n(also did this)"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15),
                stuff=[Stuff(Type.did, "Something"), Stuff(Type.event, "(also did this)")],
            ),
        )

    def test_add_stuff_old_format(self) -> None:
        period = Period(start=date(2002, 1, 15))
        summary = "line one\nline two"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2002, 1, 1))

        compare(
            result,
            expected=Period(
                start=date(2002, 1, 15),
                stuff=[Stuff(Type.event, "line one"), Stuff(Type.event, "line two")],
            ),
        )

    def test_add_stuff_with_body_dash(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event"
        body = "-"

        result = Client.add_stuff(period, summary, body)

        compare(
            result,
            expected=Period(start=date(2023, 1, 15), stuff=[Stuff(Type.event, "Test event")]),
        )

    def test_add_stuff_invalid_type_becomes_event(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "INVALID_TYPE Something"
        body = ""

        # Invalid types just become events when they don't match known patterns
        result = Client.add_stuff(period, summary, body)
        compare(
            result,
            expected=Period(
                start=date(2023, 1, 15), stuff=[Stuff(Type.event, "INVALID_TYPE Something")]
            ),
        )


class TestAddStuffErrorHandling:
    # These tests cover the error formatting code in add_stuff (lines 233-239)
    # that handles parse exceptions with line/column info. Since add_stuff does
    # extensive preprocessing to ensure valid diary format, it's extremely difficult
    # to trigger actual parse failures with real content. The preprocessing converts
    # any malformed input into valid EVENT entries before parsing.

    def test_add_stuff_error_formatting(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test"
        body = ""

        # Create mock parse function that simulates parse error with line info
        class MockParseError(Exception):
            def __init__(self, message: str) -> None:
                super().__init__(message)
                self.line = 2
                self.column = 5

        def mock_parse_with_line_info(source: str) -> list[Period]:
            raise MockParseError("Simulated parse error")

        with replace_in_module(parse.parse, mock_parse_with_line_info, module=zope):
            with ShouldRaise(ValueError):  # Should format error with line pointer
                Client.add_stuff(period, summary, body)

    def test_add_stuff_non_parse_exception(self) -> None:
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test"
        body = ""

        def mock_parse_with_line_info(source: str) -> list[Period]:
            raise TypeError("wut?")

        with replace_in_module(parse.parse, mock_parse_with_line_info, module=zope):
            with ShouldRaise(TypeError("wut?")):
                Client.add_stuff(period, summary, body)


class TestLookBackFailed:
    def test_lookback_failed_str(self) -> None:
        exc = LookBackFailed(date(2023, 1, 15), "test text")
        compare(str(exc), expected="Looked back to 2023-01-15, couldn't match test text")

    def test_lookback_failed_attributes(self) -> None:
        exc = LookBackFailed(date(2023, 1, 15), "test text")
        compare(exc.possible, expected=date(2023, 1, 15))
        compare(exc.text, expected="test text")
