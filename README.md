This plugin was developed on Raspberry Pi Buster and may work on other platforms.

The plugin creates 3 buttons to :

 - Restart Toon
 - Restart Toon GUI
 - Start/Stop vnc ( Toon 1 only since Toon 2 does not support vnc )
 
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
 - Wifi strength ( Toon 1, I do not know where to get it on a Toon 2 )

The buttons are protected by a password you enter in Domoticz in :

 - > Setup > Settings > Light/Switch Protection: Password.

The plugin also creates a room with the name you enter for your hardware item.

Updates are done every minute.

To install the plugin you need to get the contents of the zip file ToonMonitor.zip

On a Raspberry Pi you could :

Start a terminal and go to your plugins folder and the next command will download a zip file, unpack and remove the zipfile : 

    wget https://raw.githubusercontent.com/JackV2020/Domoticz-ToonMonitor/main/ToonMonitor.zip && unzip ToonMonitor.zip && rm ToonMonitor.zip

After this you need to enable access to Toon and put a reporting script in place.

You do that on your Domoticz host : ( replace 192.168.2.123 with the address of your Toon )

 - sudo -i
 - ssh-keygen   
    ( and press enter 4 times, no password )
 - ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.2.123
 - rcp /home/pi/domoticz/plugins/ToonMonitor/toon-performance.sh root@192.168.2.123:toon-performance.sh
 - ssh root@192.168.2.123 chmod +x toon-performance.sh

The Type name of the plugin is 'Jacks Toon Monitor'.

When you do not like the Type name 'Jacks Toon Monitor' feel free to edit plugin.py and modify it before you actually add your hardware.

Now to get it into Domoticz restart your domoticz like :

    sudo systemctl restart domoticz

After this you can add the hardware and you are all done.

However, you may want more......

In ToonMonitor.conf you find how to add/remove/change sensors.

In Installing.txt you find also how to install VNC on Toon 1 and SFTP on Toon 2 if you want that.
VNC Clients known to work are TigerVNC Viewer on Windows and Linux and bVNC Free on Android.
Other working VNC clients may be available but not all work with Toon 1.

Thanks for reading and enjoy.
