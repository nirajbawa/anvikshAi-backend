import httpx
from typing import Optional, Dict
from fastapi import HTTPException
import os

class HTTPEmailService:
    def __init__(self):
        self.base_url = "http://65.2.30.191"  # Your EC2 instance
        self.timeout = 30.0  # seconds
        self.api_key = os.getenv("EMAIL_SERVICE_API_KEY", "your-api-key-here")  # Set this in your environment variables

    async def send_email(
        self, 
        recipient: str, 
        subject: str, 
        html_content: str
    ) -> dict:
        """
        Send email via HTTP request to EC2 instance with API key authentication
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "recipient": recipient,
                    "subject": subject,
                    "html_content": html_content
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key  # Add API key to headers
                }
                
                response = await client.post(
                    f"{self.base_url}/send-email",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Email service timeout. Please try again."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key for email service"
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Email service error: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(e)}"
            )

# Create singleton instance
http_email_service = HTTPEmailService()