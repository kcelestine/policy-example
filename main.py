from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # you probably want some kind of logging here
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )


# it's important to add the catch_exceptions_middleware before(!)
# we add the CORSMiddleware - otherwise (say, if we add the middleware
# through the @app.exception_handler decorator) the CORS headers won't be added
app.middleware('http')(catch_exceptions_middleware)


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
