"""Model-based tests for all 13 RPC methods."""

from __future__ import annotations

import datetime
import threading

from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
)

from src import model as data_model
from src.client import RPCClient, RPCError
from src.model import SAMPLE_WINDOW_SECONDS
from src.server import create_server

TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    max_size=16,
)
RPC_METHOD_COUNT = 13


class RPCStateMachine(RuleBasedStateMachine):
    """Compare the RPC service with a simplified dictionary model."""

    def __init__(self) -> None:
        super().__init__()
        self._clear_data_model()
        self.server = create_server(port=0, journal_path="test-journal.log")
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            kwargs={"poll_interval": 0.01},
            daemon=True,
        )
        self.thread.start()
        host, port = self.server.server_address
        self.client = RPCClient(host, port)
        self.accounts: dict[int, tuple] = {}
        self.messages: dict[int, tuple] = {}
        self.feedbacks: dict[int, tuple] = {}

    @initialize()
    def cover_every_rpc_method(self) -> None:
        """Call all 13 methods inside a Hypothesis-generated scenario."""
        account = self.client.create_account("127.0.0.1")
        self.accounts[account[0]] = account
        account = self.client.edit_account(account[0], "10.0.0.1")
        self.accounts[account[0]] = account

        message = self.client.create_message("seed", account[0], 0)
        self.messages[message[0]] = message
        message = self.client.edit_message(message[0], completed=1)
        self.messages[message[0]] = message

        feedback = self.client.create_feedback(
            "ok", "created", "", message[0]
        )
        self.feedbacks[feedback[0]] = feedback
        feedback = self.client.edit_feedback(feedback[0], status="checked")
        self.feedbacks[feedback[0]] = feedback
        self._compare_state()

    @rule(ip=TEXT)
    def create_account(self, ip: str) -> None:
        account = self.client.create_account(ip)
        self.accounts[account[0]] = account

    @rule(data=st.data(), ip=TEXT)
    def edit_account(self, data: st.DataObject, ip: str) -> None:
        uid = data.draw(st.sampled_from(sorted(self.accounts)))
        account = self.client.edit_account(uid, ip)
        self.accounts[uid] = account

    @rule(data=st.data(), argument=TEXT, completed=st.integers(-2, 2))
    def create_message(
        self,
        data: st.DataObject,
        argument: str,
        completed: int,
    ) -> None:
        account_uid = data.draw(st.sampled_from(sorted(self.accounts)))
        message = self.client.create_message(
            argument,
            account_uid,
            completed,
        )
        self.messages[message[0]] = message

    @rule(data=st.data(), argument=TEXT, completed=st.integers(-2, 2))
    def edit_message(
        self,
        data: st.DataObject,
        argument: str,
        completed: int,
    ) -> None:
        uid = data.draw(st.sampled_from(sorted(self.messages)))
        account_uid = data.draw(st.sampled_from(sorted(self.accounts)))
        message = self.client.edit_message(
            uid,
            argument=argument,
            account=account_uid,
            completed=completed,
        )
        self.messages[uid] = message

    @rule(data=st.data(), result=TEXT, status=TEXT, failure=TEXT)
    def create_feedback(
        self,
        data: st.DataObject,
        result: str,
        status: str,
        failure: str,
    ) -> None:
        message_uid = data.draw(st.sampled_from(sorted(self.messages)))
        feedback = self.client.create_feedback(
            result,
            status,
            failure,
            message_uid,
        )
        self.feedbacks[feedback[0]] = feedback

    @rule(data=st.data(), status=TEXT)
    def edit_feedback(self, data: st.DataObject, status: str) -> None:
        uid = data.draw(st.sampled_from(sorted(self.feedbacks)))
        message_uid = data.draw(st.sampled_from(sorted(self.messages)))
        feedback = self.client.edit_feedback(
            uid,
            status=status,
            message=message_uid,
        )
        self.feedbacks[uid] = feedback

    @rule()
    def reject_broken_foreign_key(self) -> None:
        try:
            self.client.create_message("broken", 10**9, 0)
        except RPCError:
            return
        raise AssertionError("Сервер принял несуществующий Account")

    @invariant()
    def state_matches_model(self) -> None:
        self._compare_state()

    def _compare_state(self) -> None:
        assert len(self.client.operations) == RPC_METHOD_COUNT
        assert self.client.get_all_accounts() == list(self.accounts.values())
        assert self.client.get_all_messages() == list(self.messages.values())
        actual_feedbacks = self.client.get_all_feedbacks()
        assert actual_feedbacks == list(self.feedbacks.values())

        account_uid = next(iter(self.accounts))
        message_uid = next(iter(self.messages))
        feedback_uid = next(iter(self.feedbacks))
        assert self.client.get_account_by_uid(account_uid) == (
            self.accounts[account_uid]
        )
        assert self.client.get_message_by_uid(message_uid) == (
            self.messages[message_uid]
        )
        assert self.client.get_feedback_by_uid(feedback_uid) == (
            self.feedbacks[feedback_uid]
        )
        assert self.client.get_data_sample() == self._expected_sample()

    def _expected_sample(self) -> list[tuple]:
        current_time = int(datetime.datetime.now().timestamp())
        threshold = current_time - SAMPLE_WINDOW_SECONDS
        result = []
        for account in self.accounts.values():
            if account[1] < threshold:
                continue
            arguments = [
                row[2]
                for row in self.messages.values()
                if row[3] == account[0]
            ]
            result.extend((account[2], value) for value in arguments)
            if not arguments:
                result.append((account[2], None))
        return result

    def teardown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)
        self._clear_data_model()

    @staticmethod
    def _clear_data_model() -> None:
        data_model.accounts.clear()
        data_model.messages.clear()
        data_model.feedbacks.clear()


TestRPC = RPCStateMachine.TestCase
TestRPC.settings = settings(
    max_examples=15,
    stateful_step_count=20,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
