MAVLink commands allow you to control various aspects of the drone's behavior, such as setting modes, arming/disarming, moving to positions, adjusting orientation, etc. Here’s a breakdown of the most commonly used MAVLink commands and messages for drone control, specifically useful for a Raspberry Pi-Pixhawk setup.

### 1. **Connection Setup**
Establish a MAVLink connection from your Raspberry Pi to the Pixhawk using a serial or UDP connection:

```python
from pymavlink import mavutil

# Serial connection (replace with correct serial port and baud rate)
connection_string = '/dev/ttyAMA0'  # example serial port
baud_rate = 57600
master = mavutil.mavlink_connection(connection_string, baud=baud_rate)

# Wait for the heartbeat to confirm connection
print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Heartbeat received!")
```

### 2. **Basic MAVLink Commands**

#### **1. Arming and Disarming the Drone**

- **Arming**: Enables motors and prepares for takeoff.
- **Disarming**: Disables motors after landing or in emergencies.

```python
# Arm the drone
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0)

# Disarm the drone
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0, 0, 0, 0, 0, 0, 0)
```

#### **2. Setting Flight Modes**

Common flight modes include `GUIDED`, `STABILIZE`, `LOITER`, `AUTO`, and `RTL` (Return to Launch).

```python
# Set mode to GUIDED
mode = 'GUIDED'
mode_id = master.mode_mapping()[mode]
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id)
```

### 3. **Control Commands**

#### **1. Moving the Drone with `SET_POSITION_TARGET_LOCAL_NED`**
This command allows you to set local position targets, including coordinates, velocity, and acceleration. 

```python
# Move forward at 1 m/s
master.mav.set_position_target_local_ned_send(
    0,  # time_boot_ms (not used)
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    0b0000111111000111,  # bitmask - ignore position, only use velocity
    0, 0, 0,  # X, Y, Z positions (ignored here)
    1.0, 0, 0,  # X, Y, Z velocities in m/s (move forward along X-axis)
    0, 0, 0,  # accelerations (not used)
    0, 0)     # yaw, yaw rate (not used)
```

**Note**: Set `X`, `Y`, `Z` velocities for directional control. Positive X moves forward, positive Y moves to the right, and negative Z moves up.

#### **2. Set Absolute or Relative Yaw with `CONDITION_YAW`**

Adjusting the yaw lets you control the drone's heading.

```python
# Set absolute yaw to 90 degrees
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_YAW,
    0,
    90,  # target angle
    20,  # yaw speed (deg/s)
    1,   # direction (1: clockwise, -1: counterclockwise)
    0,   # absolute angle
    0, 0, 0)  # unused params
```

For relative yaw, change the last parameter to `1` (relative offset).

#### **3. Takeoff with `COMMAND_TAKEOFF`**
Initiates takeoff to a specified altitude (requires GUIDED mode).

```python
# Takeoff to 10 meters
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0,
    0, 0, 0, 0, 0, 0, 10)  # altitude = 10 meters
```

#### **4. Return to Launch (RTL)**
Commands the drone to return to its launch position.

```python
# Return to Launch
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
    0,
    0, 0, 0, 0, 0, 0, 0)
```

#### **5. Landing with `COMMAND_LAND`**
Initiates landing at the current position.

```python
# Land the drone
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND,
    0,
    0, 0, 0, 0, 0, 0, 0)
```

### 4. **Reading Telemetry Data**

#### **1. Getting Heading from VFR_HUD**
Retrieve the drone’s heading, altitude, and other telemetry data.

```python
# Get current heading
msg = master.recv_match(type='VFR_HUD', blocking=True)
heading = msg.heading  # heading in degrees
altitude = msg.alt     # altitude in meters
print(f"Heading: {heading}, Altitude: {altitude}")
```

#### **2. Reading Attitude Data**
The `ATTITUDE` message provides roll, pitch, and yaw angles.

```python
msg = master.recv_match(type='ATTITUDE', blocking=True)
roll = msg.roll
pitch = msg.pitch
yaw = msg.yaw
print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
```

#### **3. Custom Message Frequencies with `SET_MESSAGE_INTERVAL`**
Control the frequency of specific messages (e.g., attitude, GPS) from the Pixhawk.

```python
# Request ATTITUDE message at 10 Hz
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0,
    mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,  # Message ID
    1e6 / 10,  # Interval in microseconds (10 Hz)
    0, 0, 0, 0, 0)
```

### 5. **Emergency Safety Function**

For emergencies, use `MAV_CMD_OVERRIDE_GOTO` or switch to an autonomous mode like `RTL`.

```python
# Switch to AUTO mode for safety
master.mav.set_mode_send(
    master.target_system,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    master.mode_mapping()['AUTO'])
```

### Summary of Useful MAVLink Commands
| MAVLink Command | Function |
|-----------------|----------|
| `MAV_CMD_COMPONENT_ARM_DISARM` | Arm/Disarm the drone |
| `MAV_CMD_NAV_TAKEOFF` | Takeoff to a specified altitude |
| `MAV_CMD_NAV_LAND` | Land at the current location |
| `MAV_CMD_NAV_RETURN_TO_LAUNCH` | Return to the launch position (RTL) |
| `MAV_CMD_CONDITION_YAW` | Set yaw heading (absolute or relative) |
| `SET_POSITION_TARGET_LOCAL_NED` | Move with specified velocities or positions |
| `MAV_CMD_OVERRIDE_GOTO` | Emergency stop or go-to command |
| `SET_MESSAGE_INTERVAL` | Control message update frequency |

____
____
____


### 6. **Advanced Position and Velocity Control**

#### **1. Global Position Control (`SET_POSITION_TARGET_GLOBAL_INT`)**
For movement in global coordinates (latitude, longitude, altitude), useful for GPS-based navigation.

