from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import hcp_router, interaction_router, auth_router
from app.routers.agent import router as agent_router
from app.routers.dashboard import router as dashboard_router
from app.database import Base, engine
# Import models to register them with Base.metadata
from app.models import HCP, Interaction

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI First CRM HCP Module - Production Ready Backend API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(hcp_router)
app.include_router(interaction_router)
app.include_router(agent_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "AI First CRM HCP Module API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
