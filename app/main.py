from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .api import router as api_router
from fastapi.staticfiles import StaticFiles
import os, json


# Load API key from .env.json file
with open(os.path.join(os.path.dirname(__file__), '..', '.env.json')) as f:
    config = json.load(f)

os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
os.environ["ENV"] = config["ENV"]
os.environ["MAX_YOUTUBE_LENGTH"] = config["MAX_YOUTUBE_LENGTH"]
os.environ["API_KEY"] = config["API_KEY"]


app = FastAPI()
# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Replace with actual user authentication
    if form_data.username != "testuser" or form_data.password != "testpassword":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, debug=True)
