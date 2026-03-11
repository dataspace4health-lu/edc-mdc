from fastapi.responses import JSONResponse


class ErrorResponse:
    @staticmethod
    def create(
        status_code: int, detail: str, title: str = "An error occurred"
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "title": title,
                "status": status_code,
                "detail": detail,
            },
        )
