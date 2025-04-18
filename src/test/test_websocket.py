import asyncio
from argparse import SUPPRESS, ArgumentParser

import websockets


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group("Options")

    args.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="Show this help message and exit.",
    )

    args.add_argument(
        "-ip",
        "--ip",
        default="127.0.0.1",
        type=str,
        help="The ip of the WebSocket server. Default: 127.0.0.1",
    )

    args.add_argument(
        "-p",
        "--port",
        default=5000,
        type=int,
        help="The port of the WebSocket server. Default: 5000",
    )

    args.add_argument(
        "-uuid",
        "--uuid",
        required=True,
        type=str,
        help="The uuid of the task that use to connect WebSocket server.",
    )
    args.add_argument(
        "-n",
        "--n_user",
        default=1,
        type=int,
        help="The virtual number of user to connect WebSocket server. Default: ",
    )

    return parser


async def websocket_client(url, client_id):
    try:
        async with websockets.connect(url) as websocket:
            print(f"Client {client_id} connected to {url}")

            await websocket.send(f"Hello from client {client_id}")
            print(f"Client {client_id} sent: Hello from client {client_id}")

            while True:
                response = await websocket.recv()
                print(f"Client {client_id} received: {response}")

    except Exception as e:
        print(f"Client {client_id} error: {e}")


async def main(uuid: str, n_user: int = 1, ip: str = "127.0.0.1", port: str = 5000):
    url = f"ws://{ip}:{port}/ws/{uuid}"
    num_clients = n_user

    tasks = [
        websocket_client(url, client_id) for client_id in range(1, num_clients + 1)
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = build_argparser().parse_args()
    ip = args.ip
    port = args.port
    uuid = args.uuid
    n_user = args.n_user
    print(
        f"""The parameter you set is like below:\n \
    * ip : {ip} \n \
    * port : {port} \n \
    * uuid : {uuid} \n \
    * n_user : {n_user} \n \n \n """
    )
    asyncio.run(main(uuid=uuid, ip=ip, port=port, n_user=n_user))
