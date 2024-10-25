from fastapi import FastAPI

app = FastAPI()


@app.post("/upload")
async def upload():
    return {'message': 'success'}
