import os
import packet_manager
import video_file_manager
import socket
import hashlib
import sys

def server(server_ip_address, server_port,
           server_base_video_dir_root="./server_base/",
           server_base_video_filename="base.mp4",
           server_extracted_img_dir_root="./extracted_img/",
           video_ext=".mp4"):

    ACCEPT_QUEUE_NUM = 3

    if not os.path.exists(server_base_video_dir_root):
        os.mkdir(server_base_video_dir_root)
    if not os.path.exists(server_extracted_img_dir_root):
        os.mkdir(server_extracted_img_dir_root)

    server_base_video_dir = None
    server_extracted_img_dir = None

    # make socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind((server_ip_address, server_port))
    my_socket.listen(ACCEPT_QUEUE_NUM)

    while True:
        print("Info: waiting a client ...")
        conn, addr = my_socket.accept()
        print("Info: Accepted")
        target_device_id = None
        with conn:
            while True:
                device_id, message_id, data_size, data_1, data_2, data_3 \
                    = packet_manager.message_receiver(conn, target_device_id)

                # Initial confirmation message is received
                if message_id == packet_manager.MESSAGE_ID_INITIAL:
                    target_device_id = device_id
                    received_hash = data_1

                    # Preparing directory for base video
                    server_base_video_dir = server_base_video_dir_root + str(target_device_id).zfill(2) + "/"
                    server_base_video_path = server_base_video_dir + server_base_video_filename
                    if not os.path.exists(server_base_video_dir):
                        os.mkdir(server_base_video_dir)

                    # Preparing directory for extracted img
                    server_extracted_img_dir = server_extracted_img_dir_root + str(target_device_id).zfill(2) + "/"
                    if not os.path.exists(server_extracted_img_dir):
                        os.mkdir(server_extracted_img_dir)

                    existence_flag = 0
                    if os.path.exists(server_base_video_path):
                        # Make MD5 hash
                        server_base_video_file = open(server_base_video_path, "rb")
                        server_base_video_data = server_base_video_file.read()
                        hash_binary = hashlib.md5(server_base_video_data).digest()
                        if hash_binary == received_hash:
                            existence_flag = 1

                    if existence_flag == 0:
                        print("Info: No base video file")

                    # Send base video existence message
                    bvem_header, bvem_body, bvem_payload_size\
                        = packet_manager.make_base_video_existence_message(target_device_id, existence_flag)
                    conn.send(bvem_header)
                    conn.send(bvem_body)

                # Base video message is received
                elif message_id == packet_manager.MESSAGE_ID_BASE_VIDEO:
                    if server_base_video_path is None:
                        print("Error: Base video path is not defined")
                        conn.close()
                        break

                    if os.path.exists(server_base_video_path):
                        os.remove(server_base_video_path)

                    server_base_video_file = open(server_base_video_path, "wb")
                    server_base_video_file.write(data_1)
                    server_base_video_file.close()

                    # Send base video existence message
                    existence_flag = 1
                    bvem_header, bvem_body, bvem_payload_size \
                        = packet_manager.make_base_video_existence_message(target_device_id, existence_flag)
                    conn.send(bvem_header)
                    conn.send(bvem_body)

                # Image difference message is received
                elif message_id == packet_manager.MESSAGE_ID_DIFFERENCE:
                    if server_base_video_path is None:
                        print("Error: Base video path is not defined")
                        conn.close()
                        break

                    if server_extracted_img_dir is None:
                        print("Error: Extracted image directory is not defined")
                        conn.close()
                        break

                    server_time_stamp_str = data_1
                    server_header_difference_data = data_2
                    server_additional_frame_data = data_3

                    # Make a reconstructed video
                    server_base_video_file = open(server_base_video_path, "rb")
                    server_target_video_data = server_base_video_file.read()
                    server_base_video_file.close()
                    server_target_video_data = bytearray(server_target_video_data)
                    for i in range(4):
                        server_target_video_data[packet_manager.HEADER_DIFFERENCE_DATA_OFFSET + i] \
                            = server_header_difference_data[i]

                    client_additional_frame_data_offset \
                        = os.path.getsize(server_base_video_path) - packet_manager.FOOTER_DATA_OFFSET
                    server_target_video_data = server_target_video_data[:client_additional_frame_data_offset]
                    server_target_video_data = server_target_video_data + server_additional_frame_data

                    server_target_video_path = server_base_video_dir + "target" + video_ext
                    if os.path.exists(server_target_video_path):
                        os.remove(server_target_video_path)
                    server_target_video_file = open(server_target_video_path, "wb")
                    server_target_video_file.write(server_target_video_data)
                    server_target_video_file.close()

                    # Decompression
                    video_file_manager.decompression(server_target_video_path,
                                                     server_extracted_img_dir,
                                                     server_time_stamp_str + ".jpg")

                    # Send final message
                    final_flag = 1
                    fm_header, fm_body, fm_payload_size = packet_manager.make_final_message(target_device_id, final_flag)
                    conn.send(fm_header)
                    conn.send(fm_body)

                    if final_flag == 1:
                        break
                    else:
                        break  # Todo: Server does not stop receiving when image extraction was failed and receives image difference message once more


if __name__ == "__main__":
    print("Usage: python3 " + __file__ + " <server ip address> <server port>")

    if len(sys.argv) >= 3:
        server(sys.argv[1], int(sys.argv[2]))
    else:
        server("127.0.0.1", 10000)
