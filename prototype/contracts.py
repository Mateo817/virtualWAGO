"""Validation helpers for our standalone model protocol, not a vendor ABI."""
from __future__ import annotations

import json
import re
from typing import Any


class ContractError(ValueError):
    """Invalid request; no partial application is permitted."""


class Unsupported(ContractError):
    """Required semantics have not been implemented or verified."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def uint(value: Any, name: str, maximum: int = 2**63 - 1) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ContractError(f"{name}: expected integer in [0, {maximum}]")
    return value


def exact_keys(value: Any, required: set[str], name: str) -> None:
    if type(value) is not dict or set(value) != required:
        raise ContractError(f"{name}: expected keys {sorted(required)}")


def hexbytes(value: Any, length: int, name: str) -> bytes:
    if (type(value) is not str or len(value) != 2 * length or
            re.fullmatch(r"[0-9a-fA-F]*", value) is None):
        raise ContractError(f"{name}: expected exactly {length} bytes as hex")
    return bytes.fromhex(value)
