# MALIN Platform https://malin.cahiersfantastiques.fr/
# Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import email.mime.text
import smtplib

from . import settings


# This is purely integration code. Unit tests for this code would just be a repetition of the code, but using mocks.
# So: THIS CODE IS NOT TESTED AUTOMATICALLY.
def send_mail(to: str, subject: str, body: str) -> None:
    assert settings.OUTBOUND_MAILING is not None
    message = email.mime.text.MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.OUTBOUND_MAILING.MAIL_SENDER
    message["To"] = to

    with smtplib.SMTP_SSL(settings.OUTBOUND_MAILING.SMTP_HOST, settings.OUTBOUND_MAILING.SMTP_PORT) as smtp_server:
        smtp_server.login(settings.OUTBOUND_MAILING.SMTP_USER, settings.OUTBOUND_MAILING.SMTP_PASSWORD)
        smtp_server.sendmail(settings.OUTBOUND_MAILING.MAIL_SENDER, to, message.as_string())
