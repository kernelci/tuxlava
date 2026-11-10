import pytest
import requests

from tuxlava.exceptions import InvalidArgument
from tuxlava.jobs import Job
from tuxlava.tests.yamltest import YamlTest, yaml_test_minutes

TEXT = """\
# a comment
- test:
    timeout:
      minutes: 5
"""


def test_yaml_test_from_file(tmp_path):
    path = tmp_path / "oeqa.yaml"
    path.write_text(TEXT, encoding="utf-8")

    test = YamlTest(f"file://{path}")
    assert test.name == "oeqa"
    assert test.timeout == 5
    assert test.render() == TEXT


def test_yaml_test_from_http(mocker):
    get = mocker.patch("tuxlava.tests.yamltest.requests_get")
    get.return_value.status_code = 200
    get.return_value.content = TEXT.encode("utf-8")

    test = YamlTest("https://example.com/tests/oeqa.yaml")
    get.assert_called_once_with("https://example.com/tests/oeqa.yaml")
    assert test.name == "oeqa"
    assert test.timeout == 5
    assert test.render() == TEXT


def test_yaml_test_from_http_fails(mocker):
    get = mocker.patch("tuxlava.tests.yamltest.requests_get")
    get.return_value.status_code = 404

    with pytest.raises(InvalidArgument) as exc:
        YamlTest("https://example.com/oeqa.yaml")
    assert "https://example.com/oeqa.yaml" in str(exc.value)
    assert "404" in str(exc.value)


def test_yaml_test_ends_with_a_newline(tmp_path):
    path = tmp_path / "oeqa.yaml"
    path.write_text(TEXT.rstrip("\n"), encoding="utf-8")

    assert YamlTest(f"file://{path}").render() == TEXT


def test_yaml_test_keeps_the_last_newlines(tmp_path):
    path = tmp_path / "oeqa.yaml"
    path.write_text(TEXT + "\n\n", encoding="utf-8")

    assert YamlTest(f"file://{path}").render() == TEXT + "\n\n"


def test_yaml_test_minutes():
    text = """\
- test:
    timeout:
      minutes: 5
- test:
    timeout:
      minutes: 3
"""
    assert yaml_test_minutes("oeqa.yaml", text) == 8


@pytest.mark.parametrize(
    "text, expected",
    [
        ("- test: [\n", "invalid YAML"),
        ("test: {}\n", "YAML list"),
        ("- test:\n    timeout:\n      minutes: 1\n  extra: true\n", "item 1"),
        ("- deploy:\n    timeout:\n      minutes: 1\n", "item 1"),
        ("- test:\n    definitions: []\n", "job timeout"),
        ("- test:\n    timeout:\n      minutes: true\n", "positive integer"),
        ("- test:\n    timeout:\n      minutes: 0\n", "positive integer"),
        ("- test:\n    timeout:\n      minutes: -1\n", "positive integer"),
        ("- test:\n    timeout:\n      minutes: 1.5\n", "positive integer"),
        ("- test:\n    timeout:\n      minutes: '5'\n", "positive integer"),
        ("- test:\n    timeout:\n      hours: 2\n      minutes: 1\n", "no other"),
    ],
)
def test_yaml_test_minutes_invalid(text, expected):
    with pytest.raises(InvalidArgument) as exc:
        yaml_test_minutes("oeqa.yaml", text)
    assert str(exc.value).startswith("oeqa.yaml: ")
    assert expected in str(exc.value)


@pytest.mark.parametrize(
    "text",
    [
        "---\n" + TEXT,
        TEXT + "...\n",
        "  - test:\n      timeout:\n        minutes: 5\n",
        "[{test: {timeout: {minutes: 5}}}]\n",
    ],
)
def test_yaml_test_must_paste_into_the_job(tmp_path, text):
    path = tmp_path / "oeqa.yaml"
    path.write_text(text, encoding="utf-8")

    with pytest.raises(InvalidArgument) as exc:
        YamlTest(f"file://{path}")
    assert "column 0" in str(exc.value)


def test_yaml_test_from_a_directory(tmp_path):
    with pytest.raises(InvalidArgument) as exc:
        YamlTest(f"file://{tmp_path}")
    assert str(tmp_path) in str(exc.value)


def test_yaml_test_from_a_file_that_is_not_utf8(tmp_path):
    path = tmp_path / "oeqa.yaml"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(InvalidArgument) as exc:
        YamlTest(f"file://{path}")
    assert str(path) in str(exc.value)


def test_yaml_test_from_http_is_utf8(mocker):
    get = mocker.patch("tuxlava.tests.yamltest.requests_get")
    get.return_value.status_code = 200
    get.return_value.content = ("# \u00e5\n" + TEXT).encode("utf-8")
    get.return_value.text = "# \u00c3\u00a5\n" + TEXT

    assert YamlTest("https://example.com/oeqa.yaml").render() == "# \u00e5\n" + TEXT


def test_yaml_test_from_http_that_is_not_utf8(mocker):
    get = mocker.patch("tuxlava.tests.yamltest.requests_get")
    get.return_value.status_code = 200
    get.return_value.content = b"\xff\xfe"

    with pytest.raises(InvalidArgument) as exc:
        YamlTest("https://example.com/oeqa.yaml")
    assert "https://example.com/oeqa.yaml" in str(exc.value)


def test_yaml_test_from_http_without_network(mocker):
    get = mocker.patch("tuxlava.tests.yamltest.requests_get")
    get.side_effect = requests.ConnectionError("connection refused")

    with pytest.raises(InvalidArgument) as exc:
        YamlTest("https://example.com/oeqa.yaml")
    assert "https://example.com/oeqa.yaml" in str(exc.value)


@pytest.mark.parametrize("name", ['q".yaml', "a b.yaml", "a\\b.yaml"])
def test_yaml_test_name_must_be_plain(tmp_path, name):
    path = tmp_path / name
    path.write_text(TEXT, encoding="utf-8")

    with pytest.raises(InvalidArgument) as exc:
        YamlTest(f"file://{path}")
    assert "file name" in str(exc.value)


def test_yaml_test_from_a_url_without_a_file_name(mocker):
    mocker.patch("tuxlava.tests.yamltest.requests_get")

    with pytest.raises(InvalidArgument) as exc:
        YamlTest("https://example.com/tests/")
    assert "file name" in str(exc.value)


def test_job_takes_none_for_test_yaml():
    assert Job(device="qemu-arm64", test_yaml=None).test_yaml == []
