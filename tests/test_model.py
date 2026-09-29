import sys
import os
import threading
import time

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from hypothesis.stateful import RuleBasedStateMachine, rule
import hypothesis.strategies as st
from server import run_server
from client import RPCClient

VALID_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126), max_size=50
)

SERVER_THREAD = threading.Thread(target=run_server, daemon=True)
SERVER_THREAD.start()
time.sleep(1)


class RPCTestingMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.client = RPCClient()
        self.member_ids = []
        self.inst_ids = []
        self.resp_ids = []

    @rule(ip=VALID_TEXT, ua=VALID_TEXT)
    def test_create_member(self, ip, ua):
        res = self.client.create_member(ip, ua)
        if isinstance(res, dict) and "id" in res:
            self.member_ids.append(res["id"])

    @rule(arg=VALID_TEXT, desc=VALID_TEXT, state=VALID_TEXT)
    def test_create_instruction(self, arg, desc, state):
        mem = self.member_ids[0] if self.member_ids else 0
        res = self.client.create_instruction(arg, mem, desc, state)
        if isinstance(res, dict) and "id" in res:
            self.inst_ids.append(res["id"])

    @rule(
        res=VALID_TEXT,
        state=VALID_TEXT,
        err=VALID_TEXT,
        ch=st.integers(min_value=0, max_value=1000),
        dur=st.integers(min_value=0, max_value=1000),
    )
    def test_create_response(self, res, state, err, ch, dur):
        inst = self.inst_ids[0] if self.inst_ids else 0
        resp = self.client.create_response(res, state, err, inst, ch, dur)
        if isinstance(resp, dict) and "id" in resp:
            self.resp_ids.append(resp["id"])

    @rule()
    def test_get_all_members(self):
        self.client.get_all_members()

    @rule()
    def test_get_all_instructions(self):
        self.client.get_all_instructions()

    @rule()
    def test_get_all_responses(self):
        self.client.get_all_responses()

    @rule()
    def test_get_member(self):
        if self.member_ids:
            self.client.get_member(self.member_ids[0])

    @rule()
    def test_get_instruction(self):
        if self.inst_ids:
            self.client.get_instruction(self.inst_ids[0])

    @rule()
    def test_get_response(self):
        if self.resp_ids:
            self.client.get_response(self.resp_ids[0])

    @rule(ip=VALID_TEXT, ua=VALID_TEXT)
    def test_edit_member(self, ip, ua):
        if self.member_ids:
            self.client.edit_member(self.member_ids[0], ip, ua)

    @rule(arg=VALID_TEXT, desc=VALID_TEXT, state=VALID_TEXT)
    def test_edit_instruction(self, arg, desc, state):
        if self.inst_ids:
            mem = self.member_ids[0] if self.member_ids else 0
            self.client.edit_instruction(
                self.inst_ids[0], arg, mem, desc, state
            )

    @rule(
        res=VALID_TEXT,
        state=VALID_TEXT,
        err=VALID_TEXT,
        ch=st.integers(min_value=0, max_value=1000),
        dur=st.integers(min_value=0, max_value=1000),
    )
    def test_edit_response(self, res, state, err, ch, dur):
        if self.resp_ids:
            inst = self.inst_ids[0] if self.inst_ids else 0
            self.client.edit_response(
                self.resp_ids[0], res, state, err, inst, ch, dur
            )

    @rule()
    def test_join_data(self):
        self.client.join_data()


TestRPC = RPCTestingMachine.TestCase
