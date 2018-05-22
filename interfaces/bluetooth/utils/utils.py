import bluetooth

def get_socket(mac_address):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mac_address, 1))
    return sock

def send_data(socket, data):
    socket.send(bytes(len(data)) + b"|" + bytes(data, "utf-8"))

def recv_data(socket):
    data = ""

    while "|" not in data:
        data += socket.recv(1024).decode("utf-8")

    msg_length = int(data[0:data.index("|")])
    data = data[data.index("|") + 1:]

    while len(data) < msg_length:
        data += socket.recv(1024).decode("utf-8")

    return data
