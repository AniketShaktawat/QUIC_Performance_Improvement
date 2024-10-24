import asyncio
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

OUTPUT_VIDEO_PATH = "path/to/save/received_video.mp4"

async def main():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False  # For self-signed certificates

    async with connect(
        "localhost",
        4433,
        configuration=configuration,
    ) as client:
        # Open a bidirectional stream
        stream_reader, stream_writer = client.create_stream()

        # Send the request to the server
        stream_writer.write(b"REQUEST_VIDEO")
        await stream_writer.drain()
        stream_writer.write_eof()  # Signal end of request

        # Receive the video file
        with open(OUTPUT_VIDEO_PATH, "wb") as f:
            while True:
                data = await stream_reader.read(1024)
                if not data:
                    # EOF reached
                    break
                f.write(data)

        stream_writer.close()
        await stream_writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
