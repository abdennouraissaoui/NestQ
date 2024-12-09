from typing import Dict, List, Optional
import asyncio
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential
from fastapi import HTTPException

from app.config import Config
from app.templates.email_templates import (
    get_password_reset_template,
    get_welcome_template,
)


class EmailService:
    def __init__(self):
        self.client = EmailClient(
            endpoint=Config.AZURE_COMMUNICATION_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_COMMUNICATION_API_KEY),
        )
        self.sender_address = Config.EMAIL_SENDER_ADDRESS
        print(self.sender_address)
        self.poller_wait_time = 10
        self.max_polling_attempts = 18

    async def _send_email(
        self, recipients: List[str], template: Dict[str, str]
    ) -> bool:
        """
        Internal method to send emails using Azure Communication Services
        """
        message = {
            "senderAddress": self.sender_address,
            "recipients": {
                "to": [{"address": recipient} for recipient in recipients],
            },
            "content": template,
        }

        try:
            poller = self.client.begin_send(message)
            time_elapsed = 0

            while not poller.done():
                await asyncio.sleep(self.poller_wait_time)
                time_elapsed += self.poller_wait_time

                if (
                    time_elapsed
                    > self.max_polling_attempts * self.poller_wait_time
                ):
                    raise HTTPException(
                        status_code=504, detail="Email sending operation timed out"
                    )

            result = poller.result()
            return result["status"] == "Succeeded"

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to send email: {str(e)}"
            )

    async def send_password_reset_email(self, email: str, reset_link: str) -> bool:
        """
        Send password reset email to a user
        """
        template = get_password_reset_template(reset_link)
        return await self._send_email([email], template)

    async def send_welcome_email(self, email: str, first_name: str) -> bool:
        """
        Send welcome email to a new user
        """
        template = get_welcome_template(first_name)
        return await self._send_email([email], template)

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        html_content: Optional[str] = None,
    ) -> bool:
        """
        Send custom bulk email to multiple recipients
        """
        template = {
            "subject": subject,
            "plainText": content,
            "html": html_content or content,
        }
        return await self._send_email(recipients, template)


if __name__ == "__main__":
    email_service = EmailService()
    asyncio.run(
        email_service.send_welcome_email("abdennour@nestq.ai", "Abdennour")
    )
