import rospy
from nav_msgs.msg import Odometry
import threading
from math import asin, atan2, pi
from jderobotTypes import Pose3d

def quat2Yaw(qw, qx, qy, qz):
    rotateZa0=2.0*(qx*qy + qw*qz)
    rotateZa1=qw*qw + qx*qx - qy*qy - qz*qz
    rotateZ=0.0
    if(rotateZa0 != 0.0 and rotateZa1 != 0.0):
        rotateZ=atan2(rotateZa0,rotateZa1)
    return rotateZ

def quat2Pitch(qw, qx, qy, qz):
    rotateYa0=-2.0*(qx*qz - qw*qy)
    rotateY=0.0
    if(rotateYa0 >= 1.0):
        rotateY = pi/2.0
    elif(rotateYa0 <= -1.0):
        rotateY = -pi/2.0
    else:
        rotateY = asin(rotateYa0)

    return rotateY

def quat2Roll (qw, qx, qy, qz):
    rotateXa0=2.0*(qy*qz + qw*qx)
    rotateXa1=qw*qw - qx*qx - qy*qy + qz*qz
    rotateX=0.0

    if(rotateXa0 != 0.0 and rotateXa1 != 0.0):
        rotateX=atan2(rotateXa0, rotateXa1)
    return rotateX


def odometry2Pose3D(odom):
    pose = Pose3d()
    ori = odom.pose.pose.orientation

    pose.x = odom.pose.pose.position.x
    pose.y = odom.pose.pose.position.y
    pose.z = odom.pose.pose.position.z
    #pose.h = odom.pose.pose.position.h
    pose.yaw = quat2Yaw(ori.w, ori.x, ori.y, ori.z)
    pose.pitch = quat2Pitch(ori.w, ori.x, ori.y, ori.z)
    pose.roll = quat2Roll(ori.w, ori.x, ori.y, ori.z)
    pose.q = [ori.w, ori.x, ori.y, ori.z]
    pose.timeStamp = odom.header.stamp.secs + (odom.header.stamp.nsecs *1e-9)

    return pose


class ListenerPose3d:
    def __init__(self, topic):
        self.topic = topic
        self.data = Pose3d()
        self.sub = None
        self.lock = threading.Lock()
        self.start()
 
    def __callback (self, odom):
        pose = odometry2Pose3D(odom)

        self.lock.acquire()
        self.data = pose
        self.lock.release()
        
    def stop(self):
        self.sub.unregister()

    def start (self):
        self.sub = rospy.Subscriber(self.topic, Odometry, self.__callback)
        
    def getPose3d(self):
        self.lock.acquire()
        pose = self.data
        self.lock.release()
        
        return pose


