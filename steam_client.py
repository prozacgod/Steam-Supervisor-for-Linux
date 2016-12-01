#!/usr/bin/env python

import dbus
import time

class SteamMonitorClient():
  def __init__(self):
    bus = dbus.SessionBus()
    service = bus.get_object('com.prozacville.steam_monitor', "/com/prozacville/steam_monitor")
    self._start = service.get_dbus_method('steam_start', 'com.prozacville.steam_monitor.Start')
    self._status = service.get_dbus_method('steam_status', 'com.prozacville.steam_monitor.Status')
    self._stop = service.get_dbus_method('steam_stop', 'com.prozacville.steam_monitor.Stop')
    self._kill = service.get_dbus_method('steam_kill', 'com.prozacville.steam_monitor.Kill')
    self._quit = service.get_dbus_method('quit', 'com.example.service.Quit')

  def start(self):
    self._start()

  def status(self):
    return self._status()
      
  def stop(self):
    self._stop()

  def kill(self):
    self._kill()


if __name__ == "__main__":
  client = SteamMonitorClient()
  print client.status()
  #print client.start()
  print client.kill()
  
  #time.sleep(30)
  #SteamMonitorService().stop()
