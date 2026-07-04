from datetime import datetime, UTC
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.service as service_module


class FakeSession:
    def __init__(self, storage: dict):
        self.storage = storage

    def add(self, run) -> None:
        run.id = self.storage["next_id"]
        run.created_at = datetime.now(UTC)
        self.storage["runs"][run.id] = run
        self.storage["next_id"] += 1

    async def flush(self) -> None:
        pass

    async def get(self, model, pk):
        return self.storage["runs"].get(pk)

    async def execute(self, stmt):
        pk = stmt._where_criteria[0].right.value
        run = self.storage["runs"].get(pk)
        return SimpleNamespace(scalar_one_or_none=lambda: run)


class FakeSessionMaker:
    def __init__(self):
        self.storage = {"runs": {}, "next_id": 1}

    def begin(self):
        return self._ctx()

    def __call__(self):
        return self._ctx()

    def _ctx(self):
        session = FakeSession(self.storage)

        class Ctx:
            async def __aenter__(self_inner):
                return session

            async def __aexit__(self_inner, *args):
                return False

        return Ctx()


@pytest.fixture()
def client(monkeypatch) -> TestClient:
    monkeypatch.setattr(service_module, "async_session_maker", FakeSessionMaker())
    from app.main import app
    return TestClient(app)
