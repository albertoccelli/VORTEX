import can
from time import sleep

BITRATE = 125000


def detectPort():
    for i in range(30):
        try:
            port = i
            bus = can.interface.Bus(bustype="vector", channel = port, bitrate = BITRATE)
            print("Port found: %s\n"%(port))
            break
        except can.interfaces.vector.exceptions.VectorError:
            print("Error: device not connected\n")
            return "Error"
        except Exception as e:
            print("Port %s not found, error %s\n"%(port, e))
            return "Error"
    return port

def detectCommand(port):
    can_ear = can.Listener()
    bus = can.interface.Bus(bustype="vector", channel = port, bitrate = BITRATE)
    msg = bus.recv()
    can_ear.on_message_received(msg)
    can_ear.stop()


def activateMic(port):
    bus = can.interface.Bus(bustype="vector", channel = port, bitrate = BITRATE)
    if port != "Error":
        msg = can.Message(arbitration_id=0x2ee, extended_id=False, channel=port, dlc=4, data=[0x00, 0x04, 0x00, 0x00])     #voice button push
        msg2 = can.Message(arbitration_id=0x2ee, extended_id=False, channel=port, dlc=4, data=[0x00, 0x00, 0x00, 0x00])    #voice button release
        bus.send(msg)
        print("MICRO")
        sleep(0.1)
        bus.send(msg2)
        print("PHONE")
        return 0
    else:
        print("Invalid port. Make sure your device is properly connected")
        return 1


if __name__ == "__main__":
    port = detectPort()
    activateMic(port)
    
