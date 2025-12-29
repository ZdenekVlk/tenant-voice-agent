from __future__ import annotations

import pytest

from app.utils.origin import normalize_origin


@pytest.mark.parametrize(
    "origin,referer,expected",
    [
        ("https://Example.COM", None, "example.com"),
        ("https://example.com/", None, "example.com"),
        ("https://example.com:8443/path", None, "example.com"),
        (None, "https://Sub.Example.com/path", "sub.example.com"),
        ("http://example.com/some/path", None, "example.com"),
        (None, None, None),
        ("null", None, None),
        ("not a url", None, None),
    ],
)
def test_normalize_origin(origin: str | None, referer: str | None, expected: str | None) -> None:
    assert normalize_origin(origin, referer) == expected
