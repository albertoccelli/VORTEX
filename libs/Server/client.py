import socket

def open_connection(host, port):
    # host = '10.38.103.82' #The host on your client needs to be the external-facing IP address of your router. Obtain it from here https://www.whatismyip.com/
    # port = 42424
    global s
    s = socket.socket()
    s.connect((host,port))
def close_connection():
    s.close()

def send_message(message):
    s.sendall(message.encode("utf-8"))
    data = s.recv(1024)

def Main():
    host = '10.38.103.82' #The host on your client needs to be the external-facing IP address of your router. Obtain it from here https://www.whatismyip.com/
    port = 42424 
    s = socket.socket()
    s.connect((host,port))
    message = input("->") 
    while message != 'q':
        s.sendall(message.encode("utf-8"))
        data = s.recv(1024)
        message = input("->")
    s.close()

if __name__ == '__main__':
    open_connection('10.38.103.82', 42424)
    send_message("CIAO")
    close_connection()
