from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
async def get_test():
    return {"Test": "成功"}
