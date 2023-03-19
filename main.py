from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router

app = FastAPI(
    title="Quizless",
    servers=[
        {
            "url": "http://localhost:{port}",
            "description": "local",
            "variables": {"port": {"default": 8055}},
        }
    ]
)

app.include_router(api_router, prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    # Setup for local debug
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8055, reload=True)
