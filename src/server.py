from __future__ import annotations

import argparse
import logging
import socketserver
import threading
from pathlib import Path
from typing import Any

from src import model as data_model
from src.protocol import read_packet, send_packet

OPERATIONS = {
    1: "create_account",
    2: "get_all_accounts",
    3: "get_account_by_uid",
    4: "edit_account",
    5: "create_message",
    6: "get_all_messages",
    7: "get_message_by_uid",
    8: "edit_message",
    9: "create_feedback",
    10: "get_all_feedbacks",
    11: "get_feedback_by_uid",
    12: "edit_feedback",
    13: "get_data_sample",
}


class RPCRequestHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        server = self.server
        while True:
            try:
                operation, arguments = read_packet(self.request)
            except EOFError:
                return
            server.logger.info(
                "client=%s operation=%s arguments=%r",
                self.client_address,
                operation,
                arguments,
            )
            response = self._dispatch(operation, arguments)
            send_packet(self.request, operation, response)

    def _dispatch(self, operation: int, arguments: Any) -> dict[str, Any]:
        try:
            name = OPERATIONS[operation]
            if not isinstance(arguments, dict):
                raise TypeError("Тело запроса должно быть JSON-объектом")
            with self.server.model_lock:
                result = getattr(self.server.model, name)(**arguments)
            return {"ok": True, "result": result}
        except (KeyError, TypeError, ValueError) as error:
            self.server.logger.warning("request failed: %s", error)
            return {
                "ok": False,
                "error": type(error).__name__,
                "message": str(error),
            }


class RPCServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        model: Any,
        logger: logging.Logger,
    ) -> None:
        super().__init__(address, RPCRequestHandler)
        self.model = model
        self.model_lock = threading.RLock()
        self.logger = logger


def _make_logger(journal_path: str) -> logging.Logger:
    logger = logging.getLogger(f"variant15.rpc.{journal_path}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.FileHandler(journal_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def create_server(
    host: str = "127.0.0.1",
    port: int = 9000,
    model: Any = None,
    journal_path: str = "journal.log",
) -> RPCServer:
    return RPCServer(
        (host, port),
        data_model if model is None else model,
        _make_logger(journal_path),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Variant 15 TCP RPC server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--journal", default="journal.log")
    args = parser.parse_args()
    Path(args.journal).parent.mkdir(parents=True, exist_ok=True)
    with create_server(
        args.host,
        args.port,
        journal_path=args.journal,
    ) as server:
        print(f"RPC server: {args.host}:{server.server_address[1]}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")


if __name__ == "__main__":
    main()
