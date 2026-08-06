"""
Email Validation Utility
Performs real-world email validation using:
  1. Format check (via pydantic EmailStr - already handled at API layer)
  2. Disposable/throwaway email domain blocklist
  3. DNS MX record lookup - verifies the domain can actually receive email
"""

import asyncio
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Disposable / throwaway email domain blocklist
# Sources: known burner email providers
# ─────────────────────────────────────────────────────────────────────────────
DISPOSABLE_DOMAINS = {
    # Mailinator family
    "mailinator.com", "trashmail.com", "trashmail.net", "trashmail.org",
    "trashmail.at", "trashmail.io", "trashmail.me", "trashmail.xyz",
    # Guerrilla Mail
    "guerrillamail.com", "guerrillamail.net", "guerrillamail.org",
    "guerrillamail.biz", "guerrillamail.de", "guerrillamail.info",
    "grr.la", "spam4.me", "guerrillamailblock.com",
    # Yopmail
    "yopmail.com", "yopmail.fr", "yopmail.net", "cool.fr.nf", "jetable.fr.nf",
    "nospam.ze.tc", "nomail.xl.cx", "mega.zik.dj", "speed.1s.fr", "courriel.fr.nf",
    # 10 Minute Mail
    "10minutemail.com", "10minutemail.net", "10minutemail.org", "10minutemail.de",
    "10minutemail.co.uk", "10minutemail.us", "10minutemail.ru",
    "10minemail.com", "tempail.com", "temp-mail.org", "temp-mail.io",
    # Throwam
    "throwam.com", "throwam.net", "spamgourmet.com", "spamgourmet.net",
    # Fake inbox
    "fakeinbox.com", "fakeinbox.net", "maildrop.cc",
    # Dispostable
    "dispostable.com", "dispostable.net", "discard.email",
    # Sharklasers
    "sharklasers.com", "guerrillamail.info", "grr.la", "guerrillamail.biz",
    "guerrillamail.de", "guerrillamail.net", "guerrillamail.org", "guerrillamail.com",
    "spam4.me", "mailnull.com",
    # Spamfree
    "spamfree24.org", "spamfree.eu", "spamfree24.de",
    # Others
    "mailnesia.com", "mailnull.com", "spamgourmet.com", "spaml.de",
    "odaymail.com", "spamherelots.com", "spamhereplease.com",
    "spamspot.com", "spamthisplease.com", "spamthisplease.com",
    "tempinbox.com", "tempr.email", "tempe-mail.com", "tempmailo.com",
    "crazymailing.com", "dispostable.com", "discard.email",
    "mailscrap.com", "mailscrap.net", "mytempemail.com",
    "boximail.com", "filzmail.com", "mailnull.com",
    "emailondeck.com", "getairmail.com", "getnada.com", "mohmal.com",
    "owlpic.com", "spamgourmet.net", "spamgourmet.org",
    "dropmail.me", "cuvox.de", "dayrep.com", "einrot.com", "fleckens.hu",
    "gustr.com", "hashvk.com", "rhyta.com", "superrito.com", "teleworm.us",
    "armyspy.com", "cuvox.de", "dayrep.com", "einrot.com", "fleckens.hu",
    "jourrapide.com", "rhyta.com", "superrito.com", "teleworm.us",
    "nwldx.com", "spambog.com", "spambog.de", "spambog.ru",
    "spamdecoy.net", "spamfree24.info", "spamfree24.net",
    "spamgourmet.com", "spamhereplease.com", "spamthis.co.uk",
    "trasz.com", "trbvm.com",
}

# Well-known legitimate providers that should always pass (skip DNS for speed)
TRUSTED_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "yahoo.co.in",
    "outlook.com", "hotmail.com", "live.com", "msn.com", "passport.com",
    "icloud.com", "me.com", "mac.com", "apple.com",
    "protonmail.com", "protonmail.ch", "pm.me", "proton.me",
    "zoho.com", "zohomail.com",
    "aol.com", "aim.com",
    "mail.com", "email.com", "usa.com", "myself.com",
    "yandex.com", "yandex.ru",
    "tutanota.com", "tutamail.com", "tuta.io",
    "fastmail.com", "fastmail.fm",
    "hey.com",
    "rediffmail.com",
}


async def check_mx_record(domain: str) -> bool:
    """
    Checks if the email domain has at least one MX (Mail Exchange) record.
    Runs DNS query in a thread pool to avoid blocking the async event loop.
    Returns True if MX records found, False otherwise.
    """
    def _resolve():
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, "MX", lifetime=5)
            return len(answers) > 0
        except Exception as e:
            logger.debug(f"MX lookup failed for {domain}: {e}")
            return False

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _resolve)


async def validate_email_deliverable(email: str) -> Tuple[bool, str]:
    """
    Full email deliverability check.
    Returns (is_valid: bool, error_message: str)

    Checks:
      1. Domain is not a known disposable/throwaway service
      2. Domain has valid MX records (can receive email)
    """
    email = email.strip().lower()

    if "@" not in email:
        return False, "Invalid email format."

    _, domain = email.rsplit("@", 1)
    domain = domain.lower()

    # 1. Disposable email check
    if domain in DISPOSABLE_DOMAINS:
        return False, (
            f"Temporary or disposable email addresses are not allowed. "
            f"Please use a real, active email address."
        )

    # 2. Trusted domains — skip DNS for performance
    if domain in TRUSTED_DOMAINS:
        return True, ""

    # 3. DNS MX record check for unknown domains
    has_mx = await check_mx_record(domain)
    if not has_mx:
        return False, (
            f"The email domain '{domain}' does not appear to be a valid, active mail server. "
            f"Please use a real email address that can receive messages."
        )

    return True, ""
