# routes/__init__.py
from fastapi import APIRouter
from controllers import reports   # Import your routers

# Create a central router
router = APIRouter()

# Include the routers from controllers
router.include_router(reports.router, prefix="/reports")
# Add more include_router statements for other controllers

# Additional common routes or middleware can be added directly to this router if needed
# For example: router.add_api_route("/", some_function)

# Export the central router
__all__ = ["router"]
