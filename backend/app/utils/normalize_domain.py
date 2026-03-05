from urllib.parse import urlparse
import re
import socket


DOMAIN_REGEX = re.compile(
    r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*\.[a-z]{2,63}$"
)


def domain_exists(domain: str) -> bool:
    """Verifica se o domínio resolve no DNS"""
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False


def normalize_domain(raw: str, check_dns: bool = False) -> str:
    """
    Normaliza domínio para comparação segura.

    Exemplos aceitos:
    - example.com
    - www.example.com
    - https://example.com
    - http://example.com/path
    """

    if not raw:
        raise ValueError("Domain cannot be empty")

    raw = raw.strip().lower()

    # força parse mesmo sem protocolo
    if "://" not in raw:
        raw = "http://" + raw

    parsed = urlparse(raw)

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid port") from exc

    domain = parsed.hostname  # remove porta automaticamente

    if not domain:
        raise ValueError("Invalid domain")

    # remove www
    if domain.startswith("www."):
        domain = domain[4:]

    # exceção para ambiente local de desenvolvimento
    if domain == "localhost":
        if port is not None:
            return f"localhost:{port}"
        return domain

    # valida formato
    if not DOMAIN_REGEX.match(domain):
        raise ValueError("Invalid domain format")

    # valida DNS (opcional)
    if check_dns and not domain_exists(domain):
        raise ValueError("Domain does not resolve in DNS")

    return domain