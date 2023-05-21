Toon is Eneco's smart thermostat which is mounted on the wall of your living room for example.
It is connected to your boiler and maybe to your electricity and gas meters and maybe even more.
It comes with an Eneco subscription for which you pay a fee unless you use a rooted Toon which is perfectly legal to do.

Toon in fact is a little linux computer which you may like to see performance statistics of and developers may like some controls for.
Toon also has some more interesting things you may want to see.

This is why I developed this Domoticz plugin on my Raspberry Pi ( it also runs on pine64 and Synology NAS and maybe on others too )

The plugin creates 6 buttons to :

 - Restart Toon
 - Restart Toon GUI
 - Start/Stop vnc ( Toon 1 full and Toon 2 view-only support )
 - Start/Stop debug logging to /var/log/qt
 - Clean the log file
 - Toggle between '4 Tiles + big Heating tile' and '6 Tiles without big Heating tile'

When you use 6 tiles, the big heating app disappears, I suggest to use my thermostatPlus app from the ToonStore on your Toon to control your heating.
 
The plugin has a lot of  system related sensors like :

 - Toon Uptime
 - GUI Uptime
 - Root  filesystem usage
 - Ramdisk usage
 - Load last minute
 - Load last 5 minutes
 - Load last 15 minutes
 - CPU idle
 - Free memory
 - Network input
 - Network output
 - Wifi strength
 - and many more

The plugin has additional sensors for other things which you could be interested in.
( To remove them from the screen you can disable them in > Setup > Devices and use the 'Set Unused' arrow left from the pencil )

Just to not polute your Domoticz with all the buttons and sensors......
The plugin creates a room with the name you enter for your hardware item and puts everything in that room.

Updates of the sensors are done every 5 minutes.

A remark before installation : Your python installation may need additional plugins.
Check the live logging of your Domoticz where you will see messages from the plugin explaining what is missing.

A module which was missing on pine64 and Synology NAS was the requests module.
On the pine64 it was installed by 'sudo apt-get install python3-requests'.

To install the plugin you need to get the contents in your plugin folder :

On a Raspberry Pi :

Start a terminal and go to your ~/domoticz/plugins folder and the next will get it for you into a ToonMonitor folder : 

 ....../plugins$ git clone https://github.com/JackV2020/Domoticz-ToonMonitor.git ToonMonitor

After the first time installation you need to enable access to Toon and put a reporting script in place.

Details on that are in Installing.txt

To get the new plugin in Domoticz you restart your domoticz like :

    sudo systemctl restart domoticz

After this you can add the hardware and you are ready to use it.
The Type name of the plugin is 'Jacks Toon Monitor'.

However, you may want more ( or less ;-) ) ......which is documented in ToonMonitor.conf and Installing.txt

In ToonMonitor.conf you find how to add/remove/change sensors.

In Installing.txt you find how to install VNC on Toon 1/Toon 2 and SFTP on Toon 2 if you want that.
VNC Clients known to work are TigerVNC Viewer on Windows and Linux and bVNC Free on Android.
Other working VNC clients may be available but not all work with Toon.

Thanks for reading and enjoy.
