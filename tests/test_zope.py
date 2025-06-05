import re
from datetime import date, datetime, timedelta
from unittest.mock import Mock

import pytest
import responses
from bs4 import BeautifulSoup
from requests import HTTPError

from objects import Period, Stuff, Type
from zope import Client, LookBackFailed


@pytest.fixture
def client():
    return Client(url="https://example.com", username="testuser", password="testpass")


class TestClient:

    def test_init(self, client):
        assert client.url == "https://example.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.session.auth == ("testuser", "testpass")

    @responses.activate
    def test_request_relative_url(self, client):
        responses.add(responses.GET, "https://example.com/test", body="success", status=200)

        result = client.request("get", "/test")
        assert result.text == "success"
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == "https://example.com/test"
        assert "Authorization" in request.headers

    @responses.activate
    def test_request_absolute_url(self, client):
        responses.add(responses.GET, "https://other.com/test", body="success", status=200)

        result = client.request("get", "https://other.com/test", absolute=True)
        assert result.text == "success"
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == "https://other.com/test"

    @responses.activate
    def test_request_with_kwargs(self, client):
        responses.add(responses.POST, "https://example.com/test", body="success", status=200)

        result = client.request("post", "/test", json={"key": "value"})
        assert result.text == "success"
        assert len(responses.calls) == 1

    @responses.activate
    def test_request_raises_for_status(self, client):
        responses.add(responses.GET, "https://example.com/test", body="error", status=404)

        with pytest.raises(HTTPError):
            client.request("get", "/test")

    @responses.activate
    def test_get(self, client):
        responses.add(responses.GET, "https://example.com/test", body="success", status=200)

        result = client.get("/test")
        assert result.text == "success"

    @responses.activate
    def test_get_absolute(self, client):
        responses.add(responses.GET, "https://other.com/test", body="success", status=200)

        result = client.get("https://other.com/test", absolute=True)
        assert result.text == "success"

    @responses.activate
    def test_get_soup(self, client):
        html_content = '<html><body><h1>Test</h1></body></html>'
        responses.add(
            responses.GET,
            "https://example.com/test",
            body=html_content.encode('latin-1'),
            status=200,
        )

        soup = client.get_soup("/test")
        assert isinstance(soup, BeautifulSoup)
        assert soup.find('h1').text == "Test"

    @responses.activate
    def test_get_soup_absolute(self, client):
        html_content = '<html><body><h1>Test</h1></body></html>'
        responses.add(
            responses.GET, "https://other.com/test", body=html_content.encode('latin-1'), status=200
        )

        soup = client.get_soup("https://other.com/test", absolute=True)
        assert isinstance(soup, BeautifulSoup)
        assert soup.find('h1').text == "Test"

    @responses.activate
    def test_post(self, client):
        responses.add(responses.POST, "https://example.com/test", body="success", status=200)

        result = client.post("/test", {"key": "value"})
        assert result.text == "success"
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "key=value" in request.body

    def test_post_data_basic(self, client):
        period = Period(start=date(2023, 1, 15))
        period.stuff = [Stuff(Type.event, "Test event")]

        data = client._post_data(period)

        assert data['title'] == "(2023-01-15) Sunday"
        assert data['author'] == "-"
        assert data['summary'] == b"EVENT Test event"
        assert data['encoding'] == "Plain"
        assert data['addPosting:method'] == " Add "

    def test_post_data_unicode_error(self, client):
        period = Period(start=date(2023, 1, 15))
        # Create a Stuff with content that can't be encoded in latin-1
        stuff = Stuff(Type.event, "Test with emoji 😀")
        period.stuff = [stuff]

        with pytest.raises(Exception, match="'latin-1' codec can't encode character"):
            client._post_data(period)

    @responses.activate
    def test_add(self, client):
        responses.add(responses.POST, "https://example.com", body="success", status=200)

        period = Period(start=date(2023, 1, 15))
        period.stuff = [Stuff(Type.event, "Test event")]

        client.add(period)

        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "addPosting%3Amethod=+Add+" in request.body

    @responses.activate
    def test_update(self, client):
        responses.add(responses.POST, "https://example.com/123", body="success", status=200)

        period = Period(start=date(2023, 1, 15), zope_id="123")
        period.stuff = [Stuff(Type.event, "Updated event")]

        client.update(period)

        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == "https://example.com/123"
        assert "edit%3Amethod=Change" in request.body

    def test_update_without_zope_id(self, client):
        period = Period(start=date(2023, 1, 15))

        with pytest.raises(AssertionError):
            client.update(period)


