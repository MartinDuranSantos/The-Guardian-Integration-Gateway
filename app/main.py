from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Secure Inquiry API", 
    description="This API provides secure access to inquiry data and related operations.",
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=[ "http://127.0.0.1:8000",
                   "http://localhost:8000",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


