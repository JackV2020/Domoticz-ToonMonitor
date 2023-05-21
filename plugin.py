#
# Changelog:
#
# version 2.0.1 : Toon 1 had no /qmf/www/tsc folder so hyperlink did not work
#                 when logging is enabled, restart of Toon/GUI does not initialise log but appends
# version 2.0.0 : revised all coding
#                 added parameter to select Toon type
#                 cleared button names so now only last action is shown on button, much cleaner
#                 added 'Clear Log' button
#                 'Start/Stop Log' button now enables/disables to see logging on http://Toon/tsc/qt
#                 'Start/Stop Log' button has url you can click to go to http://Toon/tsc/qt
#                 removed default button protection, you can put protection on it yourself isn't it
#                 no more errors when Toon is powered off or when someone deleted devices from Domoticz in stead of from config file.
#                 added all sensors from /happ_thermstat?action=getThermostatInfo and /happ_pwrusage?action=GetCurrentUsage in config file.
#                 added some new icons
#                 reviewed authentication mechanism due to an 'undocumented feature' in Domoticz ( https://www.domoticz.com/forum/viewtopic.php?f=28&t=36334 )
# version 1.5.2 : remove Toon 2 sensors when changing Hardware from Toon 2 IP address to Toon 1 IP address
# version 1.5.1 : previous version did not put temperature in the room for Toon 1
# version 1.5.0 : get temperature and for Toon 2 sensor data from http://Toon2/tsc/sensors ( temperature, humidity, eco2, tvoc and light intensity)
# version 1.4.0 : get domoticz http IP port from running process named domoticz (when there is no /etc/init.d/domoticz.sh like on Raspberry Pi)
# version 1.3.0 : added button for 4-6 tile mode
# version 1.2.0 : added button to start/stop Logging
# version 1.1.0 : added buttons to restart Toon, Gui and start/stop VNC
# version 1.0.0 : initial version
#
"""
<plugin key="JacksToonMonitor" name="Jacks Toon Monitor" author="Jack Veraart" version="2.0.1">
    <description>
        <font size="4" color="white">Toon Monitor </font><font color="white">...Notes...</font>
        <ul style="list-style-type:square">
            <li><font color="cyan"><b>After reading the text below FIRST follow the instructions in the file Installing.txt to implement access to Toon and enable reporting.</b></font></li>
            <li><font color="yellow">A room with the name you give in the Name field above  will be created to hold all sensors and buttons .</font></li>
            <li><font color="yellow">In that room will be more than 30 sensors and 6 buttons for 'Restart Toon' , 'Restart GUI', 'Start/Stop vnc', 'Start/Stop Log','Clear Log' and '4 Tile / 6 Tile' mode.</font></li>
            <ul style="list-style-type:circle">
                <li><font color="yellow">When started, logging goes to /var/log/qt which will be removed after a reboot or by you manually. Logging stays active after a reboot unless you stop it again.</font></li>
                <li><font color="yellow">In your Toon app you can write to the log using : console.log("MyApp: this line is a test" + variable)</font></li>
                <li><font color="yellow">ssh to your Toon and follow your logging by 'tail -f /var/log/qt | grep MyApp'.</font></li>
                <li><font color="yellow">You can also see the log by clicking the url 'http://"Toon"/tsc/qt' in the 'Start/Stop Log' button. (Ignore json message, click Raw Data tab)</font></li>
                <li><font color="yellow">'4 Tile' is standard mode. In '6 Tile' there is no big Heating tile and you need to use an Android app or something else to control your heating.</font></li>
                <li><font color="yellow">Maybe use my 1 tile heating app for Toon 1/2 from... <a href="https://github.com/JackV2020/toonSmallHeating"><font color="cyan">https://github.com/JackV2020/toonSmallHeating</font></a> ...which may go to the ToonStore.</font></li>
                <li><font color="cyan">If you want vnc on Toon 1/2 (on Toon 2 vnc is view-only) or add sftp on Toon 2 you may use additional instructions in Installing.txt.</font></li>
            </ul>
            <li><font color="yellow">Below you specify the Toon IP address. Find it on your Toon : click upper left corner > Instellingen/Settings > Internet.</font></li>
            <li><font color="yellow">This plugin needs Admin rights so if you have accounts you need one of the next: </font></li>
            <ul style="list-style-type:circle">
                <li><font color="yellow">add Admin account details below and restart plugin.</font></li>
                <li><font color="yellow">add 127.0.0.1 to > Setup > Settings > System > 'Local Networks (no username/password):' and restart Domoticz.</font></li>
            </ul>
            <li><font color="cyan">Remember, after startup you can use notifications on the sensors to be informed by mail etc.</font></li>
            <li><font color="cyan">You can also use timers to control the switches. Maybe at midnight : disable logging followed by a reboot of your Toon.</font></li>
            <li><font color="yellow">To develop your own plugin...check this web site... <a href="https://www.domoticz.com/wiki/Developing_a_Python_plugin" ><font color="cyan">Developing_a_Python_plugin</font></a></font></li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Toon IP Address." width="120px" default="192.168.2.19"/>

        <param field="Mode5" label="Toon Type."         width="130px">
            <options>
                <option label="Toon 1" value="Toon1"    default="true"/>
                <option label="Toon 2" value="Toon2"/>
            </options>
        </param>

        <param field="Username" label="Username."       width="120px" default=""/>

        <param field="Password" label="Password."       width="120px" default="" password="true"/>

        <param field="Mode6" label="Debug."             width="75px">
            <options>
                <option label="True"  value="Debug"/>
                <option label="False" value="Normal"    default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz

# Prepare some global variables

StartupOK=0

HeartbeatInterval=10  # 10 seconds is limit to avoid broken thread notifications
#HeartbeatCounterMax = 6 # Only every 'HeartbeatCounterMax * HeartbeatInterval' seconds there is a real update.
HeartbeatCounterMax = 30 # Only every 'HeartbeatCounterMax * HeartbeatInterval' seconds there is a real update.
HeartbeatCounter = 0

ToonAddress=''  # plugin parameter
Username=''     # plugin parameter 
Password=''     # plugin parameter 
RoomName=''     # plugin parmater ( The name you gave to your hardware )

HomeFolder=''   # plugin finds right value
HTTPPort=''        # plugin finds right value
IPAddress=''        # plugin finds right value

Button_Type='0' # 0: Buttons 1: Drop Down menu

Toon1=False     # plugin looks for http://ToonAddress/tsc/sensors which is missing on a Toon 1
Toon2=False     # plugin looks for http://ToonAddress/tsc/sensors which is missing on a Toon 1

DeviceLibrary={}    # devices as created in the configuration file

# Some standard buttons

RestartToonId=0
RestartToonName='Leave the next line in place so there is no disturbing name on the button'
RestartToonName=''
RestartToonLabel='Restart Toon'
RestartToonImage='Toon'
RestartToonDescription='Restart Toon'

RestartGUIId=0
RestartGUIName='Leave the next line in place so there is no disturbing name on the button'
RestartGUIName=''
RestartGUILabel='Restart GUI'
RestartGUIImage='Toon'
RestartGUIDescription='Restart GUI'

VNCId=0
VNCName='Leave the next line in place so there is no disturbing name on the button'
VNCName=''
VNCLabels='Start VNC|Stop VNC'
VNCImage='JVx11vnc'
VNCDescription='Start VNC and Stop VNC'

LogId=0
LogName='Change here has no result because it gets set after Toon adress is found in onStart'
LogLabels='Start Log|Stop Log'
LogImage='JVLogFile'
LogDescription='Change here has no result because it gets set after Toon adress is found in onStart'

ClearLogId=0
ClearLogName='Leave the next line in place so there is no disturbing name on the button'
ClearLogName=''
ClearLogLabel='Clear Log'
ClearLogImage='JVLogFile'
ClearLogDescription='Clear the log but does not enable/disable logging'

Mode46Id=0
Mode46Name='Leave the next line in place so there is no disturbing name on the button'
Mode46Name=''
Mode46Labels='4 Tiles|6 Tiles'
Mode46Image='JV46'
Mode46Description='4 Tiles with big Heating or 6 Tiles'

class BasePlugin:
    enabled = False
    def __init__(self):

        return

# --------------------------------------------------------------------------------------------------------------------------------------------------------

    def onStart(self):

        global StartupOK
        
        global HeartbeatInterval
        global HomeFolder
        global Username
        global Password
        global RoomName
        global ToonAddress
        
        global Toon1
        global Toon2

        global IPAddress
        global HTTPPort

        global LogDescription
        global LogName

        self.pollinterval = HeartbeatInterval  #Time in seconds between two polls

        if Parameters["Mode6"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)

        Domoticz.Log("onStart called")
        try:
#
# Set some globals variables to right values
#            
            
            ToonAddress     =str(Parameters["Address"])

            LogDescription = 'Start and Stop Log to /var/log/qt + enable / disable http://'+ToonAddress+'/tsc/qt'
            LogName        = '<marquee behavior="slide" direction="left"><font color="red"><b>></b></font><a href="http://'+ToonAddress+'/tsc/qt" style="color: #000000" target="_blank">http://"Toon"/tsc/qt</a><font color="red"><b><</b></font></marquee>'

            HomeFolder      =str(Parameters["HomeFolder"])
            Username        =str(Parameters["Username"])
            Password        =str(Parameters["Password"])
            RoomName        =str(Parameters['Name'])

#            IPAddress         =GetDomoticzIPAddress() # Not used at this moment due to authentication 'feature'. See Changelog 2.0.0 last remark.
            IPAddress         = '127.0.0.1'
            HTTPPort          =GetDomoticzHTTPPort()            
#
# ----- Start code due to added parameter for Toon type
#
# I found out I can not determine Toon type when Toon is down, duhh, and that I needed an extra parameter for the type of Toon
#
            if (str(Parameters["Mode5"]) not in ['Toon1','Toon2']):
                Domoticz.Log('>>>>>> Please select Toon type in the plugin settings page')
                Domoticz.Log(">>>>>> Calling GetToonData('Toon2Sensors') to try to find out if this is a Toon 1 or 2")
                Toon2 = ( str(GetToonData('Toon2Sensors')) != "{}" )
                Toon1 = not Toon2
            else:
                Toon1 = str(Parameters["Mode5"]) == 'Toon1'
                Toon2 = str(Parameters["Mode5"]) == 'Toon2'
#
# In a future version from the code above only the last 2 lines come back resulting in :
#
#           Toon1 = str(Parameters["Mode5"]) == 'Toon1'
#           Toon2 = str(Parameters["Mode5"]) == 'Toon2'
#
# ----- End code due to added parameter
#
            StartupOK = ImportImages()

# Create devices as configured in ToonMonitor.conf

            if StartupOK == 1:
            
                StartupOK = CreateDevices()
            
            if StartupOK == 1:
                
                Domoticz.Log('onStartup OK')

                Domoticz.Heartbeat(HeartbeatInterval)

            else:
                
                Domoticz.Log('ERROR starting up')
            
        except:

            StartupOK = 0

            Domoticz.Log('ERROR starting up')

# --------------------------------------------------------------------------------------------------------------------------------------------------------

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")
# --------------------------------------------------------------------------------------------------------------------------------------------------------

    def onCommand(self, Unit, Command, Level, Hue):

        try:
            import subprocess
        except:
            Domoticz.Log("python3 is missing module subprocess")

        Domoticz.Log("onCommand called for " + Devices[Unit].Name)

        command='/usr/bin/ssh  -o ConnectionAttempts=3 -o ConnectTimeout=3 -o BatchMode=yes ' + ToonAddress + ' '

        if Unit == RestartToonId:
            command=command + ' /sbin/init 6'

        if Unit == RestartGUIId:
            command=command + ' /usr/bin/killall qt-gui'

        if Unit == VNCId and Level == 10 :
            command=command + ' "if uname -a | grep armv5 ; then /usr/bin/x11vnc ; else x11vnc -forever -shared -rawfb map:/dev/fb0@1024x600x32 -usepw -pipeinput UINPUT:touch,touch_always=1,abs,pressure=128,direct_abs=/dev/input/event0,direct_btn=/dev/input/event0,direct_rel=/devinput/event0,direct_key=/dev/input/event0,nouinput ; fi"'

        if Unit == VNCId and Level == 20 :
            command=command + ' "if uname -a | grep armv5 ; then /usr/bin/killall x11vnc-bin ; else /usr/bin/killall x11vnc ; fi"'

        if Unit == LogId and Level == 10 :
            command=command + ' "sed -i ' + chr(39) + 's#startqt >/dev/null#startqt >>/var/log/qt#' + chr(39) + ' /etc/inittab ; /sbin/init q ; /usr/bin/killall qt-gui ; mkdir /qmf/www/tsc ; ln -s /var/log/qt /qmf/www/tsc/qt"'

        if Unit == LogId and Level == 20 :
            command=command + ' "sed -i ' + chr(39) + 's#startqt >>/var/log/qt#startqt >/dev/null#' + chr(39) + ' /etc/inittab ; /sbin/init q ; /usr/bin/killall qt-gui; rm /qmf/www/tsc/qt" '

        if Unit == ClearLogId:
# this command will only restart gui if logging is active
#            command=command + ' "rm /var/log/qt ; if grep -e "/var/log/qt" /etc/inittab > /dev/null; then /usr/bin/killall qt-gui ;fi" '
# this command restarts gui when logging is running or not, not needed when logging is inactive but shows same behaviour on Toon
            command=command + ' "rm /var/log/qt ; /usr/bin/killall qt-gui" '

        if Unit == Mode46Id and Level == 10 :
            command=command + ' "sed -i ' + chr(39) + 's#<feature>noHeating</feature>##' + chr(39) + ' /qmf/config/config_happ_scsync.xml && /sbin/init 6 &"'

        if Unit == Mode46Id and Level == 20 :
            command=command + ' "sed -i ' + chr(39) + 's#<features>#<features><feature>noHeating</feature>#' + chr(39) + ' /qmf/config/config_happ_scsync.xml && /sbin/init 6 &"'

        Domoticz.Log('onCommand command : '+command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        Devices[Unit].Update(  nValue=0, sValue=str(Level))

# --------------------------------------------------------------------------------------------------------------------------------------------------------
        
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
            
# --------------------------------------------------------------------------------------------------------------------------------------------------------

    def onHeartbeat(self):

        global HeartbeatCounter
        
        if StartupOK != 1 :
            
            Domoticz.Log("onHeartbeat something wrong during startup")
        
        else:
                      
            Domoticz.Debug("onHeartbeat called Heartbeat: " + str(HeartbeatCounter))

            if HeartbeatCounter == 0:

# first get the values from the report script

                ReportValues = {}
                ReportValues = GetToonData('ReportValues')

                if (str(ReportValues) == "{}" ) :
                    Domoticz.Log('Report Info not available')

                for field in ReportValues :
                    
                    for Device in DeviceLibrary :
                        if ( field == str(DeviceLibrary[Device]['Field']) ) :

                            UpdateValue = ReportValues[field]

                            if (int(DeviceLibrary[Device]['Factor']) != 0 ): 
                                UpdateValue = str(round(float(UpdateValue) / float(DeviceLibrary[Device]['Factor']),int(DeviceLibrary[Device]['Decimals'])))

                            UpdateUnit = int(DeviceLibrary[Device]['Unit'])

                            try:
                                Devices[UpdateUnit].Update(  nValue=0, sValue=UpdateValue)
                            except:
                                Domoticz.Log('No target sensor for : '+DeviceLibrary[Device]['Name'])

# next get all thermostat info

                ThermostatInfo = {}
                ThermostatInfo = GetToonData('ThermostatInfo')

                if (str(ThermostatInfo) == '{}'):
                    Domoticz.Log('Thermostat Info not available')

                for field in ThermostatInfo :
                    
                    for Device in DeviceLibrary :
                        if ( field == str(DeviceLibrary[Device]['Field']) ) :

                            UpdateValue = str(ThermostatInfo[field])

                            if (int(DeviceLibrary[Device]['Factor']) != 0 ): 
                                UpdateValue = str(round(float(UpdateValue) / float(DeviceLibrary[Device]['Factor']),int(DeviceLibrary[Device]['Decimals'])))

                            UpdateUnit = int(DeviceLibrary[Device]['Unit'])

                            try:
                                Devices[UpdateUnit].Update(  nValue=0, sValue=UpdateValue)
                            except:
                                Domoticz.Log('No target sensor for : '+DeviceLibrary[Device]['Name'])

# next get all usage figures
                    
                UsageInfo = {}
                UsageInfo = GetToonData('Usage')
                
                if (str(UsageInfo) == '{}'):
                    Domoticz.Log('Usage Info not available')

                for field in UsageInfo :
                    
                    for Device in DeviceLibrary :
                        if ( field == str(DeviceLibrary[Device]['Field']) ) :

                            UpdateValue = str(UsageInfo[field])

                            if (int(DeviceLibrary[Device]['Factor']) != 0 ): 
                                UpdateValue = str(round(float(UpdateValue) / float(DeviceLibrary[Device]['Factor']),int(DeviceLibrary[Device]['Decimals'])))

                            UpdateUnit = int(DeviceLibrary[Device]['Unit'])

                            try:
                                Devices[UpdateUnit].Update(  nValue=0, sValue=UpdateValue)
                            except:
                                Domoticz.Log('No target sensor for : '+DeviceLibrary[Device]['Name'])

# get sensor values for Toon 2 devices

                if (Toon2):
                    ToonSensors = {}
                    ToonSensors = GetToonData('Toon2Sensors')

                    if (str(ToonSensors) == '{}'):
                        Domoticz.Log('Toon2Sensors Info not available')
                        
                    for field in ToonSensors :
                        
                        for Device in DeviceLibrary :
                            if ( field == str(DeviceLibrary[Device]['Field']) ) :

                                UpdateValue = str(ToonSensors[field])
                                
                                if (int(DeviceLibrary[Device]['Factor']) != 0 ): 
                                    UpdateValue = str(round(float(UpdateValue) / float(DeviceLibrary[Device]['Factor']),int(DeviceLibrary[Device]['Decimals'])))

                                UpdateUnit = int(DeviceLibrary[Device]['Unit'])

                                try:
                                    Devices[UpdateUnit].Update(  nValue=0, sValue=UpdateValue)
                                except:
                                    Domoticz.Log('No target sensor for : '+DeviceLibrary[Device]['Name'])
                        
                
                HeartbeatCounter = HeartbeatCounterMax

            else:
                HeartbeatCounter = HeartbeatCounter - 1
            
# --------------------------------------------------------------------------------------------------------------------------------------------------------

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------  Image Management Routines  -----------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def GetDomoticzIPAddress():

# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

    try:
        import socket
    except:
        Domoticz.Log("python3 is missing module socket")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IPAddress = s.getsockname()[0]  # this results in an entry in the Database in UserSettings with address like 192.168.27.23
    except Exception:
        IPAddress = '127.0.0.1'
    finally:
        s.close()

    return IPAddress

# --------------------------------------------------------------------------------------------------------------------------------------------------------

def GetDomoticzHTTPPort():

    try:
        import subprocess
    except:
        Domoticz.Log("python3 is missing module subprocess")
        
    try:
        import time
    except:
        Domoticz.Log("python3 is missing module time")
    
    try:
        Domoticz.Debug('GetDomoticzHTTPPort check startup file')
        pathpart=Parameters['HomeFolder'].split('/')[3]
        searchfile = open("/etc/init.d/"+pathpart+".sh", "r")
        for line in searchfile:
            if ("-www" in line) and (line[0:11]=='DAEMON_ARGS'): 
                HTTPPort=str(line.split(' ')[2].split('"')[0])
        searchfile.close()
        Domoticz.Debug('GetDomoticzHTTPPort looked in: '+"/etc/init.d/"+pathpart+".sh"+' and found port: '+HTTPPort)
    except:
        Domoticz.Debug('GetDomoticzHTTPPort check running process')
        command='ps -ef | grep domoticz | grep sslwww | grep -v grep | tr -s " "'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        timeouts=0

        result = ''
        while timeouts < 10:
            p_status = process.wait()
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:                        
                HTTPPort=str(output)
                HTTPPort = HTTPPort[HTTPPort.find('-www'):]
                HTTPPort = HTTPPort[HTTPPort.find(' ')+1:]
                HTTPPort = HTTPPort[:HTTPPort.find(' ')]
            else:
                time.sleep(0.2)
                timeouts=timeouts+1
        Domoticz.Debug('GetDomoticzHTTPPort looked at running process and found port: '+HTTPPort)
    
    return HTTPPort

# --------------------------------------------------------------------------------------------------------------------------------------------------------

def GetImageDictionary():

    try :
        import json
    except:
        Domoticz.Log("python3 is missing module json")
    
    try:
        import requests
    except:
        Domoticz.Log("python3 is missing module requests")

    try:
        mydict={}

        url='http://'+IPAddress+':'+HTTPPort+'/json.htm?type=custom_light_icons'
        
        Domoticz.Debug('GetImageDictionary '+url+'....'+Username+'....'+Password+'....')

        response=requests.get(url, auth=(Username, Password))
#        response=requests.get(url)
        data = json.loads(response.text)
        
        for Item in data['result']:
            mydict[str(Item['imageSrc'])]=int(Item['idx'])

    except:
        mydict={}

#    Domoticz.Log('GetImageDictionary '+str(mydict))
    
    return mydict

# --------------------------------------------------------------------------------------------------------------------------------------------------------

def ImportImages():
#
# Import ImagesToImport if not already loaded
#
    try :
        import glob
    except:
        Domoticz.Log("python3 is missing module glob")

    global ImageDictionary
    
    MyStatus=1
    
    ImageDictionary=GetImageDictionary()
    
    if ImageDictionary == {}:
        Domoticz.Log("Please modify your setup to have Admin access. (See Hardware setup page of this plugin.)")      
        MyStatus = 0
    else:

        for zipfile in glob.glob(HomeFolder+"CustomIcons/*.zip"):
            importfile=zipfile.replace(HomeFolder,'')
            try:
                Domoticz.Image(importfile).Create()
                Domoticz.Debug("ImportImages Imported/Updated icons from "  + importfile)
            except:
                MyStatus = 0
                Domoticz.Log("ImportImages ERROR can not import icons from "  + importfile)

        if (MyStatus == 1) : 
            ImageDictionary=GetImageDictionary()
            Domoticz.Log('ImportImages Oke')

    return MyStatus
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------  Device Creation Routines  ------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateDevice(deviceunit,devicename,devicetype,devicelogo="",devicedescription="",sAxis="",InitialValue=0.0):

    MyStatus = 1
    
    if deviceunit not in Devices:


        if ImageDictionary == {}:
            MyStatus = 0
            firstimage=0
            firstimagename='NoImage'
            Domoticz.Log("CreateDevice ERROR I can not access the image library. Please modify the hardware setup to have the right Username and Password.")      
        else:
            firstimage=int(str(ImageDictionary.values()).split()[0].split('[')[1][:-1])
            firstimagename=str(ImageDictionary.keys()).split()[0].split('[')[1][1:-2]

        if firstimage != 0: # we have a dictionary with images and hopefully also the image for devicelogo

            try:
                Domoticz.Debug("CreateDevice " + devicename)
                deviceoptions={}
                deviceoptions['Custom']="1;"+sAxis
                Domoticz.Device(Name=devicename, Unit=deviceunit, TypeName=devicetype, Used=1, Image=ImageDictionary[devicelogo], Description=devicedescription).Create()
                Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=str(InitialValue))
                Domoticz.Log("Created device : " + devicename + " with '"+ devicelogo + "' icon and options "+str(deviceoptions)+' Value '+str(InitialValue))
            except:

# when devicelogo does not exist, use the first image found, (TypeName values Text and maybe some others will use standard images for that TypeName.)

                try:
                    Domoticz.Debug("CreateDevice " + devicename)
                    Domoticz.Device(Name=devicename, Unit=deviceunit, TypeName=devicetype, Used=1, Image=firstimage, Description=devicedescription).Create()
                    Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=str(InitialValue))
                    Domoticz.Log("Created device : " + devicename+ " with '"+ firstimagename + "' icon and Value "+str(InitialValue))
                except:
                    MyStatus = 0
                    Domoticz.Log("CreateDevice ERROR Could not create device : " + devicename)
#
# The next puts the right name, axis, image and description in the device
#
    try:
        NewName = devicename
        Domoticz.Debug('CreateDevice Update settings for: '+NewName+' "'+ devicedescription+'"')
        deviceoptions={}
        deviceoptions['Custom']="1;"+sAxis
        Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=Devices[deviceunit].sValue, Name=NewName, Options=deviceoptions, Image=ImageDictionary[devicelogo], Description=devicedescription)
        Domoticz.Debug("CreateDevice Updated "+NewName)
    except:
        MyStatus = 0
        Domoticz.Log("ERROR CreateDevice Update Failed for : "+devicename+' "'+ devicedescription+'"')

    return MyStatus
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateSelectorSwitch(deviceunit,devicename,devicebuttons,devicelogo="",devicedescription="",SelectorStyle=0):
#
# Create a selector switch devicebuttons format : button1|.....|buttonx
#
    MyStatus = 1
    
    if deviceunit not in Devices:

        firstLevelName=devicebuttons.split('|')[0]
        Domoticz.Debug('First Level: '+firstLevelName)

        if (SelectorStyle == 0): 
            Options = {'LevelActions': '|'*(devicebuttons.count('|')+1),
                             'LevelNames': firstLevelName+'|'+devicebuttons,
                             'LevelOffHidden': 'true',
                             'SelectorStyle': '0'}
        else:
            Options = {'LevelActions': '|'*(devicebuttons.count('|')+1),
                             'LevelNames': firstLevelName+'|'+devicebuttons,
                             'LevelOffHidden': 'true',
                             'SelectorStyle': '1'}
        try:
            Domoticz.Device(Name=devicename, Unit=deviceunit, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary[devicelogo], Options=Options, Used=1,Description=devicedescription).Create()
            Domoticz.Log("Created device : " + devicename +' '+ devicedescription + " with '"+ devicelogo + "' icon and options "+str(Options))
        except:
            MyStatus = 0
            Domoticz.Log("ERROR Could not create selector switch : " + devicename)
#
# Devices are created with as prefix the name of the Hardware device as you named it during adding your hardware
# The next replaces that prefix, also after every restart so names are fixed
#
    try:
#        NewName = '<center>'+devicename+'</center>'
        NewName = devicename

        index=int(Devices[deviceunit].nValue/10)-1
        firstLevelName=devicebuttons.split('|')[index]
#        Domoticz.Log('...'+devicebuttons+'...'+str(index)+'...'+firstLevelName)

        if (SelectorStyle == 0): 
            Options = {'LevelActions': '|'*(devicebuttons.count('|')+1),
                             'LevelNames': firstLevelName+'|'+devicebuttons,
                             'LevelOffHidden': 'true',
                             'SelectorStyle': '0'}
        else:
            Options = {'LevelActions': '|'*(devicebuttons.count('|')+1),
                             'LevelNames': firstLevelName+'|'+devicebuttons,
                             'LevelOffHidden': 'true',
                             'SelectorStyle': '1'}
        Domoticz.Debug('CreateSelectorSwitch Update settings for: '+NewName+' "'+ devicedescription+'"')
        Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=Devices[deviceunit].sValue, Name=NewName, Image=ImageDictionary[devicelogo], Options=Options, Description=devicedescription)

    except:
        MyStatus = 0
        Domoticz.Log("ERROR CreateSelectorSwitch Update Failed for : "+devicename+' "'+ devicedescription+'"')

    return MyStatus
#---------------------------------------------------------------------------------------------------------------------------

def CreateDevices():

    try:
        import time
    except:
        Domoticz.Log("python3 is missing module time")

    global DeviceLibrary
    global RestartToonId
    global RestartGUIId
    global VNCId
    global LogId
    global ClearLogId
    global Mode46Id
    
    DeviceLibrary={}
    Name=''
    Image=''
    Field=''
    Units=''
    Description=''
    MyStatus=1
    ConfigFile='ToonMonitor.conf'
#
# Suppose there are no changes for the Room, even when not created yet
#    
    Recreate = False

    try:
        
        ToonType = '0'
        Factor   = '0'
        Decimals = '0'
        
        TheConfigFile=open(HomeFolder+ConfigFile, "r")
        TheConfigFile.close
        for Line in TheConfigFile:

            if Line[0] not in ['#', ' ', '\t', '\n' ] and Line.replace(' ','').replace('\t','') != '\n':    # skip comments and empty lines
                
                Line=Line.replace('\n','')                  # remove EOL

                if Line.split('=')[0] == 'Name':
                    Name = Line.split('=')[1]
                elif Line.split('=')[0] == 'Description':
                    Description = Line.split('=')[1]
                elif Line.split('=')[0] == 'Image':
                    Image = Line.split('=')[1]
                elif Line.split('=')[0] == 'Field':
                    Field = Line.split('=')[1]
                elif Line.split('=')[0] == 'ToonType':
                    ToonType = Line.split('=')[1]
                elif Line.split('=')[0] == 'Factor':
                    Factor = Line.split('=')[1]
                elif Line.split('=')[0] == 'Decimals':
                    Decimals = Line.split('=')[1]
                elif Line.split('=')[0] == 'Units':
                    Units = Line.split('=')[1]
                elif Line.split('=')[0] == 'EndDevice':
                    if (
                       ( ToonType == '0')
                    or ( ToonType == '1' and Toon1 )
                    or ( ToonType == '2' and Toon2 )
                    ):
                        DeviceEntry={}
                        DeviceEntry['Name']         = Name
                        DeviceEntry['Description']  = Description
                        DeviceEntry['Image']        = Image
                        DeviceEntry['Field']        = Field
                        DeviceEntry['ToonType']     = ToonType
                        DeviceEntry['Factor']       = Factor
                        DeviceEntry['Decimals']     = Decimals
                        DeviceEntry['Units']        = Units
                        DeviceEntry['Unit']         = -1
                        DeviceLibrary[Name]         = DeviceEntry
                    ToonType = '0'
                    Factor   = '0'
                    Decimals = '0'
#                    Domoticz.Log("Device: "+str(DeviceEntry))
                else:
                    Domoticz.Log('Error Line: '+Line)
                    MyStatus=-1
        Domoticz.Log('CreateDevices Read config file: '+HomeFolder+ConfigFile)
    except:
        MyStatus=-1
        Domoticz.Log('CreateDevices Error opening config file: '+HomeFolder+ConfigFile)


    if MyStatus == 1:

# ------- check which devices already exist by updating the unit field
        
        UnitsToKeep = {}
        for Unit in Devices:
            if Devices[Unit].Name in DeviceLibrary:
                DeviceLibrary[Devices[Unit].Name]['Unit'] = Unit
                UnitsToKeep[Unit] = Unit

# ------- make sure all devices from the config file are there

        Domoticz.Log('CreateDevices create/update devices')

        for Device in DeviceLibrary:
        
            Unit=DeviceLibrary[Device]['Unit']
#
# When the device does not have a unit number yet we have to create it and find a free number
#
            if ( Unit == -1):
                Recreate = True
                Unit = 1
                while Unit in Devices:
                    Unit = Unit + 1
                DeviceLibrary[Device]['Unit'] = Unit
            UnitsToKeep[Unit] = Unit

            Domoticz.Debug('Create/update '+str(Device))

            DeviceName=DeviceLibrary[Device]['Name']
            DeviceImage=DeviceLibrary[Device]['Image']
            DeviceDescription=DeviceLibrary[Device]['Description']
            Units=DeviceLibrary[Device]['Units']
#
# The next call creates the device and when it does exist it will update parameters if needed.
#
            if (MyStatus == 1):
                MyStatus = CreateDevice(Unit,DeviceName,"Custom",DeviceImage,DeviceDescription,Units,0)

        Domoticz.Log('CreateDevices create/update buttons')
#
# Create/Update Restart Toon Button
#
        for Unit in Devices:
            if Devices[Unit].Description == RestartToonDescription :
                RestartToonId=Unit
                UnitsToKeep[Unit] = Unit

        if RestartToonId == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            RestartToonId=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(RestartToonId,RestartToonName,RestartToonLabel,RestartToonImage,RestartToonDescription,0)
#
# Create Restart GUI Button
#
        for Unit in Devices:
            if Devices[Unit].Description == RestartGUIDescription :
                RestartGUIId=Unit
                UnitsToKeep[Unit] = Unit

        if RestartGUIId == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            RestartGUIId=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(RestartGUIId,RestartGUIName,RestartGUILabel,RestartGUIImage,RestartGUIDescription,0)
#
# Create Restart VNC Button
#
        for Unit in Devices:
            if Devices[Unit].Description == VNCDescription :
                VNCId=Unit
                UnitsToKeep[Unit] = Unit

        if VNCId == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            VNCId=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(VNCId,VNCName,VNCLabels,VNCImage,VNCDescription,0)
#
# Create Log Button
#
        for Unit in Devices:
            if Devices[Unit].Description == LogDescription :
                LogId=Unit
                UnitsToKeep[Unit] = Unit

        if LogId == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            LogId=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(LogId,LogName,LogLabels,LogImage,LogDescription,0)
#
# Create ClearLog Button
#
        for Unit in Devices:
            if Devices[Unit].Description == ClearLogDescription :
                ClearLogId=Unit
                UnitsToKeep[Unit] = Unit

        if ClearLogId == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            ClearLogId=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(ClearLogId,ClearLogName,ClearLogLabel,ClearLogImage,ClearLogDescription,0)
#
# Create Mode Button
#
        for Unit in Devices:
            if Devices[Unit].Description == Mode46Description :
                Mode46Id=Unit
                UnitsToKeep[Unit] = Unit

        if Mode46Id == 0:
            Recreate = True
            Unit = 1
            while Unit in Devices:
                Unit = Unit + 1
            Mode46Id=Unit
            UnitsToKeep[Unit] = Unit

        CreateSelectorSwitch(Mode46Id,Mode46Name,Mode46Labels,Mode46Image,Mode46Description,0)

# --------- start delete loop for devices we do not need anymore 

        Domoticz.Log('CreateDevices delete obsolete devices')

        DeleteOne=1
        while DeleteOne == 1: # My implementation of repeat until, make sure to get into the loop and immediately make sure to get out of it
            DeleteOne = 0

            for Unit in Devices: # inner loop to find what to delete
#                if ( not Devices[Unit].Name in DeviceLibrary and not Devices[Unit].Name in [ RestartToonName, RestartGUIName, VNCName, LogName, Mode46Name ] ) :
                if ( not Unit in UnitsToKeep ) :
                    DeleteOne = 1            # stay in the loop because we may have to do our thing again
                    UnitToDelete = Unit
                    Description=Devices[Unit].Description

            if DeleteOne == 1: # out of the inner loop it is safe to delete
                Domoticz.Log('.....')
                Domoticz.Log('.....Delete  my own device:  **'+Description+'**  Unit: **'+str(UnitToDelete)+'**')
                Devices[UnitToDelete].Delete()
                Domoticz.Log('.....Deleted my own device:  **'+Description+'**  Unit: **'+str(UnitToDelete)+'**')

# ------- end delete loop

        Domoticz.Log('CreateDevices create/update room')
#
# (Re-)Create Room
#
        RoomIdx=CreateRoom( RoomName, Recreate)
        if (RoomIdx == 0):
            MyStatus = 0
#
# Add all items from configuration file to Room if not already in
#
# Note that the order in the config file determines the order in the room
#
        if (MyStatus == 1):

            Domoticz.Log('CreateDevices put devices in room')

            for Device in DeviceLibrary:
                Addition = AddToRoom(RoomIdx,Devices[DeviceLibrary[Device]['Unit']].ID)
                if (Addition == 0):
                    MyStatus = 0
#
# Add the buttons to the Room
#
        if (MyStatus == 1):

            Domoticz.Log('CreateDevices put switches in room')

            AddToRoom(RoomIdx,Devices[RestartToonId].ID)
            AddToRoom(RoomIdx,Devices[RestartGUIId].ID)
            AddToRoom(RoomIdx,Devices[VNCId].ID)
            AddToRoom(RoomIdx,Devices[LogId].ID)
            AddToRoom(RoomIdx,Devices[ClearLogId].ID)
            AddToRoom(RoomIdx,Devices[Mode46Id].ID)

    return MyStatus
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateRoom(RoomName, Recreate):

    try:
        import json
    except:
        Domoticz.Log("python3 is missing module json")
        
    try:
        import requests
    except:
        Domoticz.Log("python3 is missing module requests")
    
    idx=0

    try:

        Domoticz.Debug('Check if Room Exists')
        
        url='http://'+IPAddress+':'+HTTPPort+'/json.htm?type=plans&order=name&used=true'
        Domoticz.Debug('Check Room '+url)
        response=requests.get(url, auth=(Username, Password))
#        response=requests.get(url)
        data = json.loads(response.text)

        if 'result' in data.keys():
            for Item in data['result']:
                if str(Item['Name']) == RoomName:
                    idx=int(Item['idx'])
                    Domoticz.Debug('Found Room '+RoomName+' with idx '+str(idx))

        if (idx != 0) and Recreate :
            url='http://'+IPAddress+':'+HTTPPort+'/json.htm?idx='+str(idx)+'&param=deleteplan&type=command'
            Domoticz.Log('Delete Room '+url)
            response=requests.get(url, auth=(Username, Password))
#            response=requests.get(url)
            idx = 0
        
        if idx == 0 :
            url='http://'+IPAddress+':'+HTTPPort+'/json.htm?name='+RoomName+'&param=addplan&type=command'
            Domoticz.Log('Create Room '+url)
            response=requests.get(url, auth=(Username, Password))
#            response=requests.get(url)
            data = json.loads(response.text)
            Domoticz.Log('CreateRoom Created Room'+str(data))
            idx=int(data['idx'])
    except:
        Domoticz.Log('ERROR CreateRoom Failed')
        idx=0

    Domoticz.Debug('CreateRoom status should not be 0 : '+str(idx))
    
    return idx
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def AddToRoom(RoomIDX,ItemIDX):

    try:
        import json
    except:
        Domoticz.Log("python3 is missing module json")
        
    try:
        import requests
    except:
        Domoticz.Log("python3 is missing module requests")
    
    status=1

    try:
        url='http://'+IPAddress+':'+HTTPPort+'/json.htm?activeidx='+str(ItemIDX)+'&activetype=0&idx='+str(RoomIDX)+'&param=addplanactivedevice&type=command'
        response=requests.get(url, auth=(Username, Password))
#        response=requests.get(url)
        data = json.loads(response.text)
    except:
        Domoticz.Log('ERROR AddRoom Failed')
        status=0

    Domoticz.Debug('AddToRoom status should not be 0 : '+str(status))
    
    return status

# --------------------------------------------------------------------------------------------------------------------------------------------------------
def GetToonData(what):

    try :
        import json
    except:
        Domoticz.Log("python3 is missing module json")
    
    try:
        import requests
    except:
        Domoticz.Log("python3 is missing module requests")

    try:
        import datetime
    except:
        Domoticz.Log("python3 is missing module datetime")

    try:
        import subprocess
    except:
        Domoticz.Log("python3 is missing module subprocess")
        
    try:
        import time
    except:
        Domoticz.Log("python3 is missing module time")

    try:
        mydict={}

        if (what == 'ThermostatInfo'):
            url='http://'+ToonAddress+'/happ_thermstat?action=getThermostatInfo' 

            Domoticz.Debug('GetToonData '+what+' '+ url)
            
            response=requests.get(url, timeout=3)
            mydict = json.loads(response.text)

            if ( int(mydict['nextTime']) == 0 ):
                mydict['nextTime'] = '-100'
            else:
                NextDateTime = datetime.datetime.fromtimestamp(int(mydict['nextTime']))
                mydict['nextTime'] = str(NextDateTime)[11:16].replace(':','')
        
        if (what == 'Usage'):
            url='http://'+ToonAddress+'/happ_pwrusage?action=GetCurrentUsage' 

            Domoticz.Debug('GetToonData '+what+' '+ url)
            
            response=requests.get(url, timeout=3)
            tempmydict = {}
            tempmydict = json.loads(response.text)
            mydict['powerUsagevalue'] = tempmydict['powerUsage']['value'] 
            mydict['powerUsageavgValue'] = tempmydict['powerUsage']['avgValue'] 
            mydict['powerProductionvalue'] = tempmydict['powerProduction']['value'] 
            mydict['powerProductionavgValue'] = tempmydict['powerProduction']['avgValue'] 
            mydict['gasUsagevalue'] = tempmydict['gasUsage']['value'] 
            mydict['gasUsageavgValue'] = tempmydict['gasUsage']['avgValue'] 
            
        if (what == 'Toon2Sensors'):

            url='http://' + ToonAddress + '/tsc/sensors'

            Domoticz.Debug('GetToonData '+what+' '+ url)

            response=requests.get(url, timeout=3)
            mydict = json.loads(response.text)

        if (what == 'ReportValues'):

            command='/usr/bin/ssh  -o ConnectionAttempts=3 -o ConnectTimeout=3 -o BatchMode=yes ' + ToonAddress + ' ./toon-performance.sh'

            Domoticz.Debug('GetToonData '+what+' '+command)

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            timeouts=0
            result = ''
            while timeouts < 10:
                p_status = process.wait()
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:                        
                    line=str(output.strip())[2:-1]
                    field=line.split(' ')[0]
                    value=line.split(' ')[1]
                    mydict[field] = value
                else:
                    time.sleep(0.2)
                    timeouts=timeouts+1
                    
    except:
        mydict={}

    Domoticz.Debug('GetToonData '+what+' '+str(mydict))
    
    return mydict
# --------------------------------------------------------------------------------------------------------------------------------------------------------
