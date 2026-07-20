from __future__ import annotations

"""
Placeholder for WhatsApp publishing/notifications.

CreatorOS will connect to WhatsApp (e.g. via the WhatsApp Business
Cloud API) once the core content pipeline is complete. This module
exists now so the platform registry (publish_manager.py) and the
publish_accounts table already treat "whatsapp" as a first-class
platform. Only this file needs a real implementation later - no
other code will need to change.
"""


class WhatsAppNotConnectedError(RuntimeError):
    pass


def build_authorization_url(owner_id: str) -> str:
    raise WhatsAppNotConnectedError(
        "WhatsApp is not connected yet. This will be implemented after "
        "the core content pipeline is complete."
    )


def send_message(*args, **kwargs):
    raise WhatsAppNotConnectedError(
        "WhatsApp is not connected yet. This will be implemented after "
        "the core content pipeline is complete."
    )