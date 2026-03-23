"""Encryption helpers for short-lived payload protection."""
from __future__ import annotations

import json
from typing import Any

from cryptography.fernet import Fernet
from django.conf import settings


def get_fernet() -> Fernet:
    return Fernet(settings.FERNET_SECRET.encode('utf-8'))


def encrypt_payload(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload).encode('utf-8')
    return get_fernet().encrypt(serialized).decode('utf-8')


def decrypt_payload(token: str) -> dict[str, Any]:
    decrypted = get_fernet().decrypt(token.encode('utf-8'))
    return json.loads(decrypted.decode('utf-8'))
