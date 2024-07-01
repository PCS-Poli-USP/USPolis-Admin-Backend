from typing import Annotated

from fastapi import Depends

from server.services.cognito_client import CognitoClient
from server.services.interfaces.i_cognito_client import ICognitoClient

CognitoClientDep = Annotated[ICognitoClient, Depends(CognitoClient)]
