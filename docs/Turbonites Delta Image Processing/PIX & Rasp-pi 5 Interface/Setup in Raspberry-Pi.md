### 1. Raspi-config Settings

Before going for anything go to the Raspi-config and follow the below steps:

![[Pasted image 20241011233122.png]]

![[Pasted image 20241011233145.png]]

![[Pasted image 20241011233214.png]]

![[Pasted image 20241011233232.png]]


Then Finish the raspi-config reboot.

### 2. Disable /dev/ttyAMA0

 1. Go to the following config file 
	
	`sudo nano /boot/firmware/config.txt`

2. Then add this line at the end of the file:

```
	dtoverlay=disable-bt
```
	![[Pasted image 20241011233810.png]]
	


### 3. Use a Python Virtual Environment

Create and use a Python virtual environment, which allows you to manage packages independently without affecting the system-wide Python installation.

#### Step-by-Step Instructions:

1. **Ensure `python3-venv` is installed**:
   Install the necessary package to create virtual environments:

   ```bash
   sudo apt install python3-venv 
   ```

2. **Create a virtual environment**:
   Choose a directory for your virtual environment and create it:

   ```bash
   python3 -m venv --system-site-packages Delta_drone
   ```

   This will create a virtual environment in a directory named `myenv` in your home folder.

3. **Activate the virtual environment**:

   ```bash
   source ~/myenv/bin/activate
   ```

   After activation, your terminal prompt will change to show that you are now using the virtual environment.

4. **Install required Python packages** (like `mavproxy`):

   ```bash
   pip install mavproxy
   ```


4. Now make the Connection between the ***PIXHAWK* and *Raspberry-Pi 5***

   ```bash
  mavproxy.py --master=/dev/ttyAMA0 --baudrate 57600 --aircraft MyCopter
   ```

which should give the following output if the connection is sucessfull:

```
WARNING: You should uninstall ModemManager as it conflicts with APM and Pixhawk
Connect /dev/ttyAMA0 source_system=255
no script MyCopter/mavinit.scr
Log Directory: MyCopter/logs/2024-10-12/flight1
Telemetry log: MyCopter/logs/2024-10-12/flight1/flight.tlog
Waiting for heartbeat from /dev/ttyAMA0
MAV> Detected vehicle 1:1 on link 0
online system 1
LOITER> Mode LOITER
fence present
fence enabled
Servo volt 4.3
AP: ArduCopter V4.5.4 (fd1bcc61)
AP: ChibiOS: 6a85082c
AP: Pixhawk1 00260041 31385110 32313330
AP: IOMCU: 410 2003 412FC231
AP: RCOut: PWM:1-14
AP: IMU0: fast sampling enabled 8.0kHz/1.0kHz
AP: Frame: QUAD/X
........
```



> [!NOTE] 
> The Baude Rate of the Connection can create problems even if the installations are proper.




> [!NOTE] links
> - [link1](https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html)



