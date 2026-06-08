from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Prompt(BaseModel):
    text: str

@app.post("/chat")
def chat(req: Prompt):
    return {
        "response": f"Tu as dit : {req.text}"
    }
