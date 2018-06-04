from enum import Enum


class MsgTypes(Enum):
    STATUS = 1
    REPLY = 2
    COMMAND = 3
    ERROR = 4


def send_msg(conn, msg_type, msg):
    if "|" in msg:
        msg_split = msg.split("|")
        values = [item.value for item in MsgTypes]

        if int(msg_split[0]) in values:
            conn.send(msg)
            return
    conn.send(str(msg_type.value) + "|" + msg)


def recv_msg(conn, msg_type=None):
    received = ""
    received_split = ["-1", ""]

    if msg_type is None:
        while "|" not in received:
            received = conn.recv()

        received_split = received.split("|")
    else:
        while int(received_split[0]) != msg_type.value:
            received = ""
            while "|" not in received:
                received = conn.recv()

            received_split = received.split("|")

    return received_split[1]
