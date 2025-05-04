from __future__ import annotations

from fastapi import FastAPI

from app.db.sessionmanager import sessionmanager
from app.settings import get_settings

settings = get_settings()


def get_application() -> FastAPI:
    sessionmanager.init(settings.database_url)

    app = FastAPI(
        openapi_url='/api/openapi.json',
        docs_url='/api/docs',
        redoc_url='/api/redoc',
        debug=settings.debug,
        version=settings.app_version or '0.1.0',
        title='Starter FastApi',
    )

    return app


application = get_application()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(application, host='0.0.0.0', port=8000)
