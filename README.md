Toon is Eneco's smart thermostat which is mounted on the wall of your living room for example.
It is connected to your boiler and maybe to your electricity and gas meters and maybe even more.
It comes with an Eneco subscription for which you pay a fee unless you use a rooted Toon which is perfectly legal to do.

Toon in fact is a little linux computer which you may like to see performance statistics of and developers may like some controls for.

This is why I developed this Domoticz plugin on my Raspberry Pi ( it may work on other platforms also )

The plugin creates 5 buttons to :

 - Restart Toon
 - Restart Toon GUI
 - Start/Stop vnc ( Toon 1 full and Toon 2 view-only support )
 - Enable/Disable debug logging to /var/log/qt
 - Toggle between '4 Tiles + big Heating tile' and '6 Tiles without big Heating tile'

In 6 Tile mode you can still control your heating by an Android app or maybe my Toon Heating app from https://github.com/JackV2020/toonSmallHeating 
 
The plugin has 12 sensors for 

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
( When already installed it will skip installation and explain it is already installed )

To install the plugin you need to get the contents in your plugin folder :

On a Raspberry Pi you could :

Start a terminal and go to your plugins folder and the next will get it for you into a ToonMonitor folder : 

 ....../plugins$ git clone https://github.com/JackV2020/Domoticz-ToonMonitor.git ToonMonitor

later when you want to check for updates you go into the folder and issue git pull :

 ....../plugins/ToonMonitor$ git pull

After the first time installation you need to enable access to Toon and put a reporting script in place.

You do that on your Domoticz host : ( replace 192.168.2.123 with the address of your Toon )

 - sudo -i
 - ssh-keygen   
    ( and press enter 4 times, no password )
 - ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.2.123
 - rcp /home/pi/domoticz/plugins/ToonMonitor/toon-performance.sh root@192.168.2.123:toon-performance.sh
 - ssh root@192.168.2.123 chmod +x toon-performance.sh
test the script :
 - ssh root@192.168.2.123 ./toon-performance.sh

To get the new plugin in Domoticz you restart your domoticz like :

    sudo systemctl restart domoticz

After this you can add the hardware and you are ready to use it.
The Type name of the plugin is 'Jacks Toon Monitor'.

However, you may want more......which is documented in ToonMonitor.conf and Installing.txt

In ToonMonitor.conf you find how to add/remove/change sensors.
Keep a copy of your changes because an update of the app will overwrite your changes.

In Installing.txt you find how to install VNC on Toon 1/Toon 2 and SFTP on Toon 2 if you want that.
VNC Clients known to work are TigerVNC Viewer on Windows and Linux and bVNC Free on Android.
Other working VNC clients may be available but not all work with Toon.

Thanks for reading and enjoy.
