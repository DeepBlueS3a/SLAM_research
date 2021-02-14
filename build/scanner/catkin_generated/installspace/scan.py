#!/usr/bin/env python2

import rospy
import time
from geometry_msgs.msg import Twist
from math import pi
import math
import tf



class Bot:
    def __init__(self, one_rot_ps=2*pi, one_mps=1, invert=True, factor=1):
        # i've defaulted invert to true, because it's like that in my bot
        if invert:
            self.invert = -1 * factor
        else:
            self.invert = 1 * factor
        self.twist = Twist()
        self.one_rot_ps = one_rot_ps
        self.one_mps = one_mps
# think of one_rot_ps and one_mps as the units that we multiply to the end of the speed/velocity


    def default_twist(self):
        self.twist = Twist()
        return self.twist

    def turn(self, rots, time, rewrite=False):
        if rewrite:
            self.default_twist()

        self.twist.angular.z = (float(rots)/float(time))*self.one_rot_ps * self.invert
        return self.twist

    def move(self, dist, time, rewrite=False):
        if rewrite:
            self.default_twist()

        self.twist.linear.x = (float(dist)/float(time))*self.one_mps * self.invert
        return self.twist

    @staticmethod
    def get_angle(tf_tup): # takes transform in quaternion value, and returns the angle in degrees
        tf_rot = tf_tup[1]
        tf_rot_angle = tf.transformations.euler_from_quaternion(tf_rot)[2] * (180/math.pi)
        if tf_rot_angle < 0:
            tf_rot_angle += 360
        tf_rot_angle = round(tf_rot_angle, 3)
        return tf_rot_angle

    @staticmethod
    def get_dist(tf_tup1, tf_tup2):
        tf_mv1 = tf_tup1[0]
        tf_mv2 = tf_tup2[0]

        dist = 0
        for x1, x2 in zip(tf_mv1, tf_mv2):
            dist += (x1 - x2) **2
        dist = math.sqrt(dist)
        return dist


print("Initializing node")
rospy.init_node("scanner", anonymous=False)
#radial_turn_positioner = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
radial_turn_positioner = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
#position = rospy.

vel_msg = Twist()

def radial_scan():
    """
        We need the bot to move in a spiral, so I'll just keep the angular velocity constant
        And accelerate the linear velocity, so as to increase the radius of rotation
        so, we can find the velocity using the formula v = u + at

        The angular velocity z doesn't add any linear velocity, as the axis of rotation
        is about the centre of mass of the robot, which just makes it turn, 
        and not give any linear velocity at all
    """

    radius_to_scan = 10 # in metres, or whatever units are used in the gazebo thingy
    angular_speed = 2*pi # 1 rotation per second

    time_to_complete = 300 # seconds

    v_initial = 0
    v_final = 2 * pi * radius_to_scan * angular_speed / (2*pi) 
    # angular_speed / angle covered in one rotation = 1 / time_taken
    # and, total distance travelled = 2 * pi * r in the final circle, so
    # v_final = 2*pi*r*(angular_speed/2*pi)

    acceleration = (v_final - v_initial)/time_to_complete
    print("The acceleration is : ", acceleration)

    v_current = 0
    vel_msg.angular.z = angular_speed

    time_at_start = time.time()
    while v_current <= v_final:
        v_current = v_initial + acceleration*(time.time()-time_at_start)
        if int(time.time()-time_at_start) % 2 == 0:
            print("moving with velocity : ", v_current) 
        vel_msg.linear.x = -v_current # cuz the bot's movement thingy has to be reversed
        radial_turn_positioner.publish(vel_msg)

def circle():
    radius = 5
    bot = Bot(one_rot_ps=6.8*pi, one_mps=2.8)
    publisher = radial_turn_positioner
    msg = bot.turn(0.25, 5) # angular_vel = (6.8/20)pi => time for one rot = 5.88
    angular_vel = bot.twist.angular.z
    time_for_one_rot = 20 # seconds
    msg = bot.move(2*pi*radius, time_for_one_rot)
    print(msg)
    time_init = time.time()
    while time.time() - time_init <= time_for_one_rot:
        publisher.publish(msg)
    msg = bot.default_twist()
    publisher.publish(msg)

if __name__ == "__main__":
#    while not rospy.is_shutdown():
#    radial_scan()
    circle()
    exit(0)