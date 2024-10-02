#!/usr/bin/env python

from enum import Enum
import time


class GripperState(Enum):
    OPEN = 0
    CLOSED = 1

class Robot():

    def __init__(self, initial_position: list[float] = [0,0,0], home_position: list[float] = [0,0,0] , gripper_state: GripperState = GripperState.OPEN):
        """
            Parameters:
                initial_position (list[float]) : 3D initial position of the robot (mm)
                home_position (list[float]) : 3D home position of the robot (mm)
                gripper_state (GripperState(Enum)) : Initial state of the gripper
            
            Returns:
                None
        """
        
        self.current_position: list[float] = initial_position
        self.home_position: list[float]  = home_position
        self.gripper_state: GripperState = gripper_state 
        self.last_motion_time: float = 0
        self.axis_speed = [0,0,0]
        self.robot_limits = [1000,1000,1000]

    def _plan_motion(self, target_position: list[float], speed: int):
        """Plan the robot motion by adjusting axis speeds in function of the control axis.

            Parameters:
                target_position (list[float]) : 3D Pose to move to (mm)
                speed (int) : Linear speed of the robot in mm/s [0,100]
            
            Returns: 
                axis_speed list(int) : Linear speed of the robot axis in mm/s [0,100]
        """
        delta = [target_position[i] - self.current_position[i] for i in range(len(self.current_position))]
        control_axis_distance = max(delta, key=abs) 
        motion_time = abs(control_axis_distance) / speed
        axis_speed = [i/motion_time for i in delta]

        return axis_speed
    
    def _same_position(self,target_position: list[float]) -> bool :
        """Validate if the current position is the same as the targeted one.

            Parameters:
                target_position (list[float]) : 3D Pose to move to (mm)
            
            Returns: 
                bool : Robot is at targeted position or not
        """
        return all(i == 0 for i in [target_position[i] - self.current_position[i] for i in range(len(self.current_position))])

    def _is_motion_completed(self, target_position: list[float]) -> bool :
        """Validate if the motion is completed

            Parameters:
                target_position (list[float]) : 3D Pose to move to (mm)
            
            Returns: 
                bool : motion is completed or not
        """
        for i,j in enumerate(target_position): 
            if (j-self.current_position[i] >= 0 <= self.axis_speed[i]) or (j-self.current_position[i] <= 0 >= self.axis_speed[i]):
                return False
        return True
        
    def move_to(self, target_position: list[float], speed: int = 90):
        """Move the robot to target_pose

            Parameters:
                target_position (list[float]) : 3D Pose to move to (mm)
                speed (int) : Linear speed of the robot in mm/s [0,100]
            Returns:
                current_position (list[float]) : 3D current position of the robot (mm)
                axis_speed (list[float]) : List of axis speeds (mm/s)
                err_msg (string) : error message 
        """

        if not (0 <= speed <= 100) : return self.current_position, self.axis_speed, f"Requested speed of : {speed} mm/s is outside of the limits [0,100]"
        for i,j in enumerate(target_position) :
            if j > self.robot_limits[i] or j < -self.robot_limits[i] :
                return self.current_position, self.axis_speed, f"Requested position of : {j} for axis {i} is outside of the limits {self.robot_limits}"

        if self._same_position(target_position): return self.current_position, self.axis_speed, None

        actual_time = time.perf_counter()

        if all(v == 0 for v in self.axis_speed):
            self.axis_speed = self._plan_motion(target_position, speed)
            self.last_motion_time = actual_time

        delta_t = actual_time - self.last_motion_time

        self.current_position = [self.current_position[i] + delta_t * self.axis_speed[i] for i in range(len(self.current_position))]
 
        self.last_motion_time = time.perf_counter()

        if self._is_motion_completed(target_position):
            self.axis_speed = [0,0,0]
            self.current_position = target_position            
        
        return self.current_position, self.axis_speed, None

    def closed_gripper(self) -> GripperState:
        """Close the robot gripper.

            Parameters:
            
            Returns: 
                gripper_state (GripperState) : GripperState.CLOSED
        """
        self.gripper_state = GripperState.CLOSED
        return self.gripper_state

    def open_gripper(self) -> bool:
        """OPEN the robot gripper.

            Parameters:
            
            Returns: 
                gripper_state (GripperState) : GripperState.OPEN
        """
        self.gripper_state = GripperState.OPEN
        return self.gripper_state

    def move_home(self, speed: int = 50) -> bool:
        """Function that moves the robot to its home position

            Parameters:
                speed (int) : Linear speed of the robot in mm/s [0,100]
            
            Returns:
                current_position (list[float]) : 3D current position of the robot (mm)
                axis_speed (list[float]) : List of axis speeds (mm/s)
                err_msg (string) : error message 
                
        """
        return self.move_to(self.home_position, speed)


if __name__=='__main__':
    pass