#
# version 1.0.0 : initial version
# version 1.1.0 : added buttons to restart Toon, Gui and start/stop VNC
# version 1.2.0 : added button to start/stop Logging
# version 1.3.0 : added button for 4-6 tile mode
# version 1.4.0 : get domoticz http IP port from running process named domoticz (when there is no /etc/init.d/domoticz.sh like on Raspberry Pi)
# version 1.5.0 : get temperature and for Toon 2 sensor data from http://Toon2/tsc/sensors ( temperature, humidity, eco2, tvoc and light intensity)
# version 1.5.1 : previous version did not put temperature in the room for Toon 1
#
"""
<plugin key="JacksToonMonitor" name="Jacks Toon Monitor" author="Jack Veraart" version="1.5.0">
    <description>
        <font size="4" color="white">Toon Monitor </font><font color="white">...Notes...</font>
        <ul style="list-style-type:square">
            <li><font color="cyan"><b>After reading the text below FIRST follow the instructions in the file Installing.txt to implement access to Toon and enable reporting.</b></font></li>
            <li><font color="yellow">This plugin has buttons for 'Restart Toon' , 'Restart GUI', 'Start/Stop vnc', 'Enable/Disable logging' and '4 Tile / 6 Tile' mode.</font></li>
            <li><font color="yellow">The buttons are protected by the password you enter in > Setup > Settings > Light/Switch Protection: Password.</font></li>
            <li><font color="yellow">When enabled, logging goes to /var/log/qt which will be removed after a reboot or by you manually. Logging stays active after a reboot unless you disable it again.</font></li>
            <li><font color="yellow">In your Toon app you can write to the log using : console.log("MyApp: this line is a test" + variable)</font></li>
            <li><font color="yellow">ssh to your Toon and follow your logging by 'tail -f /var/log/qt | grep MyApp'</font></li>
            <li><font color="yellow">'4 Tile' is standard mode. In '6 Tile' there is no big Heating tile and you need to use an Android app or something else to control your heating.</font></li>
            <li><font color="yellow">Maybe use my 1 tile heating app for Toon 1/2 from... <a href="https://github.com/JackV2020/toonSmallHeating"><font color="cyan">https://github.com/JackV2020/toonSmallHeating</font></a> ...which may go to the ToonStore.</font></li>
            <li><font color="cyan">If you want vnc on Toon 1/2 (on Toon 2 vnc is view-only) or add sftp on Toon 2 you may use additional instructions in Installing.txt.</font></li>
            <li><font color="yellow">Below you specify the Toon IP address. Find it on your Toon : click upper left corner > Instellingen/Settings > Internet.</font></li>
            <li><font color="yellow">A room can be created with the name you give in the Name field above.</font></li>
            <li><font color="yellow">The room creation needs admin rights so if you have an admin account and want a room you need to enter admin account details below.</font></li>
            <li><font color="cyan">Remember, after startup you can use notifications on the Utility Devices to be informed by mail etc. when the values like uptime are below/above certain values.</font></li>
            <li><font color="cyan">You can also use timers to control the switches. Maybe at midnight : disable logging followed by a reboot of your Toon.</font></li>
            <li><font color="yellow">To develop your own plugin...check this web site... <a href="https://www.domoticz.com/wiki/Developing_a_Python_plugin" ><font color="cyan">Developing_a_Python_plugin</font></a></font></li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Toon IP Address." width="120px" default="192.168.2.19"/>

        <param field="Username" label="Username."       width="120px" default="admin"/>

        <param field="Password" label="Password."       width="120px" default="secret" password="true"/>

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
HeartbeatCounterMax = 6 # Only every 'HeartbeatCounterMax * HeartbeatInterval' seconds there is a real update.
HeartbeatCounter = HeartbeatCounterMax

HomeFolder=''   # plugin finds right value
IPPort=0        # plugin finds right value
IPPort2=0        # plugin finds right value

ToonAddress=''
Username=''     # plugin finds right value
Password=''     # plugin finds right value
RoomName=''     # plugin uses the name you gave to your hardware

Button_Type='0'  # 0: Buttons 1: Drop Down menu

Toon2=False     # plugin looks for http://ToonAddress/tsc/sensors which is missing on a Toon 1

DeviceLibrary={}

RestartToonId=0
RestartGUIId=0
VNCId=0
LogId=0
Mode46Id=0

RestartToonName='Toon Restart'
RestartGUIName='Toon Restart GUI'
VNCName='x11vnc'
LogName='Log to /var/log/qt'
Mode46Name='Tile Mode'

SensorTemperatureId=0
SensorHumidityId=0
SensorTvocId=0
SensorEco2Id=0
SensorIntensityId=0

SensorTemperatureDescription="Toon 2 Temperature"
SensorHumidityDescription="Toon 2 Humidity"
SensorTvocDescription="Toon 2 tvoc"
SensorEco2Description="Toon 2 eco2"
SensorIntensityDescription="Toon 2 light intensity"

SensorTemperatureName="Temperature"
SensorHumidityName="Humidity"
SensorTvocName="TVOC"
SensorEco2Name="ECO2"
SensorIntensityName="Intensity"

SensorTemperatureUnits="C"
SensorHumidityUnits="%"
SensorTvocUnits="ppb"
SensorEco2Units="ppm"
SensorIntensityUnits="lux"

SensorTemperatureImage="Heating"
SensorHumidityImage="Water"
SensorTvocImage="Gas"
SensorEco2Image="Gas"
SensorIntensityImage="JVSpot"

class BasePlugin:
    enabled = False
    def __init__(self):
        #self.var = 123
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

        global LocalHostInfo
        
        global Toon2

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

            HomeFolder      =str(Parameters["HomeFolder"])
            Username        =str(Parameters["Username"])
            Password        =str(Parameters["Password"])
            RoomName        =str(Parameters['Name'])

            MyIPPort        =GetDomoticzPort()            

            LocalHostInfo='http://'+Username+':'+Password+'@localhost:'+MyIPPort

            Domoticz.Debug('call GetToon2Sensors() to determine if this is a Toon 1 / Toon 2 which has http://address/tsc/sensors')

            Toon2 = ( str(GetToon2Sensors()) != "{}" )
            
            Domoticz.Debug('Is this a Toon 2 ? : '+str(Toon2))

            ImportImages()

# Create devices as configured in ToonMonitor.conf

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

        Domoticz.Log("onCommand called " + str(Unit) + "  " + str(RestartToonId))

        command='/usr/bin/ssh  -o ConnectionAttempts=3 -o ConnectTimeout=3 -o BatchMode=yes ' + ToonAddress + ' '

        if Unit == RestartToonId:
            command=command + ' /sbin/init 6'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        if Unit == RestartGUIId:
            command=command + ' /usr/bin/killall qt-gui'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        if Unit == VNCId and Level == 10 :
            command=command + ' "if uname -a | grep armv5 ; then /usr/bin/x11vnc ; else x11vnc -forever -shared -rawfb map:/dev/fb0@1024x600x32 -usepw -pipeinput UINPUT:touch,touch_always=1,abs,pressure=128,direct_abs=/dev/input/event0,direct_btn=/dev/input/event0,direct_rel=/devinput/event0,direct_key=/dev/input/event0,nouinput ; fi"'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            Devices[Unit].Update(  nValue=0, sValue=str(Level))

        if Unit == VNCId and Level == 20 :
            command=command + ' "if uname -a | grep armv5 ; then /usr/bin/killall x11vnc-bin ; else /usr/bin/killall x11vnc ; fi"'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            Devices[Unit].Update(  nValue=0, sValue=str(Level))


        if Unit == LogId and Level == 10 :
            command=command + ' "sed -i ' + chr(39) + 's#startqt >/dev/null#startqt >/var/log/qt#' + chr(39) + ' /etc/inittab ; /sbin/init q ; /usr/bin/killall qt-gui"'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            Devices[Unit].Update(  nValue=0, sValue=str(Level))

        if Unit == LogId and Level == 20 :
            command=command + ' "sed -i ' + chr(39) + 's#startqt >/var/log/qt#startqt >/dev/null#' + chr(39) + ' /etc/inittab ; /sbin/init q ; /usr/bin/killall qt-gui"'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            Devices[Unit].Update(  nValue=0, sValue=str(Level))


        if Unit == Mode46Id and Level == 10 :
            command=command + ' "sed -i ' + chr(39) + 's#<feature>noHeating</feature>##' + chr(39) + ' /qmf/config/config_happ_scsync.xml && /sbin/init 6 &"'
            Domoticz.Log(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            Devices[Unit].Update(  nValue=0, sValue=str(Level))

        if Unit == Mode46Id and Level == 20 :
            command=command + ' "sed -i ' + chr(39) + 's#<features>#<features><feature>noHeating</feature>#' + chr(39) + ' /qmf/config/config_happ_scsync.xml && /sbin/init 6 &"'
            Domoticz.Log(command)
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
        
        if StartupOK == 1 :
                        
#            Domoticz.Log("onHeartbeat called Heartbeat: " + str(HeartbeatCounter))

            if HeartbeatCounter == HeartbeatCounterMax:

                ToonValues = {}
                ToonValues = GetReportValues()

                for field in ToonValues :
                    UpdateValue = ToonValues[field]
                    
                    for Device in DeviceLibrary :
                        if ( field == str(DeviceLibrary[Device]['Field']) ) :
                            UpdateUnit = int(DeviceLibrary[Device]['Unit'])

                            Devices[UpdateUnit].Update(  nValue=0, sValue=UpdateValue)
#
# For the next calls I have only created the temperature sensor. Others may follow
#
                ThermostatInfo = {}
                ThermostatInfo = GetToonData('Heating')

                Domoticz.Debug('Thermostat Info : ' + str(ThermostatInfo) )
                
                UsageInfo = {}
                UsageInfo = GetToonData('Usage')

                Domoticz.Debug('Usage Info : ' + str(UsageInfo) )
                
# Current Temperature

                currentTemp=str(round(float(ThermostatInfo['currentTemp' ])/100,1))
                Devices[SensorTemperatureId].Update(  nValue=0, sValue=currentTemp)
                
                if (Toon2):
                    ToonSensors = {}
                    ToonSensors = GetToon2Sensors()
                    
#                    Devices[SensorTemperatureId].Update(nValue=0, sValue=str(ToonSensors['temperature']))
                    Devices[SensorHumidityId].Update(nValue=0, sValue=str(ToonSensors['humidity']))
                    Devices[SensorTvocId].Update(nValue=0, sValue=str(ToonSensors['tvoc']))
                    Devices[SensorEco2Id].Update(nValue=0, sValue=str(ToonSensors['eco2']))
                    Devices[SensorIntensityId].Update(nValue=0, sValue=str(ToonSensors['intensity']))
                
                HeartbeatCounter = 0

            else:
                HeartbeatCounter = HeartbeatCounter + 1

            
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
# --------------------------------------------------------------------------------------------------------------------------------------------------------


def GetDomoticzPort():
#
# A friend of me renamed domoticz and changed the IP ports so.......
#
    try:
        import subprocess
    except:
        Domoticz.Log("python3 is missing module subprocess")
        
    try:
        import time
    except:
        Domoticz.Log("python3 is missing module time")
    
    global IPPort
    
    try:
        pathpart=Parameters['HomeFolder'].split('/')[3]
        searchfile = open("/etc/init.d/"+pathpart+".sh", "r")
        for line in searchfile:
            if ("-www" in line) and (line[0:11]=='DAEMON_ARGS'): 
                IPPort=str(line.split(' ')[2].split('"')[0])
        searchfile.close()
        Domoticz.Debug('######### GetDomoticzPort looked in: '+"/etc/init.d/"+pathpart+".sh"+' and found port: '+IPPort)
    except:
        command='ps -ef | grep domoticz | grep sslwww | grep -v grep | tr -s " "'
#        Domoticz.Debug(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        timeouts=0

        result = ''
        while timeouts < 10:
            p_status = process.wait()
            output = process.stdout.readline()
#            Domoticz.Log('Output: '+str(output))
            if output == '' and process.poll() is not None:
                break
            if output:                        
                IPPort=str(output)
                IPPort = IPPort[IPPort.find('-www'):]
                IPPort = IPPort[IPPort.find(' ')+1:]
                IPPort = IPPort[:IPPort.find(' ')]
            else:
                time.sleep(0.2)
                timeouts=timeouts+1
        Domoticz.Debug('######### GetDomoticzPort looked at live process and found port: '+IPPort)
    
    return IPPort

# --------------------------------------------------------------------------------------------------------------------------------------------------------

def GetImageDictionary(HostInfo):
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
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

        url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?type=custom_light_icons'
        username=HostInfo.split(':')[1][2:]
        password=HostInfo.split(':')[2].split('@')[0]

#        Domoticz.Log('....'+url+'....'+username+'....'+password+'....')

        response=requests.get(url, auth=(username, password))
        data = json.loads(response.text)
        for Item in data['result']:
            mydict[str(Item['imageSrc'])]=int(Item['idx'])

    except:
        mydict={}

#    Domoticz.Log(str(mydict))
    
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

    ImageDictionary=GetImageDictionary(LocalHostInfo)
    
    if ImageDictionary == {}:
        Domoticz.Log("ERROR I can not access the image library. Please modify the hardware setup to have the right username and password.")      
    else:

        for zipfile in glob.glob(HomeFolder+"CustomIcons/*.zip"):
            importfile=zipfile.replace(HomeFolder,'')
            try:
                Domoticz.Image(importfile).Create()
#                Domoticz.Debug("Imported/Updated icons from "  + importfile)
            except:
                Domoticz.Log("ERROR can not import icons from "  + importfile)

        ImageDictionary=GetImageDictionary(LocalHostInfo)

        Domoticz.Debug('ImportImages: '+str(ImageDictionary))
         
# --------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------  Device Creation Routines  ------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateDevice(deviceunit,devicename,devicetype,devicelogo="",devicedescription="",sAxis="",InitialValue=0.0):
    
    if deviceunit not in Devices:

        if ImageDictionary == {}:
            firstimage=0
            firstimagename='NoImage'
            Domoticz.Log("ERROR I can not access the image library. Please modify the hardware setup to have the right Username and Password.")      
        else:
            firstimage=int(str(ImageDictionary.values()).split()[0].split('[')[1][:-1])
            firstimagename=str(ImageDictionary.keys()).split()[0].split('[')[1][1:-2]
            Domoticz.Debug("First image id: " + str(firstimage) + " name: " + firstimagename)

        if firstimage != 0: # we have a dictionary with images and hopefully also the image for devicelogo

            try:

                deviceoptions={}
                deviceoptions['Custom']="1;"+sAxis
                Domoticz.Device(Name=devicename, Unit=deviceunit, TypeName=devicetype, Used=1, Image=ImageDictionary[devicelogo], Description=devicedescription).Create()
                Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=str(InitialValue))
                Domoticz.Log("Created device : " + devicename + " with '"+ devicelogo + "' icon and options "+str(deviceoptions)+' Value '+str(InitialValue))
            except:

# when devicelogo does not exist, use the first image found, (TypeName values Text and maybe some others will use standard images for that TypeName.)

                try:
                    Domoticz.Device(Name=devicename, Unit=deviceunit, TypeName=devicetype, Used=1, Image=firstimage, Description=devicedescription).Create()
                    Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=str(InitialValue))
                    Domoticz.Log("Created device : " + devicename+ " with '"+ firstimagename + "' icon and Value "+str(InitialValue))
                except:
                    Domoticz.Log("ERROR Could not create device : " + devicename)
#
# The next puts the right name, axis, image and description in the device
#
    try:

        NewName = devicename

        deviceoptions={}
        deviceoptions['Custom']="1;"+sAxis

        Devices[deviceunit].Update(nValue=Devices[deviceunit].nValue, sValue=Devices[deviceunit].sValue, Name=NewName, Options=deviceoptions, Image=ImageDictionary[devicelogo], Description=devicedescription)

        Domoticz.Debug("Updated "+NewName)
    except:
        Domoticz.Log("Update Failed")
        dummy=1

# --------------------------------------------------------------------------------------------------------------------------------------------------------

def CreateDevices():

    global DeviceLibrary
    global RestartToonId
    global RestartGUIId
    global VNCId
    global LogId
    global Mode46Id
    
    global SensorTemperatureId
    global SensorHumidityId
    global SensorTvocId
    global SensorEco2Id
    global SensorIntensityId

    DeviceLibrary={}
    Name=''
    Image=''
    Field=''
    Units=''
    Description=''
    MyStatus=1
    ConfigFile='ToonMonitor.conf'
    
    Recreate = False

    try:
        
        TheConfigFile=open(HomeFolder+ConfigFile, "r")
        TheConfigFile.close
        for Line in TheConfigFile:

#            Domoticz.Log(str(Line))

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
                elif Line.split('=')[0] == 'Units':
                    Units = Line.split('=')[1]
                elif Line.split('=')[0] == 'EndDevice':
                    DeviceEntry={}
                    DeviceEntry['Name']   = Name
                    DeviceEntry['Description']   = Description
                    DeviceEntry['Image']  = Image
                    DeviceEntry['Field']   = Field
                    DeviceEntry['Units']   = Units
                    DeviceEntry['Unit']   = -1
                    DeviceLibrary[Name]   = DeviceEntry
#                    Domoticz.Log("Device: "+str(DeviceEntry))
                else:
                    Domoticz.Log('Error Line: '+Line)
                    MyStatus=-1
#        Domoticz.Log("Library: "+str(DeviceLibrary))
    except:
        MyStatus=-1
        Domoticz.Log('Error opening config file: '+HomeFolder+ConfigFile)

    if MyStatus == 1:

# --------- start delete loop for removed / renamed devices

        DeleteOne=1
        while DeleteOne == 1: # My implementation of repeat until, make sure to get into the loop and immediately make sure to get out of it
            DeleteOne = 0
            for Unit in Devices: # inner loop to find what to delete
                if not Devices[Unit].Name in DeviceLibrary and not Devices[Unit].Name in [ RestartToonName, RestartGUIName, VNCName, LogName, Mode46Name, SensorTemperatureName, SensorHumidityName, SensorTvocName, SensorEco2Name, SensorIntensityName] :
                    DeleteOne = 1                                               # stay in the loop because we may have to do our thing again
                    UnitToDelete = Unit
                    Item=Devices[Unit].Name
            if DeleteOne == 1: # out of the inner loop it is safe to delete
                Domoticz.Log('.....')
                Domoticz.Log('.....Delete  my own device:  **'+Item+'**  Unit: **'+str(UnitToDelete)+'**')
                Devices[UnitToDelete].Delete()
                Domoticz.Log('.....Deleted my own device:  **'+Item+'**  Unit: **'+str(UnitToDelete)+'**')

# ------- end delete loop

# ------- check which devices already exist by updating the unit field
        
        for Unit in Devices:
            if Devices[Unit].Name in DeviceLibrary:
                DeviceLibrary[Devices[Unit].Name]['Unit'] = Unit

# ------- make sure all devices from the config file are there
    
        for Device in DeviceLibrary:

            DeviceName=DeviceLibrary[Device]['Name']
            DeviceUnit=DeviceLibrary[Device]['Unit']
            DeviceUnits=DeviceLibrary[Device]['Units']
            DeviceImage=DeviceLibrary[Device]['Image']
            DeviceDescription=DeviceLibrary[Device]['Description']

            deviceoptions={}
            deviceoptions['Custom']="1;"+DeviceUnits

            
            if DeviceUnit == -1:
                Domoticz.Log('Need to create '+str(Device))
                DeviceUnit = 1
                while DeviceUnit in Devices:
                    DeviceUnit = DeviceUnit + 1
                DeviceLibrary[Device]['Unit'] = DeviceUnit

#
# Whenever a new device is added we need to recreate the room so devices in the room are in the same order as in the config file.
#
                Recreate = True

                Domoticz.Device(Name=DeviceName, Unit=DeviceUnit, TypeName="Custom", Used=1, Options=deviceoptions, Image=ImageDictionary[DeviceImage], Description=DeviceDescription).Create()

                nValue=Devices[DeviceUnit].nValue
                sValue=Devices[DeviceUnit].sValue
#
# After creation, need to force right name
#
                Devices[DeviceUnit].Update(nValue=nValue, sValue=sValue, Name=DeviceName)
            else:
#
# Something in config may have changed
#
                if  (Devices[DeviceUnit].Description != DeviceDescription) or ( Devices[DeviceUnit].Options != deviceoptions) or ( Devices[DeviceUnit].Image !=ImageDictionary[DeviceImage]) :
                    Recreate = True
                    Domoticz.Log('Update config for: '+Devices[DeviceUnit].Name)
                    nValue=Devices[DeviceUnit].nValue
                    sValue=Devices[DeviceUnit].sValue
                    Devices[DeviceUnit].Update(nValue=nValue, sValue=sValue, Options=deviceoptions, Image=ImageDictionary[DeviceImage], Description=DeviceDescription)
#
# Create Restart Toon Button
#
        for Device in Devices:
            if Devices[Device].Name == RestartToonName :
                RestartToonId=Device

        if RestartToonId == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            RestartToonId=DeviceUnit
            Domoticz.Log('Create Restart Toon')

            Options ={}
            Options = {'LevelActions': '|',
                    'LevelNames': '|Restart Toon' ,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '0'}
            
            Domoticz.Device(Name=RestartToonName, Unit=RestartToonId, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary['Toon'], Options=Options, Used=1,Description='Restart Toon').Create()
            nValue=Devices[RestartToonId].nValue
            sValue=Devices[RestartToonId].sValue
#
# After creation, need to force right name and protection, ( after creation only so user changes are kept )
#
            Devices[RestartToonId].Update(nValue=nValue, sValue=sValue, Name=RestartToonName)

            DeviceProtection(LocalHostInfo,Devices[RestartToonId].ID,'yes')

            Domoticz.Log('Create Restart Toon')
#
# Create Restart GUI Button
#

        for Device in Devices:
            if Devices[Device].Name == RestartGUIName :
                RestartGUIId=Device

        if RestartGUIId == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            RestartGUIId=DeviceUnit
            Domoticz.Log('Create Restart GUI')

            Options = {'LevelActions': '|',
                    'LevelNames': '|Restart GUI' ,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '0'}
            
            Domoticz.Device(Name=RestartGUIName, Unit=RestartGUIId, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary['Toon'], Options=Options, Used=1,Description='Restart GUI').Create()
            nValue=Devices[RestartGUIId].nValue
            sValue=Devices[RestartGUIId].sValue
#
# After creation, need to force right name and protection, ( after creation only so user changes are kept )
#
            Devices[RestartGUIId].Update(nValue=nValue, sValue=sValue, Name=RestartGUIName)

            DeviceProtection(LocalHostInfo,Devices[RestartGUIId].ID ,'yes')

            Domoticz.Log('Created Restart GUI')

#
# Create Restart VNC Button
#
        for Device in Devices:
            if Devices[Device].Name == VNCName :
                VNCId=Device

        if VNCId == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            VNCId=DeviceUnit
            Domoticz.Log('Create VNC')

            Options = {'LevelActions': '||',
                    'LevelNames': '|Start VNC|Stop VNC' ,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '0'}
            
            Domoticz.Device(Name=VNCName, Unit=VNCId, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary['Toon'], Options=Options, Used=1,Description='Start / Stop VNC').Create()
            nValue=Devices[VNCId].nValue
            sValue=Devices[VNCId].sValue
#
# After creation, need to force right name and protection, ( after creation only so user changes are kept )
#
            Devices[VNCId].Update(nValue=nValue, sValue=sValue, Name=VNCName)

            DeviceProtection(LocalHostInfo,Devices[VNCId].ID ,'yes')

            Domoticz.Log('Created VNC')

#
# Create Log Button
#
        for Device in Devices:
            if Devices[Device].Name == LogName :
                LogId=Device

        if LogId == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            LogId=DeviceUnit

            Domoticz.Log('Create Log')

            Options = {'LevelActions': '||',
                    'LevelNames': '|Enable Log|Disable Log' ,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '0'}
            
            Domoticz.Device(Name=LogName, Unit=LogId, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary['Toon'], Options=Options, Used=1,Description='Start / Stop Log').Create()
            nValue=Devices[LogId].nValue
            sValue=Devices[LogId].sValue
#
# After creation, need to force right name and protection, ( after creation only so user changes are kept )
#
            Devices[LogId].Update(nValue=nValue, sValue=sValue, Name=LogName)

            DeviceProtection(LocalHostInfo,Devices[LogId].ID ,'yes')

            Domoticz.Log('Created Log')
#
# Create Mode Button
#
        for Device in Devices:
            if Devices[Device].Name == Mode46Name :
                Mode46Id=Device

        if Mode46Id == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            Mode46Id=DeviceUnit

            Domoticz.Log('Create Mode')

            Options = {'LevelActions': '||',
                    'LevelNames': '|4 Tiles|6 Tiles' ,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '0'}
            
            Domoticz.Device(Name=Mode46Name, Unit=Mode46Id, TypeName="Selector Switch", Switchtype=18, Image=ImageDictionary['Toon'], Options=Options, Used=1,Description='4 Tiles or 6 Tiles on Toon. Read Installing.txt in plugin folder to enable this on Toon itself').Create()
            nValue=Devices[Mode46Id].nValue
            sValue=Devices[Mode46Id].sValue
#
# After creation, need to force right name and protection, ( after creation only so user changes are kept )
#
            Devices[Mode46Id].Update(nValue=nValue, sValue=sValue, Name=Mode46Name)

            DeviceProtection(LocalHostInfo,Devices[Mode46Id].ID ,'yes')

            Domoticz.Log('Created Mode')
#
# Create Temperature sensor supported by Toon 1 and 2
#
        for Device in Devices:
            if Devices[Device].Name == SensorTemperatureName :
                SensorTemperatureId=Device

        if SensorTemperatureId == 0:
            DeviceUnit = 1
            while DeviceUnit in Devices:
                DeviceUnit = DeviceUnit + 1
            SensorTemperatureId=DeviceUnit

            CreateDevice(SensorTemperatureId,SensorTemperatureName,"Custom",SensorTemperatureImage,SensorTemperatureDescription,SensorTemperatureUnits,0)
#
# Add sensor devices for Toon 2 only
#
        if (Toon2):

#
# Create Humidity sensor
#
            for Device in Devices:
                if Devices[Device].Name == SensorHumidityName :
                    SensorHumidityId=Device

            if SensorHumidityId == 0:
                DeviceUnit = 1
                while DeviceUnit in Devices:
                    DeviceUnit = DeviceUnit + 1
                SensorHumidityId=DeviceUnit

                CreateDevice(SensorHumidityId,SensorHumidityName,"Custom",SensorHumidityImage,SensorHumidityDescription,SensorHumidityUnits,0)
#
# Create Eco2 sensor
#
            for Device in Devices:
                if Devices[Device].Name == SensorEco2Name :
                    SensorEco2Id=Device

            if SensorEco2Id == 0:
                DeviceUnit = 1
                while DeviceUnit in Devices:
                    DeviceUnit = DeviceUnit + 1
                SensorEco2Id=DeviceUnit

                CreateDevice(SensorEco2Id,SensorEco2Name,"Custom",SensorEco2Image,SensorEco2Description,SensorEco2Units,0)

#
# Create Tvoc sensor
#
            for Device in Devices:
                if Devices[Device].Name == SensorTvocName :
                    SensorTvocId=Device

            if SensorTvocId == 0:
                DeviceUnit = 1
                while DeviceUnit in Devices:
                    DeviceUnit = DeviceUnit + 1
                SensorTvocId=DeviceUnit

                CreateDevice(SensorTvocId,SensorTvocName,"Custom",SensorTvocImage,SensorTvocDescription,SensorTvocUnits,0)

#
# Create Intensity sensor
#
            for Device in Devices:
                if Devices[Device].Name == SensorIntensityName :
                    SensorIntensityId=Device

            if SensorIntensityId == 0:
                DeviceUnit = 1
                while DeviceUnit in Devices:
                    DeviceUnit = DeviceUnit + 1
                SensorIntensityId=DeviceUnit

                CreateDevice(SensorIntensityId,SensorIntensityName,"Custom",SensorIntensityImage,SensorIntensityDescription,SensorIntensityUnits,0)
#
# (Re-)Create Room
#
        RoomIdx=CreateRoom(LocalHostInfo, RoomName, Recreate)

#
# Add all items to Room if not already in
#
        for Device in DeviceLibrary:

            AddToRoom(LocalHostInfo,RoomIdx,Devices[DeviceLibrary[Device]['Unit']].ID)

        AddToRoom(LocalHostInfo,RoomIdx,Devices[RestartToonId].ID)
        AddToRoom(LocalHostInfo,RoomIdx,Devices[RestartGUIId].ID)
        AddToRoom(LocalHostInfo,RoomIdx,Devices[VNCId].ID)
        AddToRoom(LocalHostInfo,RoomIdx,Devices[LogId].ID)
        AddToRoom(LocalHostInfo,RoomIdx,Devices[Mode46Id].ID)

        AddToRoom(LocalHostInfo,RoomIdx,Devices[SensorTemperatureId].ID)

        if (Toon2):

            AddToRoom(LocalHostInfo,RoomIdx,Devices[SensorHumidityId].ID)
            AddToRoom(LocalHostInfo,RoomIdx,Devices[SensorTvocId].ID)
            AddToRoom(LocalHostInfo,RoomIdx,Devices[SensorEco2Id].ID)
            AddToRoom(LocalHostInfo,RoomIdx,Devices[SensorIntensityId].ID)

    return MyStatus
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------

def CreateRoom(HostInfo,RoomName, Recreate):
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
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

        username=HostInfo.split(':')[1][2:]
        password=HostInfo.split(':')[2].split('@')[0]

        Domoticz.Debug('Find Room')
        
        url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?type=plans&order=name&used=true'
        response=requests.get(url, auth=(username, password))
        data = json.loads(response.text)
        if 'result' in data.keys():
            for Item in data['result']:
                if str(Item['Name']) == RoomName:
                    idx=int(Item['idx'])
                    

        if (idx != 0) and Recreate :
            url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?idx='+str(idx)+'&param=deleteplan&type=command'
            Domoticz.Log('Delete Room '+url)
            response=requests.get(url, auth=(username, password))
            idx = 0
        
        if idx == 0 :
            
            url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?name='+RoomName+'&param=addplan&type=command'
            Domoticz.Log('Create Room '+url)
            response=requests.get(url, auth=(username, password))
            data = json.loads(response.text)
            idx=int(data['idx'])

    except:
        idx=-1

 #   Domoticz.Log(str(idx))
    
    return idx
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def AddToRoom(HostInfo,RoomIDX,ItemIDX):
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
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

        username=HostInfo.split(':')[1][2:]
        password=HostInfo.split(':')[2].split('@')[0]

        Domoticz.Debug('Add Item To Room')
        
        url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?activeidx='+str(ItemIDX)+'&activetype=0&idx='+str(RoomIDX)+'&param=addplanactivedevice&type=command'
#        Domoticz.Log(url)
        response=requests.get(url, auth=(username, password))
        data = json.loads(response.text)
#        Domoticz.Log(str(data))

    except:
        idx=-1

 #   Domoticz.Log(str(idx))
    
    return idx

# --------------------------------------------------------------------------------------------------------------------------------------------------------
def GetReportValues():

    global DeviceLibrary

    try:
        import subprocess
    except:
        Domoticz.Log("python3 is missing module subprocess")
        
    try:
        import time
    except:
        Domoticz.Log("python3 is missing module time")
    
    command='/usr/bin/ssh  -o ConnectionAttempts=3 -o ConnectTimeout=3 -o BatchMode=yes ' + ToonAddress + ' ./toon-performance.sh'
    Domoticz.Debug(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    timeouts=0

    result = ''
    mydict = {}
    while timeouts < 10:
        p_status = process.wait()
        output = process.stdout.readline()
#        Domoticz.Log('Output: '+str(output))
        if output == '' and process.poll() is not None:
            break

        if output:                        
            line=str(output.strip())[2:-1]
            field=line.split(' ')[0]
            value=line.split(' ')[1]
            mydict[field] = value
#            Domoticz.Log(line)
        else:
            time.sleep(0.2)
            timeouts=timeouts+1

#    Domoticz.Log(str(mydict))

    return mydict
# --------------------------------------------------------------------------------------------------------------------------------------------------------
def GetToonData(what):
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
# http://192.168.2.23/happ_thermstat?action=getThermostatInfo
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

        if what == 'Heating':
            url='http://'+ToonAddress+'/happ_thermstat?action=getThermostatInfo' 
        else:
            url='http://'+ToonAddress+'/happ_pwrusage?action=GetCurrentUsage' 
        
#        Domoticz.Log('....'+url)

        response=requests.get(url, timeout=5)
        mydict = json.loads(response.text)

    except:
        mydict={}

#    Domoticz.Log(str(mydict))
    
    return mydict
# --------------------------------------------------------------------------------------------------------------------------------------------------------

def GetToon2Sensors():
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
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

        url='http://' + ToonAddress + '/tsc/sensors'

        Domoticz.Debug('....'+url)

        response=requests.get(url)
        mydict = json.loads(response.text)
#        Domoticz.Log('Toon sensor data : '+str(mydict))

    except:
        mydict={}

    Domoticz.Debug(str(mydict))
    
    return mydict

# --------------------------------------------------------------------------------------------------------------------------------------------------------
def DeviceProtection(HostInfo,ItemIDX,Protected):
#
# HostInfo : http(s)://user:pwd@somehost.somewhere:port
#
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

        username=HostInfo.split(':')[1][2:]
        password=HostInfo.split(':')[2].split('@')[0]

        Domoticz.Log('Device Protection')
        
        if (Protected == 'yes'):
            url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?type=setused&protected=true&used=true&idx='+str(ItemIDX)
        else:
            url=HostInfo.split(':')[0]+'://'+HostInfo.split('@')[1]+'/json.htm?type=setused&protected=false&used=true&idx='+str(ItemIDX)
#        Domoticz.Log(url)
        response=requests.get(url, auth=(username, password))
        data = json.loads(response.text)
#        Domoticz.Log(str(data))

    except:
        idx=-1

 #   Domoticz.Log(str(idx))
    
    return idx
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------
