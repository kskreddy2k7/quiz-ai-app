from __future__ import annotations

import importlib.util
from typing import Callable, List

from kivy.utils import platform


class PermissionManager:
    def __init__(self) -> None:
        self._android_permissions = self._load_android_permissions()

    def _load_android_permissions(self):
        if platform != "android":
            return None
        if not importlib.util.find_spec("android"):
            return None
        from android.permissions import Permission, request_permissions

        return Permission, request_permissions

    def request_permissions(self, update_status: Callable[[str], None]) -> None:
        if platform != "android" or not self._android_permissions:
            update_status("Permissions ready.")
            return
        Permission, request_permissions = self._android_permissions
        permissions: List[str] = [Permission.INTERNET]

        def callback(_permissions, _grants):
            update_status("Permissions updated.")

        update_status("Requesting Android permissions...")
        request_permissions(permissions, callback)
