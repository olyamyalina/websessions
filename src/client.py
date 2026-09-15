from __future__ import annotations

import socket
from typing import Any

from src.protocol import read_packet, send_packet


class RPCError(RuntimeError):
    """Error returned by the RPC server."""


class RPCClient:

    operations = {
        "create_account": 1,
        "get_all_accounts": 2,
        "get_account_by_uid": 3,
        "edit_account": 4,
        "create_message": 5,
        "get_all_messages": 6,
        "get_message_by_uid": 7,
        "edit_message": 8,
        "create_feedback": 9,
        "get_all_feedbacks": 10,
        "get_feedback_by_uid": 11,
        "edit_feedback": 12,
        "get_data_sample": 13,
    }

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9000,
        timeout: float = 5.0,
    ) -> None:
        self.address = (host, port)
        self.timeout = timeout

    def _call(self, name: str, **arguments: Any) -> Any:
        operation = self.operations[name]
        with socket.create_connection(self.address, self.timeout) as connection:
            send_packet(connection, operation, arguments)
            response_operation, response = read_packet(connection)
        if response_operation != operation:
            raise RPCError("Код операции в ответе не совпадает с запросом")
        if not response.get("ok"):
            raise RPCError(response.get("message", "Неизвестная ошибка RPC"))
        return response.get("result")

    @staticmethod
    def _record(value: list[Any] | None) -> tuple | None:
        return None if value is None else tuple(value)

    @classmethod
    def _records(cls, values: list[list[Any]]) -> list[tuple]:
        return [tuple(value) for value in values]

    def create_account(self, ip: str) -> tuple:
        return self._record(self._call("create_account", ip=ip))

    def get_all_accounts(self) -> list[tuple]:
        return self._records(self._call("get_all_accounts"))

    def get_account_by_uid(self, uid: int) -> tuple | None:
        return self._record(self._call("get_account_by_uid", uid=uid))

    def edit_account(self, uid: int, ip: str | None = None) -> tuple:
        return self._record(self._call("edit_account", uid=uid, ip=ip))

    def create_message(
        self,
        argument: str,
        account: int,
        completed: int,
    ) -> tuple:
        return self._record(
            self._call(
                "create_message",
                argument=argument,
                account=account,
                completed=completed,
            )
        )

    def get_all_messages(self) -> list[tuple]:
        return self._records(self._call("get_all_messages"))

    def get_message_by_uid(self, uid: int) -> tuple | None:
        return self._record(self._call("get_message_by_uid", uid=uid))

    def edit_message(
        self,
        uid: int,
        argument: str | None = None,
        account: int | None = None,
        completed: int | None = None,
    ) -> tuple:
        return self._record(
            self._call(
                "edit_message",
                uid=uid,
                argument=argument,
                account=account,
                completed=completed,
            )
        )

    def create_feedback(
        self,
        result: str,
        status: str,
        failure: str,
        message: int,
    ) -> tuple:
        return self._record(
            self._call(
                "create_feedback",
                result=result,
                status=status,
                failure=failure,
                message=message,
            )
        )

    def get_all_feedbacks(self) -> list[tuple]:
        return self._records(self._call("get_all_feedbacks"))

    def get_feedback_by_uid(self, uid: int) -> tuple | None:
        return self._record(self._call("get_feedback_by_uid", uid=uid))

    def edit_feedback(
        self,
        uid: int,
        result: str | None = None,
        status: str | None = None,
        failure: str | None = None,
        message: int | None = None,
    ) -> tuple:
        return self._record(
            self._call(
                "edit_feedback",
                uid=uid,
                result=result,
                status=status,
                failure=failure,
                message=message,
            )
        )

    def get_data_sample(self) -> list[tuple]:
        return self._records(self._call("get_data_sample"))
