import asyncio
import os
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, QuicEvent

VIDEO_PATH = "sample.mp4"  # Replace with the path to your video file

class VideoServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event: QuicEvent):
        if isinstance(event, StreamDataReceived):
            data = event.data
            stream_id = event.stream_id
            if data == b"REQUEST_VIDEO" and event.end_stream:
                # Send the video file
                asyncio.ensure_future(self.send_video(stream_id))
            else:
                # Handle invalid request or partial data
                pass

    async def send_video(self, stream_id):
        if os.path.exists(VIDEO_PATH):
            with open(VIDEO_PATH, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self._quic.send_stream_data(stream_id, chunk)
                    await asyncio.sleep(0)  # Yield control to event loop
            # Signal the end of the stream
            self._quic.send_stream_data(stream_id, b'', end_stream=True)
        else:
            # Video file not found
            self._quic.send_stream_data(stream_id, b"Video file not found", end_stream=True)

async def main():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("certificate.pem", "private_key.pem")

    await serve(
        "localhost",
        4433,
        configuration=configuration,
        create_protocol=VideoServerProtocol,
    )

    # Keep the server running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