```python
# Move to a specific GPS location
master.mav.set_position_target_global_int_send(
    0,  # time_boot_ms
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    0b0000111111111000,  # bitmask - ignore velocity and acceleration
    int(latitude * 1e7),  # Latitude in degrees * 1e7
    int(longitude * 1e7),  # Longitude in degrees * 1e7
    altitude,  # Altitude in meters
    0, 0, 0,  # X, Y, Z velocity (ignored)
    0, 0, 0,  # X, Y, Z acceleration (ignored)
    0, 0)  # yaw, yaw rate
```

#### **2. Velocity Control with `SET_POSITION_TARGET_LOCAL_NED`**
Set directional speed along specific axes, suitable for precise maneuvering in local space.

```python
# Move sideways at 1 m/s
master.mav.set_position_target_local_ned_send(
    0,
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    0b0000111111000111,  # bitmask
    0, 0, 0,  # Positions ignored
    0, 1.0, 0,  # Set Y-axis velocity to 1 m/s (move right)
    0, 0, 0,  # Accelerations ignored
    0, 0)     # yaw, yaw rate
```

### 7. **Waypoint Navigation and Missions**

For multi-waypoint missions, `MISSION_ITEM_INT` allows adding waypoints. Combine it with `MISSION_COUNT` to upload multiple waypoints, and `MISSION_START` to execute the mission.

```python
# Add a waypoint at a specific latitude, longitude, and altitude
master.mav.mission_item_int_send(
    master.target_system,
    master.target_component,
    seq,  # Sequence number of waypoint
    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
    0,  # current (0=not current, 1=current)
    1,  # autocontinue
    0, 0, 0, 0,  # params 1-4 unused for waypoint
    int(latitude * 1e7),  # Latitude
    int(longitude * 1e7),  # Longitude
    altitude)  # Altitude
```

### 8. **Specialized Commands**

#### **1. Loitering with `MAV_CMD_NAV_LOITER_TIME`**
Loiters for a specified time at the current or designated position.

```python
# Loiter at current position for 30 seconds
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME,
    0,
    30,  # loiter time in seconds
    0, 0, 0, 0, 0, 0)
```

#### **2. Precision Land (`MAV_CMD_NAV_LAND_LOCAL`)**
Land at a precise local position, often useful with sensors for precision landing (e.g., visual markers).

```python
# Land at a specific local position
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_LAND_LOCAL,
    0,
    0, 0, 0,  # params 1-3 not used
    0, 0, 0, 0)  # unused
```

#### **3. Follow Target Mode**
Set the drone to follow a GPS target dynamically.

```python
# Set follow target mode
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_DO_FOLLOW,
    0,
    target_lat, target_lon, 10, 0, 1, 0, 0)  # target lat/lon and altitude
```

### 9. **Condition-Based Commands**

These commands perform specific actions once a condition is met, such as reaching a heading, distance, or altitude.

#### **1. Condition Reach Altitude (`MAV_CMD_CONDITION_CHANGE_ALT`)**
This sets the vehicle to maintain a target altitude.

```python
# Change altitude to 20 meters
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
    0,
    20, 0, 0, 0, 0, 0, 0)  # target altitude
```

#### **2. Condition Delay (`MAV_CMD_CONDITION_DELAY`)**
Delays subsequent commands until a set amount of time has passed.

```python
# Delay for 10 seconds
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_CONDITION_DELAY,
    0,
    10, 0, 0, 0, 0, 0, 0)  # delay in seconds
```

### 10. **Data Collection and Telemetry**

#### **1. Getting GPS Information**
Retrieves GPS data, including latitude, longitude, altitude, and accuracy.

```python
msg = master.recv_match(type='GPS_RAW_INT', blocking=True)
latitude = msg.lat / 1e7  # in degrees
longitude = msg.lon / 1e7  # in degrees
altitude = msg.alt / 1000  # in meters
print(f"GPS: {latitude}, {longitude}, {altitude}")
```

#### **2. Battery Status**
Monitor the battery’s voltage, current, and remaining capacity.

```python
msg = master.recv_match(type='BATTERY_STATUS', blocking=True)
voltage = msg.voltages[0] / 1000.0  # in volts
remaining = msg.battery_remaining    # in percentage
print(f"Battery: {voltage}V, {remaining}% remaining")
```

### MAVLink Command Overview Table

| MAVLink Command                         | Function                                 |
|-----------------------------------------|------------------------------------------|
| `MAV_CMD_NAV_WAYPOINT`                  | Adds a waypoint to mission               |
| `MAV_CMD_NAV_LOITER_TIME`               | Loiters at a position for a set time     |
| `MAV_CMD_NAV_LAND_LOCAL`                | Precision land at a specific local point |
| `MAV_CMD_DO_FOLLOW`                     | Follow a moving target                   |
| `MAV_CMD_CONDITION_CHANGE_ALT`          | Change altitude to specified level       |
| `MAV_CMD_CONDITION_DELAY`               | Delay next command by a time period      |
| `MAV_CMD_DO_SET_RELAY`                  | Control GPIO pin on Pixhawk for relays   |
| `MAV_CMD_DO_SET_SERVO`                  | Control servo positions directly         |
| `SET_POSITION_TARGET_GLOBAL_INT`        | Control position using GPS coordinates   |
| `SET_POSITION_TARGET_LOCAL_NED`         | Control position in local NED coordinates|

The above commands and examples will provide comprehensive control over the Pixhawk and allow you to implement both basic and complex mission functions from a Raspberry Pi. These can be expanded with more specialized commands as your requirements grow. For more MAVLink commands, refer to the [MAVLink command documentation](https://mavlink.io/en/messages/common.html) for specific versions and updates.
