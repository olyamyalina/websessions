from __future__ import annotations

import json
import socket
from typing import Any

HEADER_SIZE = 4
MAX_BODY_SIZE = (1 << 24) - 1
MIN_OPERATION_CODE = 0
MAX_OPERATION_CODE = (1 << 8) - 1


def _receive_exact(connection: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    received = 0
    while received < size:
        chunk = connection.recv(size - received)
        if not chunk:
            raise EOFError("Соединение закрыто до получения пакета")
        chunks.append(chunk)
        received += len(chunk)
    return b"".join(chunks)


def encode_packet(operation: int, payload: Any) -> bytes:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if not MIN_OPERATION_CODE <= operation <= MAX_OPERATION_CODE:
        raise ValueError("Код операции должен занимать один байт")
    if len(body) > MAX_BODY_SIZE:
        raise ValueError("Тело пакета превышает размер трехбайтового поля")
    return len(body).to_bytes(3, "little") + bytes([operation]) + body


def read_packet(connection: socket.socket) -> tuple[int, Any]:
    header = _receive_exact(connection, HEADER_SIZE)
    body_size = int.from_bytes(header[:3], "little")
    operation = header[3]
    body = _receive_exact(connection, body_size)
    return operation, json.loads(body.decode("utf-8"))


def send_packet(
    connection: socket.socket,
    operation: int,
    payload: Any,
) -> None:
    connection.sendall(encode_packet(operation, payload))
