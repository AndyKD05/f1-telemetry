import asyncio
import json
import websockets

LIVE_QUEUE = None
loop = asyncio.get_event_loop()


def enqueue(data):
    global LIVE_QUEUE

    if LIVE_QUEUE is None:
        return False

    loop.call_soon_threadsafe(LIVE_QUEUE.put_nowait, data)

    return True


async def consume_queue(websocket):
    global LIVE_QUEUE

    print("Connected")

    if LIVE_QUEUE is None:
        LIVE_QUEUE = asyncio.Queue()

    try:
        while True:
            try:
                data = await asyncio.wait_for(LIVE_QUEUE.get(), 0.5)
            except asyncio.TimeoutError:
                await websocket.ping()
                continue

            await websocket.send(json.dumps(data))

    except websockets.exceptions.ConnectionClosed:
        print("Disconnected")
        return


async def _serve():
    async with websockets.serve(consume_queue, "localhost", 20775):
        await asyncio.Future()  # run forever


def serve():
    loop.run_until_complete(_serve())
