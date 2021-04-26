#!/bin/sh
#
# 
#
#UPTIME=$(awk '{print int($1)}' /proc/uptime)
UPTIME=$(cat /proc/uptime | cut -d "." -f 1)
echo "uptime $UPTIME"
#
PID=$(pidof qt-gui)
#STARTTIME=$(awk '{print int($22 / 100)}' /proc/$PID/stat)
STARTTIME=$(( $(cat /proc/$PID/stat | cut -d " " -f 22) / 100 ))
echo "qt-gui-uptime $((UPTIME - STARTTIME))"
#
# Next 3 lines will show start time of qt-gui
#
#NOW=$(date +%s)
#DIFF=$((NOW - (UPTIME - STARTTIME)))
#date -d @$DIFF
#
LOAD1=$(cat /proc/loadavg | cut -d " " -f 1)
echo "load1 $LOAD1"
LOAD5=$(cat /proc/loadavg | cut -d " " -f 2)
echo "load5 $LOAD5"
LOAD15=$(cat /proc/loadavg | cut -d " " -f 3)
echo "load15 $LOAD15"
FREEMEM=$(cat /proc/meminfo | grep MemFree | tr -s " " | cut -d " " -f 2)
echo "freemem $FREEMEM"
USEDROOT=$(df | grep root | tr -s " " | cut -d " " -f 5 | cut -d "%" -f 1)
echo "usedroot $USEDROOT"
USEDRAMDISK=$(df | grep /var/volatile | tr -s " " | cut -d " " -f 5 | cut -d "%" -f 1)
echo "usedramdisk $USEDRAMDISK"
# Now a complicated command because top on Toon 1 differs from top on Toon 2
CPUIDLE=$(top -b -n 2 | grep -i CPU  | grep ":" | grep "%" | grep -v grep | tail -n 1 | tr -s " " | cut -d "n" -f 2 | cut -d " " -f 2 | cut -d "%" -f 1)
echo "cpuidle $CPUIDLE"
#WINDOW=2
#tail -n 1 /proc/net/netstat | cut -d " " -f 8,9 > /var/volatile/tmp/net1.txt && sleep $WINDOW && tail -n 1 /proc/net/netstat | cut -d " " -f 8,9 > /var/volatile/tmp/net2.txt
#echo inbytesrate $(( ( `cat /var/volatile/tmp/net2.txt | cut -d " " -f 1` - `cat /var/volatile/tmp/net1.txt | cut -d " " -f 1` ) / $WINDOW  ))
#echo outbytesrate $(( ( `cat /var/volatile/tmp/net2.txt | cut -d " " -f 2` - `cat /var/volatile/tmp/net1.txt | cut -d " " -f 2` ) / $WINDOW  ))
#
# Networkload over last period
#
INBYTES=`tail -n 1 /proc/net/netstat | cut -d " " -f 8`
OUTBYTES=`tail -n 1 /proc/net/netstat | cut -d " " -f 9`
NETADMINFILE='/var/volatile/tmp/lastnetdata.txt'
if ! [ -f $NETADMINFILE ]
then 
  INBYTESRATE=0
  OUTBYTESRATE=0
else
  PREVUPTIME=`cat $NETADMINFILE | cut -d " " -f 1`
  PREVINBYTES=`cat $NETADMINFILE | cut -d " " -f 2`
  PREVOUTBYTES=`cat $NETADMINFILE | cut -d " " -f 3`
  INBYTESRATE=$(( ( $INBYTES - $PREVINBYTES ) / ( $UPTIME - $PREVUPTIME) ))
  OUTBYTESRATE=$(( ( $OUTBYTES - $PREVOUTBYTES ) / ( $UPTIME - $PREVUPTIME) ))
fi
echo inbytesrate $INBYTESRATE
echo outbytesrate $OUTBYTESRATE
echo $UPTIME $INBYTES $OUTBYTES > $NETADMINFILE
#
# wifi signal in dBm 
# 
# oepie-loepie gave me the bxt command to get wireless info. Output turned out to be in the error device so we need output from 2
/qmf/bin/bxt -d :hcb_netcon -s NetworkInformation -n GetWirelessNetworkInformation > /dev/null 2>/var/volatile/tmp/get_dBm.txt
# the next gets the value.
echo wifidb `grep -i -e '<signal' /var/volatile/tmp/get_dBm.txt | cut -d ">" -f 2 | cut -d " " -f 1`
