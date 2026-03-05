import os
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

local_app_path = ROOT / "app"
if "app" in sys.modules:
    del sys.modules["app"]
app_module = types.ModuleType("app")
app_module.__path__ = [str(local_app_path)]
sys.modules["app"] = app_module

models_module = types.ModuleType("app.models")
models_module.__path__ = [str(local_app_path / "models")]
sys.modules["app.models"] = models_module

# Precarrega modelos reais com relacionamentos para evitar falha de mapper
import app.models.user  # noqa: E402,F401
import app.models.domain  # noqa: E402,F401
import app.models.integrations  # noqa: E402,F401
import app.models.collections  # noqa: E402,F401

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("SLACK_CLIENT_ID", "test-client-id")
os.environ.setdefault("SLACK_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("SLACK_REDIRECT_URI", "http://localhost:8000/auth/slack/callback")
