import socket
from socket import timeout


def open_connection(port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print('HOST IP:',host_ip)
    socket_address = (host_ip, port)
    # socket bind
    server_socket.bind(socket_address)
    #socket listen
    server_socket.listen(10)
    print("LISTENING AT:",socket_address)
    '''
    #accept
    while True:
        global client_socket, addr
        client_socket, addr = server_socket.accept()
        print("GOT CONNECTION FROM:",addr)
        if client_socket:
            client_socket.sendall(("Welcome").encode("utf-8"))
            break
    '''
    return host_ip, port
    

def send_message(message):
    global client_socket, addr
    try:
        client_socket.sendall((message.replace("\n","")+"\n").encode("utf-8"))
    except NameError:
        server_socket.settimeout(0.1)
        try:
            print("No client connected, waiting for connection...")
            client_socket, addr = server_socket.accept()
            print("GOT CONNECTION FROM:",addr)
            if client_socket:
                client_socket.sendall(("Welcome").encode("utf-8"))
                client_socket.sendall(message.encode("utf-8"))
        except timeout:
            print("Timeout! Proceeding offline")
            pass
            
    except ConnectionAbortedError:
        server_socket.settimeout(0.1)
        try:
            print("Client not connected")
            client_socket, addr = server_socket.accept()
            print("GOT CONNECTION FROM:",addr)
            client_socket.sendall(message.encode("utf-8"))
        except timeout:
            pass
            
            

def Main():
    server_socket.listen(1)
    c, addr = server_socket.accept()
    while True:
        data = c.recv(1024)
        if not data:
            break
        print(str(data))
        data = str(data).upper()
        c.sendall(data.encode('utf-8'))
    c.close()
    
if __name__ == '__main__':
    import time

    open_connection(42886)
    while True:
        send_message("prova")
        print("Prova")
        time.sleep(1)
