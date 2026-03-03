
from urllib.parse import urlparse
import re

def normalize_domain(self, raw: str) -> str:
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

    # 👇 força parse mesmo sem protocolo
    if "://" not in raw:
        raw = "http://" + raw

    parsed = urlparse(raw)

    domain = parsed.hostname  # 🔥 já remove porta automaticamente

    if not domain:
        raise ValueError("Invalid domain")

    if domain.startswith("www."):
        domain = domain[4:]

    # (opcional mas recomendado)
    if not re.match(r"^[a-z0-9.-]+$", domain):
        raise ValueError("Invalid domain format")

    return domain