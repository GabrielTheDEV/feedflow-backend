import pytest

import app.utils.normalize_domain as normalize_module


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("example.com", "example.com"),
        ("www.Example.com", "example.com"),
        ("https://example.com/path", "example.com"),
        ("api-v2.sub.example.com", "api-v2.sub.example.com"),
        ("localhost", "localhost"),
        ("LOCALHOST:5173", "localhost:5173"),
        ("http://localhost:3000/path", "localhost:3000"),
    ],
)
def test_normalize_domain_valid_inputs(raw, expected):
    assert normalize_module.normalize_domain(raw) == expected


@pytest.mark.parametrize(
    "raw,error_message",
    [
        ("", "Domain cannot be empty"),
        ("http://", "Invalid domain"),
        ("bad_domain!.com", "Invalid domain format"),
        ("http://-foo.com", "Invalid domain format"),
        ("localhost:abc", "Invalid port"),
        ("example.com:abc", "Invalid port"),
    ],
)
def test_normalize_domain_invalid_inputs(raw, error_message):
    with pytest.raises(ValueError, match=error_message):
        normalize_module.normalize_domain(raw)


def test_normalize_domain_dns_check_enabled_success(monkeypatch):
    monkeypatch.setattr(normalize_module, "domain_exists", lambda domain: domain == "example.com")

    assert normalize_module.normalize_domain("example.com", check_dns=True) == "example.com"


def test_normalize_domain_dns_check_enabled_failure(monkeypatch):
    monkeypatch.setattr(normalize_module, "domain_exists", lambda domain: False)

    with pytest.raises(ValueError, match="Domain does not resolve in DNS"):
        normalize_module.normalize_domain("example.com", check_dns=True)


def test_localhost_bypasses_dns_check(monkeypatch):
    def _fail_if_called(_):
        raise AssertionError("domain_exists should not be called for localhost")

    monkeypatch.setattr(normalize_module, "domain_exists", _fail_if_called)

    assert normalize_module.normalize_domain("localhost:5173", check_dns=True) == "localhost:5173"
