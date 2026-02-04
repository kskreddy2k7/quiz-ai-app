from __future__ import annotations

from typing import Callable

from kivy.utils import platform


class PermissionManager:
    def request_permissions(self, on_status: Callable[[str], None]) -> None:
        if platform != "android":
            on_status("Permissions not required on this device.")
            return

        try:
            from android.permissions import Permission, request_permissions
        except Exception:
            on_status("Permissions unavailable.")
            return

        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
        ]

        def callback(_, grants):
            if all(grants):
                on_status("Permissions granted.")
            else:
                on_status("Some permissions denied.")

        request_permissions(permissions, callback)