class TestClientInferDate:
    def test_infer_date_with_date_format(self):
        result, end = Client.infer_date("(2023-01-15) Sunday")
        assert result == date(2023, 1, 15)
        assert end is None

    def test_infer_date_format_mismatch(self):
        with pytest.raises(AssertionError, match="was a Sunday, got"):
            Client.infer_date("(2023-01-15) Monday")

    def test_infer_date_day_name_only_with_previous(self):
        previous = date(2023, 1, 20)  # Friday
        result, end = Client.infer_date("Tuesday", previous)
        assert result == date(2023, 1, 17)
        assert end is None

    def test_infer_date_day_name_only_without_previous(self):
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("Tuesday")

    def test_infer_date_day_name_not_found(self):
        previous = date(2023, 1, 15)  # Sunday
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("NotADay", previous)

    def test_infer_date_bad_format(self):
        with pytest.raises(ValueError, match="Bad format"):
            Client.infer_date("invalid date format")

    def test_infer_date_single_day_with_previous(self):
        previous = date(2023, 1, 20)
        with pytest.raises(LookBackFailed):
            Client.infer_date("15", previous)

    def test_infer_date_single_day_without_previous(self):
        with pytest.raises(ValueError, match="Need previous date for"):
            Client.infer_date("15")

    def test_infer_date_day_with_month(self):
        previous = date(2023, 1, 20)  # Close enough for 5-day lookback
        result, end = Client.infer_date("16 Jan", previous)
        assert result == date(2023, 1, 16)
        assert end is None

    def test_infer_date_full_date(self):
        previous = date(2023, 1, 20)  # Close enough for 5-day lookback
        result, end = Client.infer_date("16 Jan 2023", previous)
        assert result == date(2023, 1, 16)
        assert end is None

    def test_infer_date_range_with_end_day(self):
        previous = date(2023, 1, 20)
        # These patterns cause TypeError in lookback due to None day_number
        with pytest.raises(TypeError):
            Client.infer_date("15 - 17", previous)

    def test_infer_date_range_with_to(self):
        previous = date(2023, 1, 20)
        # These patterns cause TypeError in lookback due to None day_number
        with pytest.raises(TypeError):
            Client.infer_date("15 to 17", previous)

    def test_infer_date_range_full_dates(self):
        previous = date(2023, 1, 20)  # Use January so months match
        result, end = Client.infer_date("15 Jan 2023 - 17 Jan 2023", previous)
        assert result == date(2023, 1, 15)
        assert end == date(2023, 1, 17)


class TestClientLookback:
    def test_lookback_basic(self):
        start = date(2023, 1, 20)
        result = Client.lookback(start, "15", None, "15", None, None, max_days=10)
        assert result == date(2023, 1, 15)

    def test_lookback_with_day_name(self):
        start = date(2023, 1, 20)  # Friday
        result = Client.lookback(start, "Tuesday 17", "Tuesday", "17", None, None, max_days=10)
        assert result == date(2023, 1, 17)

    def test_lookback_with_day_name_short(self):
        start = date(2023, 1, 20)  # Friday
        result = Client.lookback(start, "Tue 17", "Tue", "17", None, None, max_days=10)
        assert result == date(2023, 1, 17)

    def test_lookback_wrong_day_name(self):
        start = date(2023, 1, 20)  # Friday
        with pytest.raises(AssertionError, match="was a Tuesday, but entry had Wednesday"):
            Client.lookback(start, "Wednesday 17", "Wednesday", "17", None, None, max_days=10)

    def test_lookback_with_month(self):
        start = date(2023, 1, 20)  # Start in January
        result = Client.lookback(start, "15 January", None, "15", "January", None, max_days=10)
        assert result == date(2023, 1, 15)

    def test_lookback_with_month_short(self):
        start = date(2023, 1, 20)  # Start in January
        result = Client.lookback(start, "15 Jan", None, "15", "Jan", None, max_days=10)
        assert result == date(2023, 1, 15)

    def test_lookback_with_month_alias(self):
        start = date(2023, 9, 20)  # Start in September
        result = Client.lookback(start, "15 Sept", None, "15", "Sept", None, max_days=10)
        assert result == date(2023, 9, 15)

    def test_lookback_wrong_month(self):
        start = date(2023, 1, 20)  # Start in January
        with pytest.raises(AssertionError, match="was in January, but entry had February"):
            Client.lookback(start, "15 February", None, "15", "February", None, max_days=10)

    def test_lookback_with_year(self):
        start = date(2023, 1, 20)  # Start in 2023
        result = Client.lookback(start, "15 2023", None, "15", None, "2023", max_days=10)
        assert result == date(2023, 1, 15)

    def test_lookback_wrong_year(self):
        start = date(2023, 1, 20)
        with pytest.raises(AssertionError, match="was in 2023, but entry had 2022"):
            Client.lookback(start, "15 2022", None, "15", None, "2022", max_days=10)

    def test_lookback_max_days_exceeded(self):
        start = date(2023, 1, 20)
        with pytest.raises(LookBackFailed) as exc_info:
            Client.lookback(start, "1", None, "1", None, None, max_days=5)

        assert exc_info.value.text == "1"
        # The lookback goes 0, 1, 2, 3, 4 days back, so max_days=5 means it tries dates 20, 19, 18, 17, 16
        assert exc_info.value.possible == date(2023, 1, 16)
        assert str(exc_info.value) == "Looked back to 2023-01-16, couldn't match 1"


