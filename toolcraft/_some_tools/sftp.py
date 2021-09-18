from typing import Optional

import asyncio
import json
import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

app = FastAPI()


async def numbers(minimum, maximum):
    for i in range(minimum, maximum + 1):
        await asyncio.sleep(0.9)
        yield json.dumps(dict(fileName="dataset.zip", percentage=i/10))


@app.get('/stream')
async def sse():
    generator = numbers(0, 10)
    return EventSourceResponse(generator)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
