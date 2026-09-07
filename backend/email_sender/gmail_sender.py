import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any
from datetime import datetime
from backend.config import get_settings
from rich.console import Console

console = Console()
settings = get_settings()


def build_email_html(jobs: List[Dict[str, Any]]) -> str:
    """Build a premium HTML email with job cards."""
    date_str = datetime.now().strftime("%A, %d %B %Y")

    cards_html = ""
    for job in jobs:
        score = job.get("relevance_score", 0) or 0
        sal_min = job.get("salary_min")
        sal_max = job.get("salary_max")
        salary_text = f"&#8377;{sal_min}&#8211;{sal_max} LPA" if sal_min else "Salary not listed"

        score_color = "#22c55e" if score >= 8 else "#f59e0b" if score >= 6 else "#94a3b8"
        type_colors = {"Product": "#6366f1", "Startup": "#ec4899", "MNC": "#0ea5e9", "Service": "#64748b"}
        type_color = type_colors.get(job.get("company_type", ""), "#64748b")

        cards_html += f"""
        <div style="background:#1e293b;border-radius:12px;padding:20px;margin-bottom:16px;
                    border-left:4px solid {score_color};">
          <h3 style="margin:0 0 6px 0;color:#f1f5f9;font-size:16px;">{job.get('title','')}</h3>
          <p style="margin:0 0 8px;color:#94a3b8;font-size:13px;">
            &#127970; {job.get('company','')} &nbsp;&middot;&nbsp;
            &#128205; {job.get('location') or 'India'} &nbsp;&middot;&nbsp;
            &#128188; {job.get('work_mode') or 'Not specified'}
          </p>
          <div style="display:inline-block;background:{score_color};color:#fff;
                      border-radius:20px;padding:2px 10px;font-size:12px;
                      font-weight:700;margin-right:8px;">
            &#11088; {score:.1f}/10
          </div>
          <div style="display:inline-block;background:{type_color};color:#fff;
                      border-radius:20px;padding:2px 10px;font-size:11px;margin-bottom:12px;">
            {job.get('company_type') or 'Company'}
          </div>
          <p style="margin:8px 0 14px;color:#22d3ee;font-size:14px;font-weight:600;">
            &#128176; {salary_text}
          </p>
          <a href="{job.get('url','#')}"
             style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;
                    text-decoration:none;padding:8px 20px;border-radius:8px;
                    font-size:13px;font-weight:600;">
            Apply Now &#8594;
          </a>
        </div>"""

    return f"""<!DOCTYPE html><html><body
      style="margin:0;padding:0;background:#0f172a;font-family:Arial,sans-serif;">
      <div style="max-width:640px;margin:0 auto;padding:24px 16px;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                    border-radius:16px;padding:28px;text-align:center;margin-bottom:20px;">
          <h1 style="margin:0;color:#fff;font-size:26px;">&#127919; JobHunt AI</h1>
          <p style="margin:8px 0 0;color:#c4b5fd;">{date_str}</p>
        </div>
        <div style="background:#1e293b;border-radius:12px;padding:16px;
                    text-align:center;margin-bottom:24px;">
          <span style="color:#6366f1;font-size:22px;font-weight:800;">{len(jobs)}</span>
          <span style="color:#94a3b8;font-size:12px;"> New Jobs &nbsp;|&nbsp; </span>
          <span style="color:#22c55e;font-size:22px;font-weight:800;">
            {len([j for j in jobs if (j.get('relevance_score') or 0) >= 7])}
          </span>
          <span style="color:#94a3b8;font-size:12px;"> High Match &nbsp;|&nbsp; </span>
          <span style="color:#f59e0b;font-size:22px;font-weight:800;">
            {len(set(j.get('company') for j in jobs))}
          </span>
          <span style="color:#94a3b8;font-size:12px;"> Companies</span>
        </div>
        {cards_html}
        <p style="text-align:center;color:#475569;font-size:12px;margin-top:24px;">
          Powered by JobHunt AI &middot; Groq (Llama 3.1 70B) + Playwright
        </p>
      </div></body></html>"""


async def send_job_alert_async(jobs: List[Dict[str, Any]]) -> bool:
    """Send job alert via Gmail SMTP (async)."""
    gmail_user = getattr(settings, 'gmail_user', '')
    gmail_password = getattr(settings, 'gmail_app_password', '')
    to_email = settings.alert_to_email

    if not gmail_user or not gmail_password:
        console.print("[yellow]⚠️  GMAIL_USER or GMAIL_APP_PASSWORD not set[/yellow]")
        return False
    if not to_email:
        console.print("[yellow]⚠️  ALERT_TO_EMAIL not set[/yellow]")
        return False
    if not jobs:
        console.print("[yellow]No jobs to email.[/yellow]")
        return False

    try:
        date_str = datetime.now().strftime("%d %b %Y")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎯 {len(jobs)} New Jobs Found — {date_str}"
        msg["From"] = f"JobHunt AI <{gmail_user}>"
        msg["To"] = to_email

        html = build_email_html(jobs)
        msg.attach(MIMEText(html, "html"))

        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=gmail_user,
            password=gmail_password,
        )
        console.print(f"[green]✅ Email sent to {to_email} ({len(jobs)} jobs)[/green]")
        return True

    except Exception as e:
        console.print(f"[red]Email error: {e}[/red]")
        return False


def send_job_alert(jobs: List[Dict[str, Any]]) -> bool:
    """Sync wrapper for send_job_alert_async."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, send_job_alert_async(jobs))
                return future.result()
        else:
            return loop.run_until_complete(send_job_alert_async(jobs))
    except Exception as e:
        console.print(f"[red]Email send error: {e}[/red]")
        return False
