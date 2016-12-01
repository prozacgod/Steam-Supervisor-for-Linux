#!/usr/bin/env python
import signal, psutil
import time
import subprocess
import dbus
import dbus.service
import dbus.mainloop.glib

import gobject

# DVI-I-1 connected 1280x1024+2560+0 (normal left inverted right x axis y axis) 376mm x 301mm
# DP-4 connected primary 2560x1440+0+0 (normal left inverted right x axis y axis) 597mm x 336mm

#FEATURE: Kill other steam processes?

#TODO: config file


def child_processes(parent_pid):
  try:
    parent = psutil.Process(parent_pid)
  except psutil.NoSuchProcess:
    return []
  
  return parent.children(recursive=True)
  
# child_processes(21805)

class Steam():
  def __init__(self):
    self.steamCmd = ["/usr/bin/steam"]
    self.pid = None
    self.process = None
    self.lastReturnCode = None
    
  def status(self):
    if self.process:
      self.process.poll()

      #TODO: should I time.sleep(1) here?
      
      if self.process.returncode:
        return '{status:"stopped", returnCode:%d}' % (self.process.returncode)
      else:
        return '{status:"running", pid:%d}' % (self.process.pid)
    
    else:
      return '{status:"ready"}'

  def start(self):
    self.process = subprocess.Popen(self.steamCmd)
    
  def stop(self):
    #self.process.terminate()
    #NOTE: see Steam.kill
    children = child_processes(self.process.pid)
    for child in children:
      if child.name == 'steam':
        print "Stopping - ", child.pid
        child.send_signal(signal.SIGTERM)    
       
  def kill(self):
    #NOTE: steam is not a straight forward beast to kill, this bash process launches the steam process(es) so
    # we'll
    #TODO: this was working hack, audit for proper procedure
    #self.process.kill()
    children = child_processes(self.process.pid)
    for child in children:
      print child.name
      if child.name == 'steam':      
        print "Killing - ", child.pid
        child.send_signal(signal.SIGKILL)
        

class SteamMonitorService(dbus.service.Object):
  def __init__(self):
    self.steam = Steam()

  def run(self):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus_name = dbus.service.BusName("com.prozacville.steam_monitor", dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, "/com/prozacville/steam_monitor")

    self._loop = gobject.MainLoop()
    print "Service running..."
    self._loop.run()
    print "Service stopped"

  @dbus.service.method("com.prozacville.steam_monitor.Start", in_signature='', out_signature='')
  def steam_start(self):
    print "Steam starting"
    self.steam.start()
    print "Steam started, PID %s" % self.steam.process.pid

  @dbus.service.method("com.prozacville.steam_monitor.Status", in_signature='', out_signature='s')
  def steam_status(self):
    status = self.steam.status() 
    print "Steam Status", status    
    return status

  @dbus.service.method("com.prozacville.steam_monitor.Stop", in_signature='', out_signature='')
  def steam_stop(self):
    print "Steam stop"
    self.steam.stop()

  @dbus.service.method("com.prozacville.steam_monitor.Kill", in_signature='', out_signature='')
  def steam_kill(self):
    print "Steam KILL!"
    self.steam.kill()

  @dbus.service.method("com.prozacville.steam_monitor.Quit", in_signature='', out_signature='')
  def quit(self):
    print "  shutting down"
    self._loop.quit()

if __name__ == "__main__":
  print "Starting Steam Supervisor"
  SteamMonitorService().run()

