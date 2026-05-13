"""
Entry point updated to FastAPI. Runs UVicorn serving `fastapi_app.main:app`.
This file replaces the old Flask run helper.
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app.main:app", host="0.0.0.0", port=8000, reload=True)