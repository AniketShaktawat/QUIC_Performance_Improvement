import asyncio
import random

class LossyTransport(asyncio.DatagramTransport):
    def __init__(self, transport, loss_rate=0.2):
        self.transport = transport
        self.loss_rate = loss_rate  # Probability of packet loss

    def sendto(self, data, addr=None):
        if random.random() >= self.loss_rate:
            self.transport.sendto(data, addr)
        else:
            # Drop the packet
            print("Packet dropped")

    def close(self):
        self.transport.close()

    def get_extra_info(self, name, default=None):
        return self.transport.get_extra_info(name, default)

    def is_closing(self):
        return self.transport.is_closing()
    


import asyncio
import os
import random
from aioquic.asyncio import QuicConnectionProtocol, QuicServer
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, QuicEvent

VIDEO_PATH = "sample.mp4"  # Replace with the path to your video file

class VideoServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super(VideoServerProtocol, self).__init__(*args, **kwargs)
        self.file_sent = asyncio.Event()  # Event to signal when the file has been sent

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
        # Set the event to signal that the file has been sent
        self.file_sent.set()

async def main():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("certificate.pem", "private_key.pem")

    loop = asyncio.get_event_loop()

    # Create the UDP socket
    listen = loop.create_datagram_endpoint(
        lambda: QuicServer(
            configuration=configuration,
            create_protocol=VideoServerProtocol,
        ),
        local_addr=('localhost', 4433),
    )

    # Start the server and get the transport and protocol
    transport, protocol = await listen

    # Wrap the transport with LossyTransport to simulate packet loss
    lossy_transport = LossyTransport(transport, loss_rate=0.2)

    # Replace the original transport with the lossy transport
    protocol._transport = lossy_transport

    print("Server is running with 20% packet loss.")

    # Wait for the protocol to signal that the file has been sent
    await protocol._protocols[0].file_sent.wait()

    # Close the server after sending the file
    transport.close()
    await asyncio.sleep(0)
    print("Server has shut down after sending the file.")

if __name__ == "__main__":
    asyncio.run(main())

