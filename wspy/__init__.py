#!/usr/bin/env python

# WS server example
import json
import asyncio
import websockets
import logging


logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

conexiones = dict()
USERS = set()


async def register(websocket, path):
    ''' Metodo que agrega al usuario a un conjunto general 'USERS'
    y los agrupa por path de conexion.
    :param websocket:
    :param path:
    :return: None
    '''
    # print(dir(websocket))
    if conexiones.get(path) is None:
        conexiones[path] = set()
    conexiones[path].add(websocket)
    USERS.add(websocket)


async def unregister(websocket, path):
    conexiones[path].remove(websocket)
    USERS.remove(websocket)


def users_by_path(path):
    for u in conexiones.get(path):
        if u.closed:
            continue
        yield u


def users_active():
    for u in USERS:
        if u.closed:
            continue
        yield u


async def send_data(jsondata, path):
    json_response = json.dumps(jsondata)
    print("Sending => ",json_response)
    await asyncio.wait([u.send(json_response) for u in users_by_path(path)])


async def main(websocket, path):
    await register(websocket, path)
    while True: # loop para mantener conexión.
        raw_data = await websocket.recv()
        try:
            json_data = json.loads(raw_data)
            await send_data(json_data, path)
            print("Sending")
        except Exception as e:
            print("Discard Conexion e => ", str(e))
            await unregister(websocket, path)



def main_module():
    try:
        start_server = websockets.serve(main, 'localhost', 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except websockets.exceptions.ConnectionClosed:
        logger.warning("Conexion Closed")
    except KeyboardInterrupt:
        logger.warning("Proceso WebSocket terminado")
    except Exception as e:
        logger.warning("Conexion Interrupted {}".format(e,))


if __name__ == "__main__":
    main_module()