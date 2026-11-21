#!/usr/bin/python3
"""Invoca o serviço ROS da VM YIN com o segredo obtido da VM YANG."""
import sys

import rospy
from yin.srv import yangrequest


if len(sys.argv) != 3:
    raise SystemExit(f"Uso: {sys.argv[0]} <segredo> <comando>")

rospy.init_node("sidequest_call_yin", anonymous=True)
rospy.wait_for_service("svc_yang", timeout=10)
service = rospy.ServiceProxy("svc_yang", yangrequest)
reply = service(sys.argv[1], sys.argv[2], "Yang", "Yin")
print(reply.response)
