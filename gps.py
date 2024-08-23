#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import NavSatFix
import serial
import time

def parse_nmea_sentence(nmea_sentence):
    data = nmea_sentence.split(',')

    if data[0] == "$GNGGA":
        try:
            lat_deg = float(data[2][:2])
            lat_min = float(data[2][2:])
            latitude = lat_deg + (lat_min / 60.0)
            if data[3] == 'S':
                latitude = -latitude

            lon_deg = float(data[4][:3])
            lon_min = float(data[4][3:])
            longitude = lon_deg + (lon_min / 60.0)
            if data[5] == 'W':
                longitude = -longitude

            altitude = float(data[9])

            return latitude, longitude, altitude
        except (ValueError, IndexError) as e:
            rospy.logwarn(f"Failed to parse NMEA sentence: {e}")
            return None, None, None
    else:
        return None, None, None

def set_gps_rate_10hz(ser):
    # UBX command to set update rate to 10 Hz (100 ms)
    ubx_command = bytes([0xB5, 0x62, 0x06, 0x08, 0x06, 0x00,
                         0x64, 0x00, 0x01, 0x00, 0x01, 0x00,
                         0x7A, 0x12])  # Command to set rate to 10 Hz
    
    rospy.loginfo("Sending command to set GPS update rate to 10 Hz...")
    ser.write(ubx_command)
    time.sleep(1)  # Give time for the GPS module to process the command

def talker(port="/dev/ttyACM0", baudrate=38400):
    rospy.init_node('gps_data_publisher', anonymous=True)
    pub = rospy.Publisher('/gps_data', NavSatFix, queue_size=10)

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        rospy.loginfo(f"Connected to GPS module on {port} at {baudrate} bps.")

        # Set GPS update rate to 10 Hz
        set_gps_rate_10hz(ser)

        while not rospy.is_shutdown():
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line.startswith("$GNGGA"):
                lat, lon, alt = parse_nmea_sentence(line)
                if lat is not None and lon is not None and alt is not None:
                    gps_fix = NavSatFix()
                    gps_fix.header.stamp = rospy.Time.now()
                    gps_fix.header.frame_id = "gps"
                    gps_fix.latitude = lat
                    gps_fix.longitude = lon
                    gps_fix.altitude = alt

                    pub.publish(gps_fix)
                    rospy.loginfo(f"Published GPS data: Lat: {lat:.6f}, Lon: {lon:.6f}, Alt: {alt:.2f} m")
    except serial.SerialException as e:
        rospy.logerr(f"Serial Exception: {e}")
    except rospy.ROSInterruptException:
        ser.close()
        rospy.loginfo("Terminating GPS data publisher.")
    finally:
        ser.close()
        rospy.loginfo("Serial connection closed.")

if __name__ == "__main__":
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

