# for localized messages
from . import _

from Plugins.Plugin import PluginDescriptor

from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigText, ConfigNumber, NoSave, ConfigClock, ConfigEnableDisable, ConfigSubDict

from echannelizer import Scheduleautostart, EChannelizer_Fetch, EChannelizer_Setup

config.echannelizer = ConfigSubsection()

config.echannelizer.token = ConfigText("", False)
config.echannelizer.settings = ConfigYesNo(default = False)
config.echannelizer.picons = ConfigYesNo(default = False)
config.echannelizer.epg = ConfigYesNo(default = False)
config.echannelizer.extensions = ConfigYesNo(default = False)

# start: echannelizer.schedule
config.echannelizer.schedule = ConfigYesNo(default = False)
config.echannelizer.scheduletime = ConfigClock(default = 0) # 1:00
config.echannelizer.retry = ConfigNumber(default = 30)
config.echannelizer.retrycount = NoSave(ConfigNumber(default = 0))
config.echannelizer.nextscheduletime = ConfigNumber(default = 0)
config.echannelizer.schedulewakefromdeep = ConfigYesNo(default = True)
config.echannelizer.scheduleshutdown = ConfigYesNo(default = True)
config.echannelizer.dayscreen = ConfigSelection(choices = [("1", _("Press OK"))], default = "1")
config.echannelizer.days = ConfigSubDict()
for i in range(7):
	config.echannelizer.days[i] = ConfigEnableDisable(default = True)
# end: echannelizer.schedule


def main(session, **kwargs):
	session.open(EChannelizer_Setup)

def startfetch(session, **kwargs):
	session.open(EChannelizer_Fetch)

def EChannelizerWakeupTime():
	print "[EChannelizer] next wakeup due %d" % config.echannelizer.nextscheduletime.value
	return config.echannelizer.nextscheduletime.value > 0 and config.echannelizer.nextscheduletime.value or -1

def Plugins(**kwargs):
	plist = []
	plist.append(PluginDescriptor(name="EChannelizerScheduler", where=[ PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART ], fnc=Scheduleautostart, wakeupfnc=EChannelizerWakeupTime, needsRestart=True))
	plist.append(PluginDescriptor(name=_("EChannelizer"), description=_("Fetches from EChannelizer server."), icon="echannelizer.png", where = PluginDescriptor.WHERE_PLUGINMENU, needsRestart = True, fnc=main))
	if config.echannelizer.extensions.getValue():
		plist.append(PluginDescriptor(name=_("EChannelizer fetch"), description=_("Fetches from EChannelizer server."), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=startfetch, needsRestart=True))
	return plist