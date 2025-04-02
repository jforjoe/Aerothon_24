### >> Set an ip address for ethernet connection

`sudo ip addr add 192.168.1.100/24 dev eth0`

>To Set Static Ethernet IP address
> https://www.instructables.com/Configuring-the-Raspberry-Pi-ethernet-port-for-rem/



### >> List and Change the Wifi through teminal

`sudo iwlist wlan0 scan`


### >> Remove the SSID of the Connected Wifi list

- `sudo nmtui`
	- edit connections
	- select the required wifi name and then delete


