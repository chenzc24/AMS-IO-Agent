#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""User profile helpers without smolagents wrappers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROFILE_DIR = PROJECT_ROOT / "user_data"
PROFILE_DIR.mkdir(exist_ok=True)


def get_profile_path(username: Optional[str] = None) -> Path:
    env_path = os.getenv("USER_PROFILE_PATH", "").strip()
    if env_path and env_path.lower() not in {"", "none", "null"}:
        p = Path(env_path)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p

    default_profile = PROFILE_DIR / "default_user_profile.md"
    if default_profile.exists():
        return default_profile

    if username is None:
        username = os.getenv("USER_PROFILE_NAME", "default_user")
    return PROFILE_DIR / f"{username}_profile.md"


def read_profile(username: Optional[str] = None) -> str:
    profile_path = get_profile_path(username)
    if not profile_path.exists():
        default_profile = PROFILE_DIR / "default_user_profile.md"
        if default_profile.exists() and profile_path != default_profile:
            try:
                import shutil

                shutil.copy(default_profile, profile_path)
            except Exception:
                return ""
        else:
            return ""

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def update_user_profile(new_content: str, username: Optional[str] = None) -> str:
    profile_path = get_profile_path(username)
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"✅ User profile updated: {profile_path}"
    except Exception as e:
        return f"❌ Failed to update profile: {e}"


__all__ = ["get_profile_path", "read_profile", "update_user_profile"]
