import asyncio
import os
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

VIDEO_PATH = "sample.mp4"

async def handle_stream(stream_id, reader, writer):
    # Send the video file
    if os.path.exists(VIDEO_PATH):
        with open(VIDEO_PATH, "rb") as f:
            data = f.read()
            writer.write(data)
            await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("certificate.pem", "path/to/your/private_key.pem")

    await serve(
        "localhost",
        4433,
        configuration=configuration,
        stream_handler=handle_stream,
    )

if __name__ == "__main__":
    asyncio.run(main())
