import hashlib
import struct

HEADER_DIFFERENCE_DATA_OFFSET = 36
FOOTER_DATA_OFFSET = 795

MESSAGE_ID_INITIAL = 1
MESSAGE_ID_VIDEO_EXISTENCE = 2
MESSAGE_ID_BASE_VIDEO = 3
MESSAGE_ID_FINAL = 4
MESSAGE_ID_DIFFERENCE = 5

MESSAGE_HEADER_SIZE = 6
TIME_STAMP_SIZE = 13
HEADER_DIFFERENCE_DATA_SIZE = 4
SOCKET_BUFFER_SIZE = 1024

def make_initial_confirmation_message(device_id, base_video_data):
    # Make MD5 hash
    hash_binary = hashlib.md5(base_video_data).digest()

    data_size = len(hash_binary)
    message_header = struct.pack("!BBI", device_id, MESSAGE_ID_INITIAL, data_size)
    message_body = struct.pack("!{}s".format(data_size), hash_binary)

    return message_header, message_body, data_size


def make_base_video_existence_message(device_id, video_existence_flag):
    data_size = 1
    message_header = struct.pack("!BBI", device_id, MESSAGE_ID_VIDEO_EXISTENCE, data_size)
    message_body = struct.pack("!B", video_existence_flag)

    return message_header, message_body, data_size


def make_base_video_message(device_id, base_video_data):
    data_size = len(base_video_data)
    message_header = struct.pack("!BBI", device_id, MESSAGE_ID_BASE_VIDEO, data_size)
    message_body = struct.pack("!{}s".format(data_size), base_video_data)

    return message_header, message_body, data_size


def make_final_message(device_id, success_flag):
    data_size = 1
    message_header = struct.pack("!BBI", device_id, MESSAGE_ID_FINAL, data_size)
    message_body = struct.pack("!B", success_flag)

    return message_header, message_body, data_size


def make_image_difference_message(device_id, time_stamp_str, header_difference_data, additional_frame_data):
    frame_size = len(additional_frame_data)
    data_size = TIME_STAMP_SIZE + HEADER_DIFFERENCE_DATA_SIZE + frame_size
    message_header = struct.pack("!BBI", device_id, MESSAGE_ID_DIFFERENCE, data_size)
    message_body = struct.pack("!{}s{}s{}s".format(TIME_STAMP_SIZE, HEADER_DIFFERENCE_DATA_SIZE, frame_size), time_stamp_str.encode("utf-8"), header_difference_data, additional_frame_data)

    return message_header, message_body, frame_size

def parse_message_header(message_header):
    device_id, message_id, data_size = struct.unpack("!BBI", message_header)

    return device_id, message_id, data_size

def parse_message_body(message_id, data_size, message_body):
    data_1 = None
    data_2 = None
    data_3 = None

    if message_id == MESSAGE_ID_INITIAL:
        data_1 = struct.unpack("!{}s".format(data_size), message_body)[0]
    elif message_id == MESSAGE_ID_VIDEO_EXISTENCE:
        data_1 = struct.unpack("B".format(data_size), message_body)[0]
    elif message_id == MESSAGE_ID_BASE_VIDEO:
        data_1 = struct.unpack("!{}s".format(data_size), message_body)[0]
    elif message_id == MESSAGE_ID_FINAL:
        data_1 = struct.unpack("B".format(data_size), message_body)[0]
    elif message_id == MESSAGE_ID_DIFFERENCE:
        data_1, data_2, data_3 = struct.unpack("!{}s{}s{}s".format(TIME_STAMP_SIZE, HEADER_DIFFERENCE_DATA_SIZE, data_size - (TIME_STAMP_SIZE + HEADER_DIFFERENCE_DATA_SIZE)), message_body)
        data_1 = data_1.decode("utf-8", "replace")
    else:
        print("Warning: Unknown message")

    return data_1, data_2, data_3


def packet_receiver(socket, target_size):
    data = None

    receive_size = target_size

    while True:
        tmp = socket.recv(receive_size)
        receive_size -= len(tmp)
        if data is None:
            data = tmp
        else:
            data = data + tmp

        if receive_size <= 0:
            break

    return data


def message_receiver(socket, target_device_id=None):
    message_header = packet_receiver(socket, MESSAGE_HEADER_SIZE)
    device_id, message_id, data_size = parse_message_header(message_header)
    message_body = packet_receiver(socket, data_size)

    data_1 = None
    data_2 = None
    data_3 = None

    if (target_device_id is not None) and (device_id != target_device_id):
        print("Warning: Device ID ({}) and target device ID ({}) is different".format(device_id, target_device_id))
        return None, None, None, None, None, None

    data_1, data_2, data_3 = parse_message_body(message_id, data_size, message_body)

    return device_id, message_id, data_size, data_1, data_2, data_3