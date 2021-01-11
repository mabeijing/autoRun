# import asyncio
# import websockets

# async def echo(websocket, path):
#     async for message in websocket:
#         await websocket.send(message)

# start_server = websockets.serve(echo, "192.168.88.60", 8765)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()


import asyncio
import datetime
import random
import websockets


async def time(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        await websocket.send(now)
        await asyncio.sleep(random.random() * 4)


start_server = websockets.serve(time, "192.168.88.60", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
