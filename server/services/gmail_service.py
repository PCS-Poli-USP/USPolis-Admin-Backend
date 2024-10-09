from email.mime.text import MIMEText
import os
import base64
from typing import Any

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

def gmail_login() -> Credentials:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds  # type: ignore


def gmail_send_message(creds: Credentials, content: Any) -> Any:
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(content, "html")

        message["To"] = "uspolis@usp.br"
        message["From"] = (
            service.users().getProfile(userId="me").execute().get("emailAddress")
        )
        message["Subject"] = "Comentário no app USPolis"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message
