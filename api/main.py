import asyncio
import uvicorn

from api import app as api_app
from scheduler import app as scheduler_app


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        scheduler_app.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    "Run scheduler and the API"
    server = Server(config=uvicorn.Config(api_app, workers=1, loop="asyncio"))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(scheduler_app.serve())

    await asyncio.wait([sched, api])


if __name__ == "__main__":
    asyncio.run(main())
