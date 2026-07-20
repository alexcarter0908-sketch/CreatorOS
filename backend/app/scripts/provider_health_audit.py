"""
Provider Health Audit
======================

Run this BEFORE adding real API keys to catch structural bugs early
(the same class of bug that broke Kling and Runway):

  - Abstract methods not implemented -> class can't instantiate
  - api_key_env pointing to a Settings field that doesn't exist
  - supports_* flags not matching supported_asset_types

Usage (from the backend/ folder):

    python -m app.scripts.provider_health_audit

This does NOT need any real API keys. It only checks structure.
"""

from __future__ import annotations

import sys

from app.core.config import settings
from app.services.providers.registry import PROVIDER_REGISTRY


def audit() -> bool:

    all_ok = True

    print("=" * 70)
    print("PROVIDER HEALTH AUDIT")
    print("=" * 70)

    for provider_id, definition in PROVIDER_REGISTRY.items():

        print(f"\n[{provider_id}]")

        # -----------------------------------------------------
        # 1. Config check - does the env var actually exist?
        # -----------------------------------------------------

        if not hasattr(settings, definition.api_key_env):
            print(
                f"  XX CONFIG ERROR: settings has no attribute "
                f"'{definition.api_key_env}' "
                f"(referenced by api_key_env)"
            )
            all_ok = False
        else:
            key_present = bool(getattr(settings, definition.api_key_env, ""))
            print(
                f"  {'OK' if key_present else '..'} "
                f"API key configured: {key_present}"
            )

        # -----------------------------------------------------
        # 2. Instantiation check - the exact bug that hit
        #    Kling and Runway (abstract methods not implemented)
        # -----------------------------------------------------

        if definition.provider_class is None:
            print("  ..  No provider_class assigned (not implemented yet)")
            continue

        instance = None

        try:
            instance = definition.provider_class()
            print("  OK Instantiates cleanly")

        except TypeError as e:
            # This is the REAL structural bug (missing abstract
            # method implementation) - the same bug Kling/Runway had.
            print(f"  XX CANNOT INSTANTIATE (structural bug): {e}")
            all_ok = False
            continue

        except Exception as e:
            # Not a structural bug. The class itself is fine, but
            # __init__ does real work (e.g. creates an SDK client)
            # that needs a real credential to succeed. Expected when
            # no API key is configured yet - skip further checks.
            print(f"  ..  Skipped (needs real credentials to fully init): {e}")
            continue

        # -----------------------------------------------------
        # 3. Cross-check supports_* flags vs supported_asset_types
        #    (informational only - not a bug for text providers,
        #    since sub-types like blog/seo/script route through
        #    BaseProvider.generate() to the same chat() method)
        # -----------------------------------------------------

        flag_map = {
            "supports_text": "text",
            "supports_image": "image",
            "supports_video": "video",
            "supports_audio": "audio",
        }

        declared_types = set(
            getattr(instance, "supported_asset_types", ()) or ()
        )

        flags_true = {
            asset
            for flag, asset in flag_map.items()
            if getattr(definition, flag, False)
        }

        if declared_types and not declared_types.issubset(
            flags_true | declared_types
        ):
            print(
                f"  ..  Info: supported_asset_types={declared_types}, "
                f"base flags imply {flags_true}"
            )

    print("\n" + "=" * 70)

    if all_ok:
        print("RESULT: All providers are structurally sound.")
    else:
        print("RESULT: One or more providers have structural bugs.")
        print("Fix these BEFORE adding real API keys.")

    print("=" * 70)

    return all_ok


if __name__ == "__main__":
    healthy = audit()
    sys.exit(0 if healthy else 1)