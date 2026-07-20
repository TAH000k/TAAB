from fastapi import FastAPI

app = FastAPI(
    title="TAAB API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "name": "TAAB API",
        "version": "0.1.0",
        "status": "online"
    }