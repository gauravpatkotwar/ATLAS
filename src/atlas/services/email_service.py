import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from atlas.config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """Sends an HTML email via Gmail SMTP using app password."""
        if not settings.EMAILS_ENABLED or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP Email sending skipped: Credentials not fully configured.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"ATLAS Work Intelligence <{settings.SMTP_USER}>"
            msg["To"] = to_email

            part = MIMEText(html_content, "html")
            msg.attach(part)

            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
            
            logger.info(f"✅ Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    def send_interview_invitation(to_email: str, candidate_name: str, job_title: str, interview_link: str) -> bool:
        """Sends candidate interview invitation email."""
        subject = f"Invitation: AI Voice Interview for {job_title} at ATLAS"
        html_content = f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #0f172a; color: #f8fafc; border-radius: 12px;">
            <h1 style="color: #6366f1; font-size: 24px; margin-bottom: 16px;">⚡ ATLAS Work Intelligence</h1>
            <p style="font-size: 16px; line-height: 1.5;">Hi <strong>{candidate_name}</strong>,</p>
            <p style="font-size: 16px; line-height: 1.5;">You have been invited to participate in an AI Voice Mock Interview for the position of <strong>{job_title}</strong>.</p>
            <div style="margin: 32px 0; text-align: center;">
                <a href="{interview_link}" style="background: linear-gradient(135deg, #6366f1, #a855f7); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; display: inline-block;">Start Voice Interview</a>
            </div>
            <p style="font-size: 14px; color: #94a3b8;">This link will remain active for your evaluation session.</p>
        </div>
        """
        return EmailService.send_email(to_email, subject, html_content)
