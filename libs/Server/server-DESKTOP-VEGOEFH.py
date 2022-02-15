import socket
import cv2
import pickle, struct

def Main():
    s = socket.socket()
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print("HOST IP: %s" % host_ip)
    port = 42886
    socket_address = (host_ip, port)

    s.bind(socket_address)

    s.listen(5)
    print("LISTENING AT:", socket_address)

    while True:
        c, addr = s.accept()
        print("GOT CONNECTION FROM:", addr)
        if s:
            vid = cv2.VideoCapture(1)
            while(vid.isOpened()):
                img, frame = vid.read()
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a))+a
                c.sendall(message)
                cv2.imshow("TRANSMITTING VIDEO", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    c.close()



if __name__ == '__main__':
    Main()
