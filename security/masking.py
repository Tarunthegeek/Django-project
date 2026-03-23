"""Helpers that mask optional sensitive fields before they are echoed back."""
from __future__ import annotations


def mask_value(value: str, keep: int = 2) -> str:
    if not value:
        return ''
    if len(value) <= keep:
        return '*' * len(value)
    return f"{value[:keep]}{'*' * max(1, len(value) - keep)}"


def mask_email(email: str) -> str:
    if not email or '@' not in email:
        return mask_value(email)
    local_part, domain = email.split('@', 1)
    return f"{mask_value(local_part, keep=1)}@{domain}"
