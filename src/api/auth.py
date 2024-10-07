from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
import os
import dotenv

dotenv.load_dotenv()

api_keys: list[str] = []
api_key = os.environ.get("API_KEY")

if api_key is None:
    raise RuntimeError("No API KEY provided")

api_keys.append(api_key)
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(request: Request, api_key_header: str = Security(api_key_header)):
    if api_key_header in api_keys:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden"
        )
