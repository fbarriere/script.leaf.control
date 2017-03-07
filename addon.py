#####################################################################
# Leaf status:
#     Kodi addon to fetch informations from the Carwings/Leaf service
# and remotely manage your Leaf (start charging, start the climate
# control, etc) from Kodi.
#####################################################################

import xbmcaddon
import xbmcgui
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib", "pycarwings2"))

import pycarwings2


def _(msg):
    addon = xbmcaddon.Addon()
    return addon.getLocalizedString(msg)


def build_config(addon):
    
    config = dict()
    
    config['username'] = addon.getSetting("username")
    config['password'] = addon.getSetting("password")
    config['timer']    = addon.getSetting("timer")
    config['region']   = ["NNA", "NE", "NCI", "NMA", "NML"][int(addon.getSetting("region"))]

    xbmc.log("Leaf control region: %s" % config['region'])

    return config


def leaf_connect(config):
    
    feedback(_(32050))

    server = pycarwings2.Session(
        config['username'],
        config['password'],
        config['region']
    )
    leaf = server.get_leaf()

    return leaf


def get_leaf_status(leaf, config):
    """Fetch the status from the server and display the informations
    in a progress window.
    Reports the following informations:
       - Charging or not charging
       - The plugin state (plugged/unplugged)
       - The percentage of battery charged.
    """
    
    status_table = {
        "YES":           _(32056),
        "NO":            _(32057),
        "CONNECTED":     _(32058),
        "NOT_CONNECTED": _(32059),
        }
    
    progress = xbmcgui.DialogProgress()
    
    progress.create(_(32060), _(32061))
    
    result_key     = leaf.request_update()
    battery_status = None
    msg            = _(32066)
    while battery_status is None:
        time.sleep(int(config['timer']))
        msg += "."
        progress.update(0, msg)
        battery_status = leaf.get_status_from_update(result_key)
    
    
    capacity         = float(battery_status.answer[u"batteryCapacity"])
    degradation      = float(battery_status.answer[u"batteryDegradation"])
    charge           = int((degradation / capacity) * 100)
    est_range_ac_off = int(float(battery_status.answer[u"cruisingRangeAcOff"]) / 1000.0)
    est_range_ac_on  = int(float(battery_status.answer[u"cruisingRangeAcOn"])  / 1000.0)
    
    # Status line 1
    status  = _(32062) + status_table.get(battery_status.answer[u"charging"], _(32065))
    status += "\n"
    # Status line 2
    status += _(32063) + status_table.get(battery_status.answer[u"pluginState"], _(32065))
    status += "\n"
    # Status line 3
    status += _(32064) + "%d / %d" % (est_range_ac_off, est_range_ac_on) + "\n"    
    
    progress.update(charge, status)
    
    while 1:
        time.sleep(3)
        if progress.iscanceled():
            break
    

def start_climate_control(leaf):
    """Start the climate control.
    """
    feedback(_(32999), xbmcgui.NOTIFICATION_WARNING)

 
def stop_climate_control(leaf):
    """Stop the climate control.
    """
    feedback(_(32999), xbmcgui.NOTIFICATION_WARNING)

 
def start_charging(leaf):
    """Start charging.
    """
    feedback(_(32999), xbmcgui.NOTIFICATION_WARNING)
    

def feedback(msg, type=xbmcgui.NOTIFICATION_INFO):
    xbmcgui.Dialog().notification(_(32060), msg, type)


def leaf_main():
    addon       = xbmcaddon.Addon()
    addonname   = addon.getAddonInfo('name')
    config      = build_config(addon)
    leaf        = leaf_connect(config)
    
    selection = xbmcgui.Dialog().select(
        _(32051), 
        [
            _(32052), 
            _(32053),
            _(32054),
            _(32055),
        ]
    )
    
    if selection == 0:
        get_leaf_status(leaf, config)
    elif selection == 1:
        start_charging(leaf)
    elif selection == 2:
        start_climate_control(leaf)
    elif selection == 3:
        stop_climate_control(leaf)
    

leaf_main()

