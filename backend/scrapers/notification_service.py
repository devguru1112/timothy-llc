"""
Email community members when new project leads are scraped.

Recipients: active users who are not Django staff or superusers (typical "admins").
"""
from __future__ import annotations

import logging
import os
from html import escape
from typing import Tuple

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def is_new_project_notifications_enabled() -> bool:
    raw = os.getenv("NOTIFY_NEW_PROJECTS_AFTER_SCRAPE", "1").strip().lower()
    return raw in ("1", "true", "yes", "on")


def get_frontend_projects_url() -> str:
    base = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{base}/dashboard/projects/available"


def community_member_recipients():
    """Users who should receive product notifications (exclude admin/staff)."""
    return User.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
    ).exclude(email="")


def build_new_projects_email(
    *,
    display_name: str,
    projects_added: int,
    platform_name: str,
) -> Tuple[str, str]:
    """
    Build subject + HTML body for the "new projects after scrape" email.
    Copy is intentionally friendly and actionable.
    """
    safe_name = escape(display_name or "there")
    safe_platform = escape(platform_name or "our sources")
    n = max(0, int(projects_added))
    projects_url = get_frontend_projects_url()

    if n == 1:
        subject = f"New project for you — 1 listing from {platform_name or 'a source'}"
        lead = "We just added <strong>1 new project</strong> to the board."
    else:
        subject = f"New projects for you — {n} listings from {platform_name or 'a source'}"
        lead = f"We just added <strong>{n} new projects</strong> to the board."

    # Alternate short tagline (used in preheader-style line)
    tagline = "Fresh opportunities that might match your skills are live."

    body = f"""
    <html>
    <body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; line-height: 1.5; color: #1a1a1a;">
        <p>Hi {safe_name},</p>
        <p>{lead}</p>
        <p style="color: #444;">{escape(tagline)}</p>
        <p style="color: #444;">Source: <strong>{safe_platform}</strong>. Log in and browse what&apos;s available — matching is updated as new leads come in.</p>
        <p style="margin: 24px 0;">
            <a href="{escape(projects_url)}"
               style="display: inline-block; padding: 12px 20px; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600;">
                View available projects
            </a>
        </p>
        <p style="font-size: 13px; color: #666;">
            You&apos;re receiving this because you have an account on our platform and new leads were imported after a scrape.
        </p>
    </body>
    </html>
    """
    return subject.strip(), body.strip()


def send_new_projects_emails(projects_added: int, platform_name: str) -> dict:
    """
    Send notification email to each eligible user. Returns summary counts.
    """
    if not is_new_project_notifications_enabled():
        logger.info("New-project notifications disabled (NOTIFY_NEW_PROJECTS_AFTER_SCRAPE).")
        return {"skipped": True, "reason": "disabled", "sent": 0, "failed": 0}

    if projects_added <= 0:
        return {"skipped": True, "reason": "no_new_projects", "sent": 0, "failed": 0}

    try:
        from outreach.email_service import get_email_service
    except Exception as e:
        logger.error("Could not load email service: %s", e)
        return {"skipped": True, "reason": "email_service_import_error", "sent": 0, "failed": 0}

    email_service = get_email_service()
    recipients = list(community_member_recipients())
    sent = 0
    failed = 0

    for user in recipients:
        display = (user.get_full_name() or "").strip() or (user.first_name or "").strip() or user.username
        subject, html = build_new_projects_email(
            display_name=display,
            projects_added=projects_added,
            platform_name=platform_name or "",
        )
        try:
            result = email_service.send_email(to_email=user.email, subject=subject, body=html)
            if result.get("success"):
                sent += 1
            else:
                failed += 1
                logger.warning(
                    "New-project email failed for %s: %s",
                    user.email,
                    result.get("error"),
                )
        except Exception as e:
            failed += 1
            logger.exception("New-project email error for %s: %s", user.email, e)

    logger.info(
        "New-project scrape notification: platform=%s added=%s emails sent=%s failed=%s recipients=%s",
        platform_name,
        projects_added,
        sent,
        failed,
        len(recipients),
    )
    return {
        "skipped": False,
        "sent": sent,
        "failed": failed,
        "recipients": len(recipients),
        "projects_added": projects_added,
        "platform_name": platform_name,
    }
