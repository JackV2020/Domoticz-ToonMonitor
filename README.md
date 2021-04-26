This plugin was developed on Raspberry Pi Buster and may work on other platforms.

The plugin creates 4 buttons to :

 - Restart Toon
 - Restart Toon GUI
 - Start/Stop vnc ( Toon 1 full and Toon 2 view-only support )
 - Enable/Disable debug logging to /var/log/qt
 
 and 12 sensors for 

 - Toon Uptime
 - GUI Uptime
 - root  filesystem usage
 - ramdisk usage
 - load last minute
 - load last 5 minutes
 - load last 15 minutes
 - CPU idle
 - free memory
 - network input
 - network output
 - Wifi strength

The plugin creates a room with the name you enter for your hardware item.

The buttons are protected by a password you enter in Domoticz in :

 - > Setup > Settings > Light/Switch Protection: Password.

By going to the Switches menu and editing the switches you can remove the protection.
After a restart of the plugin the protection will not change.

Updates are done every minute.

Before installing make sure that the requests module is installed :
sudo apt-get install python3-requests
( When already installed it will will skip installation and explain it is already installed )

To install the plugin you need to get the contents in your plugin folder :

On a Raspberry Pi you could :

Start a terminal and go to your plugins folder and the next will get it for you : 

 ....../plugins$ git clone https://github.com/JackV2020/Domoticz-ToonMonitor.git

later when you want to check for updates you go into the folder and issue git pull :

 ....../plugins/Domoticz-ToonMonitor$ git pull

After this you need to enable access to Toon and put a reporting script in place.

You do that on your Domoticz host : ( replace 192.168.2.123 with the address of your Toon )

 - sudo -i
 - ssh-keygen   
    ( and press enter 4 times, no password )
 - ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.2.123
 - rcp /home/pi/domoticz/plugins/Domoticz-ToonMonitor/toon-performance.sh root@192.168.2.123:toon-performance.sh
 - ssh root@192.168.2.123 chmod +x toon-performance.sh
test the script :
 - ssh root@192.168.2.123 ./toon-performance.sh

The Type name of the plugin is 'Jacks Toon Monitor'.

When you do not like the Type name 'Jacks Toon Monitor' feel free to edit plugin.py and modify it before you actually add your hardware.

Now to get it into Domoticz restart your domoticz like :

    sudo systemctl restart domoticz

After this you can add the hardware and you are all done.

However, you may want more......

In ToonMonitor.conf you find how to add/remove/change sensors.

In Installing.txt you find also how to install VNC on Toon 1/Toon 2 and SFTP on Toon 2 if you want that.
VNC Clients known to work are TigerVNC Viewer on Windows and Linux and bVNC Free on Android.
Other working VNC clients may be available but not all work with Toon.

Thanks for reading and enjoy.