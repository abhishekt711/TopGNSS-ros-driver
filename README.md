# TopGNSS-ros-package
ROS package of TOP USB GNSS receiver : checked with TOP608BT USB GNSS receiver sensor, will work with all other USB GNSS sensor with NMEA0183 msg.

Plug the USB GNSS sensor in USB of the system. and run this command in terminal : ls /dev/tty*

you will get the list of usb port name, you will find /dev/ttyACM0 or sudo cat /dev/ttyUSB. whatever you found in terminal change the port name in 57th line of the python code: port = "/dev/ttyACM0"

run the python code : python3 gps.py

in next terminal run command: rostopic echo gps/data

GPS data will come in the terminal at 10Hz:



![Screenshot from 2024-08-24 03-17-27](https://github.com/user-attachments/assets/cbc030b8-c61c-40c4-8ea3-a76fef39d412)
