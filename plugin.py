# PS4Status for Domoticz
#
# by John van de Vrugt
#
# A domoticz plugin based on the ps4waker
# https://github.com/dhleong/ps4-waker
"""
<plugin key="PS4Status4Domoticz" name="PS4Status4Domoticz" author="John van de Vrugt" version="1.0.0">
    <description>
    </description>
    <params>
        <param field="Mode1" label="IP address" required="true"/>
        <param field="Mode2" label="Time out" required="true">
            <options>
                <option label="100 ms" value="100" default="true" />
                <option label="250 ms" value="250"/>
                <option label="500 ms" value="500"/>
                <option label="1000 ms" value="1000"/>
            </options>
        </param>
        <param field="Mode3" label="Update rate" required="true">
            <options>
                <option label="10 seconds" value="0.12"/>
                <option label="30 seconds" value="0.5" default="true" />
                <option label="1 minute" value="1"/>
                <option label="2 minutes" value="2"/>
                <option label="5 minutes" value="5"/>
                <option label="10 minutes" value="10"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import json

import Domoticz
import subprocess
import sys

HEARTBEATS_PER_MIN = 6


class PS4StatusPlugin:
    _heart_beat = 0
    _heart_bead_mod = 1
    _debug_on = False
    _previous_value = -1  # not set

    def __init__(self):
        return

    def on_start(self):
        Domoticz.Log("Starting PS4Status")
        self._debug_on = Parameters["Mode6"] == "Debug"

        updates_per_min = 1
        if Parameters["Mode3"] != "":
            updates_per_min = (Parameters["Mode3"])
        self._heart_bead_mod = HEARTBEATS_PER_MIN * float(updates_per_min)

        if self._debug_on:
            Domoticz.Log("Heartbeat mod: " + str(self._heart_bead_mod))

        if (len(Devices) == 0):
            Domoticz.Device(Name="Status", Unit=1, TypeName="Switch", Image=9).Create()

        self._update_devices()

    def on_command(self, Unit, Command, Level, Hue):
        if self._debug_on:
            Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" +
                         str(Command) + "', Level: " + str(Level))

    def on_heartbeat(self):
        self._heart_beat = self._heart_beat + 1
        if self._heart_beat >= self._heart_bead_mod:
            self._heart_beat = 0
            self._update_devices()

    def _update_devices(self):
        if self._debug_on:
            Domoticz.Log("Update devices")

        statusOnOff = 0
        output = subprocess.run(["ps4-waker", "-d", str(Parameters["Mode1"]), "-t", str(Parameters["Mode2"]), "check"], capture_output=True)

        parsedoutputStd = output.stdout.decode("utf-8")
        parsedoutputErr = output.stderr.decode("utf-8")

        if self._debug_on :
            Domoticz.Log("Std: " + parsedoutputStd)
            Domoticz.Log("Err: " + parsedoutputErr)

        if len(parsedoutputErr) == 0:
            jsonPS4 = json.loads(parsedoutputStd)

            if self._debug_on:
                Domoticz.Log("JSON status: " + str(jsonPS4["status"]))

            if jsonPS4["status"] == "Ok":
                statusOnOff = 1

        #Domoticz.Log("statusOnOff: " + str(statusOnOff) + " self._previous_value: " + str(self._previous_value) )

        if statusOnOff != self._previous_value:
            if self._debug_on:
                Domoticz.Log("Update PS4 status: " + str(statusOnOff))
            Devices[1].Update(statusOnOff, str(statusOnOff))

        self._previous_value = statusOnOff

global _plugin
_plugin = PS4StatusPlugin()


def onStart():
    global _plugin
    _plugin.on_start()


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.on_command(Unit, Command, Level, Hue)


def onHeartbeat():
    global _plugin
    _plugin.on_heartbeat()
