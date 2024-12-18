from dotenv import load_dotenv
load_dotenv()

from routes.routes import router as main_router  # Import the central router
from config.db.database import connect_to_db, disconnect_from_db
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
import os


# main.py

ROOT_PATH = os.environ.get("ROOT_PATH", "/")

app = FastAPI(title="APIs for GSTIN9R", description="APIs for GSTIN9R",
              root_path=f"{ROOT_PATH}", openapi_url='/openapi.json', docs_url=None, redoc_url=None)

origins = [
    "*"
]

app.add_middleware(CORSMiddleware, allow_origins=origins,  
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="APIs for Reports"
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database at startup
    connect_to_db()
    try:
        # Yield control back to FastAPI for the lifespan of the application
        yield
    finally:
        # Ensure the database is disconnected when the application shuts down
        disconnect_from_db()

# Set the lifespan context of the FastAPI app
app.router.lifespan_context = lifespan

# Include the central router in the app
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
