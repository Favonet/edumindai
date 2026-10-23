import os
import re
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/teste.db"
os.environ["EDUMIND_ARQ_CHAVE"] = f"{_tmp}/chave"
os.environ.pop("ANTHROPIC_API_KEY", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import seed  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def banco():
    seed.popular()


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


def csrf_de(html: str) -> str:
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


@pytest.fixture
def entrar(cliente):
    def _entrar(email, senha="edumind123"):
        token = csrf_de(cliente.get("/login").text)
        return cliente.post("/login", data={"email": email, "senha": senha, "csrf": token})
    return _entrar
