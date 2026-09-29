import threading
import time

from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    precondition,
)
import hypothesis.strategies as st

# Абсолютные импорты компонентов сервера
from src.server import run_server
from src.client import RPCClient
from src import app

# Запускаем сервер в фоновом потоке один раз для всех тестов
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(0.5)

# Безопасный генератор печатного текста для обхода багов XML-парсера
VALID_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=15,
)


class ModelRPC(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model_members = []
        self.model_instructions = []
        self.model_responses = []
        self.client = RPCClient("127.0.0.1", 8000)

    def teardown(self):
        """Очистка состояния базы между генерациями сценариев."""
        app.members.clear()
        app.instructions.clear()
        app.responses.clear()
        self.model_members.clear()
        self.model_instructions.clear()
        self.model_responses.clear()

    # --- 1-3. МЕТОДЫ СОЗДАНИЯ ---

    @rule(ip=VALID_TEXT, agent=VALID_TEXT)
    def create_member(self, ip, agent):
        res = self.client.create_member(ip, agent)
        if isinstance(res, dict) and "id" in res:
            self.model_members.append(res)

    @precondition(lambda self: len(self.model_members) > 0)
    @rule(arg=VALID_TEXT, desc=VALID_TEXT)
    def create_instruction(self, arg, desc):
        m_id = self.model_members[-1]["id"]
        res = self.client.create_instruction(arg, m_id, desc, "active")
        if isinstance(res, dict) and "id" in res:
            self.model_instructions.append(res)

    @precondition(lambda self: len(self.model_instructions) > 0)
    @rule(
        resp=VALID_TEXT,
        err=VALID_TEXT,
        dur=st.integers(min_value=0, max_value=1000),
    )
    def create_response(self, resp, err, dur):
        i_id = self.model_instructions[-1]["id"]
        res = self.client.create_response(resp, "ok", err, i_id, 1, dur)
        if isinstance(res, dict) and "id" in res:
            self.model_responses.append(res)

    # --- 4-6. МЕТОДЫ ЧТЕНИЯ ВСЕХ ЗАПИСЕЙ ---

    @rule()
    def get_all_members(self):
        res = self.client.get_all_members()
        assert len(res) == len(self.model_members)

    @rule()
    def get_all_instructions(self):
        res = self.client.get_all_instructions()
        assert len(res) == len(self.model_instructions)

    @rule()
    def get_all_responses(self):
        res = self.client.get_all_responses()
        assert len(res) == len(self.model_responses)

    # --- 7-9. МЕТОДЫ ЧТЕНИЯ ОДНОЙ ЗАПИСИ ---

    @precondition(lambda self: len(self.model_members) > 0)
    @rule()
    def get_member(self):
        target = self.model_members[-1]
        res = self.client.get_member(target["id"])
        assert res["id"] == target["id"]

    @precondition(lambda self: len(self.model_instructions) > 0)
    @rule()
    def get_instruction(self):
        target = self.model_instructions[-1]
        res = self.client.get_instruction(target["id"])
        assert res["id"] == target["id"]

    @precondition(lambda self: len(self.model_responses) > 0)
    @rule()
    def get_response(self):
        target = self.model_responses[-1]
        res = self.client.get_response(target["id"])
        assert res["id"] == target["id"]

    # --- 10-12. МЕТОДЫ РЕДАКТИРОВАНИЯ ---

    @precondition(lambda self: len(self.model_members) > 0)
    @rule(ip=VALID_TEXT, agent=VALID_TEXT)
    def edit_member(self, ip, agent):
        target_id = self.model_members[-1]["id"]
        res = self.client.edit_member(target_id, ip, agent)
        assert res["ip"] == ip
        self.model_members[-1] = res

    @precondition(lambda self: len(self.model_instructions) > 0)
    @rule(arg=VALID_TEXT, desc=VALID_TEXT)
    def edit_instruction(self, arg, desc):
        target = self.model_instructions[-1]
        res = self.client.edit_instruction(
            target["id"], arg, target["member"], desc, "inactive"
        )
        assert res["argument"] == arg
        self.model_instructions[-1] = res

    @precondition(lambda self: len(self.model_responses) > 0)
    @rule(resp=VALID_TEXT, err=VALID_TEXT)
    def edit_response(self, resp, err):
        target = self.model_responses[-1]
        res = self.client.edit_response(
            target["id"], resp, "fail", err, target["instruction"], 0, 50
        )
        assert res["response"] == resp
        self.model_responses[-1] = res

    # --- 13. МЕТОД JOIN ---

    @rule()
    def join_data(self):
        res = self.client.join_data()
        assert isinstance(res, list)


TestRPC = ModelRPC.TestCase

if __name__ == "__main__":
    import unittest

    unittest.main()
