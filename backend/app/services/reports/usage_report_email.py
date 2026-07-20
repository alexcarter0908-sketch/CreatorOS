from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config.settings import settings

logger = logging.getLogger("usage_reports")


def _render_html(user_name: str, month_label: str, summary: dict) -> str:
    rows = ""
    for item in summary["breakdown"]:
        rows += (
            f"<tr><td style='padding:6px 12px;border-bottom:1px solid #eee;'>{item['label']}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #eee;text-align:right;'>{item['count']}</td></tr>"
        )

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;color:#222;">
      <h2 style="margin-bottom:4px;">Your CreatorOS Usage Report</h2>
      <p style="color:#666;margin-top:0;">{month_label}</p>
      <p>Hi {user_name or "there"},</p>
      <p>Here is a summary of what happened on your account in {month_label}:</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0;">
        <thead>
          <tr>
            <th style="text-align:left;padding:6px 12px;border-bottom:2px solid #333;">Activity</th>
            <th style="text-align:right;padding:6px 12px;border-bottom:2px solid #333;">Count</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p><strong>Total generations:</strong> {summary["total_generations"]}</p>
      <p><strong>Failed generations:</strong> {summary["failed_generations"]}</p>
      <p><strong>Credits used:</strong> {summary["credits_spent"]}</p>
      <p><strong>Credits purchased:</strong> {summary["credits_purchased"]}</p>
      <p><strong>Current balance:</strong> {summary["current_balance"]} credits</p>
      <p style="color:#888;font-size:12px;margin-top:24px;">
        This is an automated summary from CreatorOS. Credit costs reflect what was
        actually charged at the time of each generation, based on the pricing in
        effect that day.
      </p>
    </div>
    """


def send_monthly_usage_report_email(to_email: str, user_name: str, month_label: str, summary: dict) -> None:
    """
    Reuses the same SMTP settings/pattern as email_service.py (without
    modifying that file), so this is fully independent of the OTP flow
    and cannot break it.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured - skipping usage report email to %s", to_email)
        return

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

    html_body = _render_html(user_name, month_label, summary)
    message = MIMEText(html_body, "html")
    message["Subject"] = f"Your CreatorOS Usage Report - {month_label}"
    message["From"] = from_email
    message["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(from_email, [to_email], message.as_string())