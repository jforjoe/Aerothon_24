from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
from pymavlink import mavutil
import math

# Connection string for Pixhawk
# Replace with your connection port (usually /dev/ttyACM0 or /dev/ttyAMA0)
connection_string = '/dev/ttyACM0'
baud_rate = 57600

print('Connecting to vehicle on: %s' % connection_string)

try:
    # Connect to the Vehicle
    vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)

    def set_yaw(heading, relative=False):
        """
        Set vehicle yaw to specific heading (in degrees).
        relative: True if heading is relative to current position, False for absolute heading
        """
        if relative:
            is_relative = 1
        else:
            is_relative = 0

        # Create the CONDITION_YAW command
        msg = vehicle.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW, # command
            0,       # confirmation
            heading, # param 1 - target angle
            25,     # param 2 - angular speed deg/s
            1,      # param 3 - direction (-1:ccw, 1:cw)
            is_relative, # param 4 - relative offset (1) or absolute angle (0)
            0, 0, 0 # param 5-7 not used
        )
        
        # Send command to vehicle
        vehicle.send_mavlink(msg)

    def get_heading():
        """Get the current heading in degrees (0-360)"""
        return vehicle.heading

    def align_to_target(target_heading):
        """
        Align the drone to a target heading
        """
        current_heading = get_heading()
        heading_error = target_heading - current_heading
        
        # Normalize the error to [-180, 180]
        if heading_error > 180:
            heading_error -= 360
        elif heading_error < -180:
            heading_error += 360
            
        print(f"Current Heading: {current_heading}")
        print(f"Target Heading: {target_heading}")
        print(f"Heading Error: {heading_error}")
        
        # Set the new heading
        set_yaw(heading_error, relative=True)
        
        return abs(heading_error)

    def main():
        print("Basic pre-arm checks")
        while not vehicle.is_armable:
            print("Waiting for vehicle to initialize...")
            time.sleep(1)

        print("Arming motors")
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        while not vehicle.armed:
            print("Waiting for arming...")
            time.sleep(1)

        print("Vehicle armed!")
        
        while True:
            print("\nCurrent vehicle heading: %s" % get_heading())
            print("\nAvailable commands:")
            print("1: Set absolute heading (0-360 degrees)")
            print("2: Set relative heading (-180 to 180 degrees)")
            print("3: Print current status")
            print("q: Quit")
            
            choice = input("Enter command: ")
            
            if choice == '1':
                try:
                    target = float(input("Enter target heading (0-360): "))
                    if 0 <= target <= 360:
                        error = align_to_target(target)
                        print(f"Aligning to heading: {target}")
                        time.sleep(3)  # Wait for movement to complete
                    else:
                        print("Invalid heading value")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '2':
                try:
                    relative = float(input("Enter relative heading change (-180 to 180): "))
                    if -180 <= relative <= 180:
                        print(f"Changing heading by: {relative}")
                        set_yaw(relative, relative=True)
                        time.sleep(3)  # Wait for movement to complete
                    else:
                        print("Invalid heading value")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '3':
                print("\nVehicle Status:")
                print(f"Heading: {get_heading()}")
                print(f"Mode: {vehicle.mode.name}")
                print(f"Armed: {vehicle.armed}")
                print(f"System status: {vehicle.system_status.state}")
                
            elif choice.lower() == 'q':
                break
                
            else:
                print("Invalid command")

    if __name__ == '__main__':
        try:
            main()
        finally:
            print("\nClosing vehicle")
            vehicle.close()

except Exception as e:
    print(f"Error: {e}")
    print("Failed to connect to vehicle.")