import asyncio
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

OUTPUT_VIDEO_PATH = "received_video.mp4"

async def main():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False  # For self-signed certificates

    async with connect(
        "localhost",
        4433,
        configuration=configuration,
    ) as client:

        # Open a bidirectional stream
        stream_id = client.get_next_available_stream_id()
        reader, writer = client.create_stream(stream_id)

        # Since we're receiving data, we don't need to send anything
        # But we need to wait for the data to arrive

        # Receive the video file
        with open(OUTPUT_VIDEO_PATH, "wb") as f:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                f.write(data)

        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
