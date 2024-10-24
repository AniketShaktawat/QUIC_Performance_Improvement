import asyncio
from aioquic.asyncio import connect, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration

OUTPUT_VIDEO_PATH = "received_video.mp4"

class VideoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super(VideoClientProtocol, self).__init__(*args, **kwargs)
        self.output_file = open(OUTPUT_VIDEO_PATH, "wb")

    async def send_request(self):
        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=False)
        stream_reader, stream_writer = await self._create_stream(stream_id)

        # Send the request to the server
        stream_writer.write(b"REQUEST_VIDEO")
        await stream_writer.drain()
        stream_writer.write_eof()

        # Receive the video file
        while True:
            data = await stream_reader.read(1024)
            if not data:
                break
            self.output_file.write(data)

        self.output_file.close()
        stream_writer.close()
        await stream_writer.wait_closed()
        self._quic.close()

async def main():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False  # For self-signed certificates

    async with connect(
        "localhost",
        4433,
        configuration=configuration,
        create_protocol=VideoClientProtocol,
    ) as client:
        await client.send_request()

if __name__ == "__main__":
    asyncio.run(main())
