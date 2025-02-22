from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import pandas as pd
import os

app = FastAPI()

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="."), name="static")

# Ensure CSV file exists with proper headers
CSV_FILE = "users_data.csv"
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["user_id", "username"]).to_csv(CSV_FILE, index=False)

class UserCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="Unique identifier for the user")
    username: str = Field(..., min_length=3, max_length=50, description="User's unique name")

@app.post("/user/")
async def create_user(user_data: list[UserCreate]):
    new_users = [{"user_id": user.user_id, "username": user.username} for user in user_data]
    df = pd.DataFrame(new_users)
    df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    return {"msg": "Users created and stored successfully", "users": new_users}

@app.get("/users/")
async def get_users():
    try:
        df = pd.read_csv(CSV_FILE)
        users_list = df.to_dict(orient="records")
        return {"users": users_list}
    except Exception as e:
        return {"error": str(e)}

@app.get("/export_users/")
async def export_users():
    if os.path.exists(CSV_FILE):
        return {"msg": f"Users are stored in '{CSV_FILE}'"}
    return {"msg": "No users found in CSV file"}

# Serving the dashboard (HTML file)
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("dashboard.html") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
