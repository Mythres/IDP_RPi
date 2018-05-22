import bluetooth

def get_socket(mac_address):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((mac_address, 1))
    return sock

def send_data(socket, data):
    socket.send(bytes(len(data)) + b"|" + bytes(data, "utf-8") + b';')

def check_data(data):
    all_complete = True
    commands = data.split(";")

    for command in commands:
        command_split = command.split("|")
        if command_split[0] != len(command_split[1]):
            all_complete = False

    return all_complete

def recv_data(socket):
    data = ""
    commands = []

    while "|" not in data:
        data += socket.recv(1024).decode("utf-8", errors="ignore")

    while check_data(data):
        data += socket.recv(1024).decode("utf-8", errors="ignore")

    for command in data.split(";"):
        command_split = command.split("|")
        commands.append(command_split[1])

    return commands