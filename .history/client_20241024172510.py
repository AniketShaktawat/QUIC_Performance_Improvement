import asyncio
from aioquic.asyncio import connect, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived

OUTPUT_VIDEO_PATH = "received_video.mp4"  # Replace with your desired output path

class VideoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super(VideoClientProtocol, self).__init__(*args, **kwargs)
        self.output_file = None
        self.video_stream_id = None

    def quic_event_received(self, event: QuicEvent):
        if isinstance(event, StreamDataReceived):
            if self.video_stream_id is None:
                # First data received, open the output file
                self.video_stream_id = event.stream_id
                self.output_file = open(OUTPUT_VIDEO_PATH, "wb")

            if event.stream_id == self.video_stream_id:
                # Write data to the file
                self.output_file.write(event.data)
                if event.end_stream:
                    # Close the file and the connection
                    self.output_file.close()
                    self._quic.close()

    async def send_request(self):
        # Send the request to the server
        stream_id = self._quic.get_next_available_stream_id()
        self._quic.send_stream_data(stream_id, b"REQUEST_VIDEO", end_stream=True)

async def main():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False  # For self-signed certificates

    async with connect(
        "localhost",
        4433,
        configuration=configuration,
        create_protocol=lambda **kwargs: VideoClientProtocol(quic_configuration=configuration, **kwargs),
    ) as client:
        await client.send_request()
        # Wait until the connection is closed
        await client.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