class TestClientList:
    @responses.activate
    def test_list_basic(self):
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 1
        period = periods[0]
        assert period.start == date(2023, 1, 15)
        assert period.end is None
        assert period.zope_id == "123"
        assert period.modified == date(2023, 1, 15)

    @responses.activate
    def test_list_with_pagination(self):
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
        responses.add(
            responses.GET, "https://example.com", body=html_content1.encode('latin-1'), status=200
        )
        responses.add(
            responses.GET,
            "https://example.com/page2",
            body=html_content2.encode('latin-1'),
            status=200,
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 2
        assert periods[0].zope_id == "123"
        assert periods[1].zope_id == "456"

    @responses.activate
    def test_list_stops_at_earliest(self):
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
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 1
        assert periods[0].zope_id == "123"

    @responses.activate
    def test_list_with_error_handler(self):
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
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        def handle_error(e, url, dt):
            return True  # Skip errors

        periods = list(client.list(earliest, handle_error=handle_error))

        assert len(periods) == 1
        assert periods[0].zope_id == "456"

    @responses.activate
    def test_list_error_not_handled(self):
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>Invalid Date Format</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        with pytest.raises(ValueError):
            list(client.list(earliest))

    @responses.activate
    def test_list_no_next_link(self):
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
        </html>
        '''
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 1

    @responses.activate
    def test_list_empty_html(self):
        responses.add(
            responses.GET, "https://example.com", body="<html></html>".encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 0

    @responses.activate
    def test_list_next_link_no_href(self):
        html_content = '''
        <html>
            <a name="2023-01-15T10:00:00Z">
                <strong>(2023-01-15) Sunday</strong>
                <a class="read" href="/entry/123">Read</a>
            </a>
            <a class="next">Next</a>
        </html>
        '''
        responses.add(
            responses.GET, "https://example.com", body=html_content.encode('latin-1'), status=200
        )

        client = Client("https://example.com", "user", "pass")
        earliest = date(2023, 1, 10)

        periods = list(client.list(earliest))

        assert len(periods) == 1


class TestClientAddStuff:
    def test_add_stuff_basic(self):
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event"
        body = "Additional notes"

        result = Client.add_stuff(period, summary, body)

        assert result.start == date(2023, 1, 15)
        assert len(result.stuff) == 2
        assert result.stuff[0].type == Type.event
        assert result.stuff[0].title == "Test event"
        assert result.stuff[1].type == Type.note
        assert result.stuff[1].title == "from body"
        assert "Additional notes" in result.stuff[1].body

    def test_add_stuff_strip_whitespace(self):
        period = Period(start=date(2023, 1, 15))
        summary = "  EVENT Test event  "
        body = ""

        result = Client.add_stuff(period, summary, body)

        assert result.stuff[0].title == "Test event"

    def test_add_stuff_event_pattern_at_end(self):
        period = Period(start=date(2023, 1, 15))
        summary = "DID Something\n\nwent to the store"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        assert len(result.stuff) == 2
        assert result.stuff[0].type == Type.did
        assert result.stuff[1].type == Type.event
        assert result.stuff[1].title == "went to the store"

    def test_add_stuff_remove_trailing_whitespace(self):
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event   \nDID Something   "
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        # Check that trailing whitespace is removed
        source_lines = str(result).split('\n')
        for line in source_lines:
            if line.strip():  # Skip empty lines
                assert not line.endswith(' '), f"Line '{line}' has trailing whitespace"

    def test_add_stuff_fix_missing_caps(self):
        period = Period(start=date(2023, 1, 15))
        summary = "DIdn't do something"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        # The regex first capitalizes "DIdn't" to "DIDN'T", then it becomes an EVENT with the title
        assert result.stuff[0].type == Type.event
        assert result.stuff[0].title == "DIDN'T do something"

    def test_add_stuff_gave_up_on(self):
        period = Period(start=date(2023, 1, 15))
        summary = "GAVE UP on the project"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        assert result.stuff[0].type == Type.cancelled
        assert result.stuff[0].title == "the project"

    def test_add_stuff_didnt_lowercase(self):
        period = Period(start=date(2023, 1, 15))
        summary = "didn't finish task"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        # The lowercase "didn't" gets converted to "DIDN't " which then becomes an event
        assert result.stuff[0].type == Type.event
        assert result.stuff[0].title == "DIDN'T finish task"

    def test_add_stuff_initial_text_becomes_event(self):
        period = Period(start=date(2023, 1, 15))
        summary = "went to the store"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        assert result.stuff[0].type == Type.event
        assert result.stuff[0].title == "went to the store"

    def test_add_stuff_final_text_in_brackets(self):
        period = Period(start=date(2023, 1, 15))
        summary = "DID Something\n(also did this)"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2023, 1, 1))

        assert len(result.stuff) == 2
        assert result.stuff[0].type == Type.did
        assert result.stuff[1].type == Type.event
        assert result.stuff[1].title == "(also did this)"

    def test_add_stuff_old_format(self):
        period = Period(start=date(2002, 1, 15))
        summary = "line one\nline two"
        body = ""

        result = Client.add_stuff(period, summary, body, date(2002, 1, 1))

        assert len(result.stuff) == 2
        assert all(stuff.type == Type.event for stuff in result.stuff)
        assert result.stuff[0].title == "line one"
        assert result.stuff[1].title == "line two"

    def test_add_stuff_with_body_dash(self):
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test event"
        body = "-"

        result = Client.add_stuff(period, summary, body)

        assert len(result.stuff) == 1  # Body with just "-" is ignored

    def test_add_stuff_invalid_type_becomes_event(self):
        period = Period(start=date(2023, 1, 15))
        summary = "INVALID_TYPE Something"
        body = ""

        # Invalid types just become events when they don't match known patterns
        result = Client.add_stuff(period, summary, body)
        assert result.stuff[0].type == Type.event
        assert result.stuff[0].title == "INVALID_TYPE Something"

    def test_add_stuff_parse_error_without_line_info(self):
        # Mock a period that will cause a parse error without line info
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test"
        body = ""

        # We need to create a malformed source that the parser can't handle
        # Let's patch the parse function to simulate an error without line info
        original_parse = Client.add_stuff.__globals__['parse']

        def mock_parse(source):
            # Simulate parse error without line attribute
            error = Exception("Parse error without line info")
            raise error

        Client.add_stuff.__globals__['parse'] = mock_parse

        try:
            with pytest.raises(Exception, match="Parse error without line info"):
                Client.add_stuff(period, summary, body)
        finally:
            # Restore original parse function
            Client.add_stuff.__globals__['parse'] = original_parse

    def test_add_stuff_parse_error_with_line_info(self):
        # Test the error formatting code path
        period = Period(start=date(2023, 1, 15))
        summary = "EVENT Test"
        body = ""

        # Mock parse to raise an error with line and column info
        original_parse = Client.add_stuff.__globals__['parse']

        def mock_parse(source):
            error = Exception("Parse error with line info")
            error.line = 2  # Second line
            error.column = 5  # Fifth column
            raise error

        Client.add_stuff.__globals__['parse'] = mock_parse

        try:
            with pytest.raises(ValueError) as exc_info:
                Client.add_stuff(period, summary, body)

            # Check that the error message includes formatted output
            error_msg = str(exc_info.value)
            assert "Parse error with line info" in error_msg
            assert "^" in error_msg  # Pointer should be included
        finally:
            # Restore original parse function
            Client.add_stuff.__globals__['parse'] = original_parse


class TestLookBackFailed:
    def test_lookback_failed_str(self):
        exc = LookBackFailed(date(2023, 1, 15), "test text")
        assert str(exc) == "Looked back to 2023-01-15, couldn't match test text"

    def test_lookback_failed_attributes(self):
        exc = LookBackFailed(date(2023, 1, 15), "test text")
        assert exc.possible == date(2023, 1, 15)
        assert exc.text == "test text"
