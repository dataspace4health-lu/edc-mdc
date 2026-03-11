import os
import httpx
from fastapi import UploadFile


class AntivirusService:
    def __init__(self):
        self.api_key = os.getenv("AVSCAN_API_KEY")
        self.api_url = os.getenv("AVSCAN_API_URL")

    async def scan_file(self, file: UploadFile) -> tuple[bool, str]:
        if not self.api_key:
            return True, "Antivirus scanning disabled (no API key configured)"

        url = f"{self.api_url}/av/v1/scans"

        headers = {
            "X-AVSCAN-API-KEY": self.api_key,
        }

        # Read file content
        content = await file.read()
        # Reset file position for later use
        await file.seek(0)

        files = {"file": (file.filename, content, file.content_type)}

        data = {"synchronous": "true"}

        try:
            async with httpx.AsyncClient(timeout=900.0) as client:
                response = await client.post(
                    url, headers=headers, files=files, data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    message = result.get("result", "No message from scanner")

                    if result.get("code") == 200 and status == "clean":
                        return True, message
                    else:
                        return False, message
                elif response.status_code == 401:
                    return False, "Invalid API key"
                elif response.status_code == 429:
                    return False, "Rate limited"
                else:
                    return False, f"Scan failed with status {response.status_code}"

        except Exception as e:
            error_msg = f"Error scanning file: {str(e)}"
            print(error_msg)
            return False, error_msg
