import time
import os
import packet_manager
import video_file_manager
import socket
import sys


def cilent(server_ip_address, server_port, device_id, client_base_image_path, client_target_image_path,
           client_base_video_dir="./client_base/", fourcc="mp4v", video_ext=".mp4"):
    start_time = time.time()
    payload_size_all = 0

    if not os.path.exists(client_base_video_dir):
        os.mkdir(client_base_video_dir)

    client_base_video_path \
        = client_base_video_dir + "base_" + os.path.splitext(os.path.basename(client_base_image_path))[0] + video_ext
    client_target_video_path = client_base_video_dir + "target" + video_ext
    client_time_stamp_str = os.path.splitext(os.path.basename(client_target_image_path))[0]

    # Create base video file
    if not os.path.exists(client_base_video_path):
        print("Info: Create a base video file")
        ret = video_file_manager.compression(fourcc, [client_base_image_path], client_base_video_path)
        if ret is None:
            print("Error: Failed to create a base video file")
            return 2, None
    else:
        # print("Info: Found a base video file")
        pass

    # Create target video file
    if os.path.exists(client_target_video_path):
        os.remove(client_target_video_path)
    ret = video_file_manager.compression(fourcc,
                                         [client_base_image_path, client_target_image_path],
                                         client_target_video_path)
    if ret is None:
        print("Error: Failed to create a target video file")
        return 3, None

    # Open target video file
    client_target_video_file = open(client_target_video_path, "rb")
    client_target_video_data = client_target_video_file.read()

    # Make difference data
    client_additional_frame_data_offset = os.path.getsize(client_base_video_path) - packet_manager.FOOTER_DATA_OFFSET
    client_header_difference_data = client_target_video_data[packet_manager.HEADER_DIFFERENCE_DATA_OFFSET: packet_manager.HEADER_DIFFERENCE_DATA_OFFSET + 4]
    client_additional_frame_data = client_target_video_data[client_additional_frame_data_offset:]

    # make socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((server_ip_address, server_port))

    # Make initial confirmation message
    client_base_video_file = open(client_base_video_path, "rb")
    client_base_video_data = client_base_video_file.read()
    client_base_video_file.close()
    icm_header, icm_body, icm_payload_size = packet_manager.make_initial_confirmation_message(device_id, client_base_video_data)


    # Send initial confirmation message
    my_socket.send(icm_header)
    my_socket.send(icm_body)

    while True:
        # Receive base file existence message
        device_id, message_id, data_size, existence_flag, data_2, data_3 \
            = packet_manager.message_receiver(my_socket, device_id)

        if existence_flag == 1:
            break

        # Send base video message
        bvm_header, bvm_body, bvm_payload_size = packet_manager.make_base_video_message(device_id, client_base_video_data)
        my_socket.send(bvm_header)
        my_socket.send(bvm_body)
        payload_size_all += bvm_payload_size

    while True:
        # Send image difference message
        idm_header, idm_body, idm_payload_size = packet_manager.make_image_difference_message(device_id,
                                                                            client_time_stamp_str,
                                                                            client_header_difference_data,
                                                                            client_additional_frame_data)
        my_socket.send(idm_header)
        my_socket.send(idm_body)
        payload_size_all += idm_payload_size

        # Receive final message
        device_id, message_id, data_size, success_flag, data_2, data_3 \
            = packet_manager.message_receiver(my_socket, device_id)
        if success_flag == 1:
            break

    my_socket.close()

    elapsed_time = time.time() - start_time
    # print("{} seconds".format(elapsed_time))

    return 0, elapsed_time, payload_size_all


if __name__ == "__main__":
    DEVICE_ID = 1

    print("Usage: python3 " + __file__ + " <server ip address> <server port> <device id> <base image path(*.jpg)> <target image path(*.jpg)>")

    ret = 0
    et = 0
    ps = 0
    if len(sys.argv) >= 6:
        ret, et, ps = cilent(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5])
    else:
        ret, et, ps = cilent("127.0.0.1", 10000, DEVICE_ID, "./img/20201218_0600.jpg", "./img/20201218_0602.jpg")

    print("{}, seconds".format(et))