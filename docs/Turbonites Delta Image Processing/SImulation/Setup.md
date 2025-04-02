
1. Ubuntu version :  https://releases.ubuntu.com/focal/
4. Drone Firmware based environments:
	1. PX4 Dev Env setup : https://docs.px4.io/v1.14/en/dev_setup/dev_env_linux_ubuntu.html#ros-gazebo-classic
	2. SITL (Ardupilot) :  https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux
		1. Initial:
			1. `https://github.com/ArduPilot/ardupilot.git` for the main ardupilot repo
			2. `ardupilot/Tools/environment_install/install-prereqs-ubuntu.sh -y`
			3. Reload the path (log-out and log-in to make it permanent):  `. ~/.profile`
		2. SITL Setup: https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html
			1. Check with the .sim_vehicle.py file and then verify the MAVProxy commands are working or not.
	
5. Gazebo Setup: https://gazebosim.org/docs/garden/install/
6. ArduPilot Gazebo Plugin: https://github.com/ArduPilot/ardupilot_gazebo/blob/main/README.md
	1. refer to the 2nd step and then if the Mavproxy commands are working continue with the installatioon - probably the commands will be working.






# final
1. SITL installations: https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux
	1.  Initial:
			1. `https://github.com/ArduPilot/ardupilot.git` for the main ardupilot repo
			2. `ardupilot/Tools/environment_install/install-prereqs-ubuntu.sh -y`
			3. Reload the path (log-out and log-in to make it permanent):  `. ~/.profile`
			4. 




