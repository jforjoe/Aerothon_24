def control_servo(pixhawk_connection, servo_channel=9, pwm_value=1900):
    """
    Controls a servo connected to the Pixhawk.
    
    Parameters:
    - pixhawk_connection: The mavutil connection object to the Pixhawk.
    - servo_channel: The channel number of the servo (default is 9).
    - pwm_value: The PWM value to set the servo position (e.g., 1900 to release, 1100 to reset).
    """
    # Send command to control servo
    pixhawk_connection.mav.command_long_send(
        pixhawk_connection.target_system,    # Target system
        pixhawk_connection.target_component, # Target component
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, # Command ID for servo control
        0,                                   # Confirmation
        servo_channel,                       # Servo channel (e.g., 9)
        pwm_value,                           # PWM value (1900 for release, 1100 for reset)
        0, 0, 0, 0, 0                        # Unused parameters
    )
    print(f"Servo on channel {servo_channel} set to PWM {pwm_value}")
