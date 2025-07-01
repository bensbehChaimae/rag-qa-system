from fastapi import FastAPI 

app = FastAPI()

@app.get("/welcome")
def welcome():
    return {
        "message" : "welcome to fastapi"
    }


