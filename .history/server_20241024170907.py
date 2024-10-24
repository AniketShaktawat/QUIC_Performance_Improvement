import asyncio
import os
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

VIDEO_PATH = "sample.mp4"

async def handle_stream(stream_id, stream_reader, stream_writer):
    # Read the request from the client
    request = b''
    while True:
        data = await stream_reader.read(1024)
        if not data:
            # EOF reached
            break
        request += data

    if request == b"REQUEST_VIDEO":
        # Send the video file
        if os.path.exists(VIDEO_PATH):
            with open(VIDEO_PATH, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    stream_writer.write(chunk)
                    await stream_writer.drain()
    else:
        # Handle invalid request
        stream_writer.write(b"Invalid request")
        await stream_writer.drain()

    stream_writer.close()
    await stream_writer.wait_closed()

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
