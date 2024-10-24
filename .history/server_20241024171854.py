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
    



