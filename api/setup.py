import uvicorn

from fastapi import FastAPI

from api.router import router


app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run('setup:app', host='127.0.0.1', port=7000, log_level='info', reload=True)


