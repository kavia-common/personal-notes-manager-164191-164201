# PUBLIC_INTERFACE
def get_package_info():
    """This package contains the FastAPI app, routers, database setup, models, and schemas for the notes backend."""
    return {
        "name": "src.api",
        "components": ["main", "routers_notes", "db", "models", "schemas"],
    }
