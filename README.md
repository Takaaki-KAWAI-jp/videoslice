# Video Slice: Image Compression and Transmission for Agricultural Systems (https://www.mdpi.com/1424-8220/21/11/3698)

## Introduction
This web page provides the source code of video slice prototype described in the  paper of video slice.

## Source code
### client.py
+ Usage
  + python3 ./client.py \<server ip address\> \<server port\> \<device id\> \<base image path(\*.jpg)\> \<target image path(\*.jpg)\>
+ default parameter
  + python3 ./client.py 127.0.0.1 10000 1 ./img/20201218_0600.jpg ./img/20201218_0602.jpg
+ Note
  + The name of image files should be "YYYYmmdd_HHMM.jpg" where "YYYY" is year, "mm" is month, "dd" is day, "HH" is hour, "MM" is minute.
  + Server makes the directory named client_base
  + The base video file and the target video file are created in client_base.
  + The base video file has same file name as original base image file, and this file name is used to confirm the existence of base video file corresponding to today's base image file.

### server.py
+ Usage:
  + python3 ./server.py  \<server ip address\> \<server port\>
+ default parameter
  + python3 ./client.py 127.0.0.1 10000
+ Note
  + Server makes the directories named server_base, extracted_img.
  + The base video file and the target video file are created in server_base.
  + The base video file name is base.mp4
  + The extracted images are created in extracted_img/\<Device ID of client\>/.

### packet_manager.py and video_file_manager.py
Used by client.py and server.py
