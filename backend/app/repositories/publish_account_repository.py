from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import PublishAccount


class PublishAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_owner_and_platform(
        self,
        owner_id: str,
        platform: str,
    ) -> PublishAccount | None:
        return (
            self.db.query(PublishAccount)
            .filter(
                PublishAccount.owner_id == owner_id,
                PublishAccount.platform == platform,
                PublishAccount.is_active.is_(True),
            )
            .first()
        )

    def upsert(
        self,
        *,
        owner_id: str,
        platform: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None,
        account_label: str | None = None,
        external_account_id: str | None = None,
        scopes: str | None = None,
        extra_metadata: dict | None = None,
    ) -> PublishAccount:
        account = self.get_by_owner_and_platform(owner_id, platform)

        if account is None:
            account = PublishAccount(
                owner_id=owner_id,
                platform=platform,
            )

        if access_token is not None:
            account.access_token = access_token
        if refresh_token is not None:
            account.refresh_token = refresh_token
        if token_expiry is not None:
            account.token_expiry = token_expiry
        if account_label is not None:
            account.account_label = account_label
        if external_account_id is not None:
            account.external_account_id = external_account_id
        if scopes is not None:
            account.scopes = scopes
        if extra_metadata is not None:
            account.extra_metadata = extra_metadata

        account.is_active = True

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def get_by_id(self, account_id: str) -> PublishAccount | None:
        return (
            self.db.query(PublishAccount)
            .filter(PublishAccount.id == account_id, PublishAccount.is_active.is_(True))
            .first()
        )

    def deactivate(self, account: PublishAccount) -> None:
        account.is_active = False
        self.db.add(account)
        self.db.commit()

    # ------------------------------------------------------------------
    # Multi-account support (additive only -- upsert()/get_by_owner_and_platform()
    # above are untouched and keep behaving exactly as before for any
    # existing single-account caller).
    # ------------------------------------------------------------------
    def list_by_owner_and_platform(
        self,
        owner_id: str,
        platform: str,
    ) -> list[PublishAccount]:
        """Returns every connected account for this platform (e.g. all
        YouTube channels, all Instagram accounts), not just the first."""
        return (
            self.db.query(PublishAccount)
            .filter(
                PublishAccount.owner_id == owner_id,
                PublishAccount.platform == platform,
                PublishAccount.is_active.is_(True),
            )
            .order_by(PublishAccount.created_at.asc())
            .all()
        )

    def get_by_owner_platform_and_external_id(
        self,
        owner_id: str,
        platform: str,
        external_account_id: str,
    ) -> PublishAccount | None:
        return (
            self.db.query(PublishAccount)
            .filter(
                PublishAccount.owner_id == owner_id,
                PublishAccount.platform == platform,
                PublishAccount.external_account_id == external_account_id,
                PublishAccount.is_active.is_(True),
            )
            .first()
        )

    def upsert_by_external_id(
        self,
        *,
        owner_id: str,
        platform: str,
        external_account_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None,
        account_label: str | None = None,
        scopes: str | None = None,
        extra_metadata: dict | None = None,
    ) -> PublishAccount:
        """Like upsert(), but keys off (owner, platform, external_account_id)
        instead of just (owner, platform) -- so connecting a second channel
        on the same platform creates a new row instead of overwriting the
        first one."""
        account = self.get_by_owner_platform_and_external_id(
            owner_id, platform, external_account_id
        )
        if account is None:
            account = PublishAccount(
                owner_id=owner_id,
                platform=platform,
                external_account_id=external_account_id,
            )
        if access_token is not None:
            account.access_token = access_token
        if refresh_token is not None:
            account.refresh_token = refresh_token
        if token_expiry is not None:
            account.token_expiry = token_expiry
        if account_label is not None:
            account.account_label = account_label
        if scopes is not None:
            account.scopes = scopes
        if extra_metadata is not None:
            account.extra_metadata = extra_metadata
        account.is_active = True
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

