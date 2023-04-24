import socket
def create_server():
    

    s = socket.socket()
    port = 12345
    s.bind(('', port))
    print("socket binded to %s" %(port))
    s.listen(2)
    print("socket listening")
    return s