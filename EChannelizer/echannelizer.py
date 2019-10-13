# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigText, ConfigNumber, NoSave, ConfigClock, ConfigEnableDisable, ConfigSubDict, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.Sources.StaticText import StaticText

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

class EChannelizer_Fetch():
	def __init__(self, session, args = None):
		pass


class EChannelizer_Setup(ConfigListScreen, Screen):
	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.setup_title = _('EChannelizer') + " - " + _('Setup')
		Screen.setTitle(self, self.setup_title)
		self.skinName = ["EChannelizer_Setup", "Setup"]
		self.config = config.echannelizer
		self.onChangedEntry = []
		self.session = session
		ConfigListScreen.__init__(self, [], session = session, on_change = self.changedEntry)

		self["actions2"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"menu": self.keyCancel,
			"cancel": self.keyCancel,
			"save": self.keySave,
			"red": self.keyCancel,
			"green": self.keySave,
			"yellow": self.keyGo,
			"blue": self.keyAbout
		}, -2)

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Download"))
		self["key_blue"] = StaticText(_("About"))

		self["description"] = Label("")
		self["VKeyIcon"] = Boolean(False)
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()

		self.createSetup()

		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		indent = "- "
		self.list = []

		self.list.append(getConfigListEntry(_("EChannelizer token"), self.config.token, _('Token hints text.')))
		self.list.append(getConfigListEntry(_("Download settings"), self.config.settings, _('Settings hints text.')))
		self.list.append(getConfigListEntry(_("Download picons"), self.config.picons, _('Picons hints text.')))
		self.list.append(getConfigListEntry(_("Download epg"), self.config.epg, _('EPG hints text.')))
		self.list.append(getConfigListEntry(_("Show in extensions menu"), self.config.extensions, _('Extensions menu hints text.')))

		self.list.append(getConfigListEntry(_("Scheduled fetch"), self.config.schedule, _("Set up a task scheduler to automatically fetch EChannelizer data.")))
		if self.config.schedule.value:
			self.list.append(getConfigListEntry(indent + _("Schedule time of day"), self.config.scheduletime, _("Set the time of day to run EChannelizer plugin.")))
			self.list.append(getConfigListEntry(indent + _("Schedule days of the week"), self.config.dayscreen, _("Press OK to select which days to fetch the EPG.")))
			self.list.append(getConfigListEntry(indent + _("Schedule wake from deep standby"), self.config.schedulewakefromdeep, _("If the receiver is in 'Deep Standby' when the schedule is due wake it up to fetch the EPG.")))
			if self.config.schedulewakefromdeep.value:
				self.list.append(getConfigListEntry(indent + _("Schedule return to deep standby"), self.config.scheduleshutdown, _("If the receiver was woken from 'Deep Standby' and is currently in 'Standby' and no recordings are in progress return it to 'Deep Standby' once the import has completed.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyOk(self):
		if self["config"].getCurrent() and len(self["config"].getCurrent()) > 1 and self["config"].getCurrent()[1] == self.config.dayscreen:
			self.session.open(EChannelizerDaysScreen)
		else:
			self.keySave()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelCallback, MessageBox, _("Really close without saving settings?"))
		else:
			self.cancelCallback(True)

	def cancelCallback(self, answer):
		if answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False)

	def keySave(self):
		self.saveAll()
		self["description"].setText(_("The current configuration has been saved.") + (self.scheduleInfo and " " + _("Next scheduled fetch is programmed for %s.") % self.scheduleInfo + " " or " ") +  _("Please don't forget that after downloading the first time the selected providers will need to be enabled in EPG-Importer plugin."))

	def keyGo(self):
		self.saveAll()
		self.startDownload()

	def startDownload(self):
		print "[EChannelizer] startDownload"
		#self.session.openWithCallback(self.echannelizerCallback, EChannelizer_Fetch, {})

	def echannelizerCallback(self):
		pass

	def keyAbout(self):
		pass

	def selectionChanged(self):
		self["description"].setText(self.getCurrentDescription()) #self["description"].setText(self["config"].getCurrent()[2])

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		if self["config"].getCurrent() and len(self["config"].getCurrent()) > 1 and self["config"].getCurrent()[1] in (self.config.schedule, self.config.schedulewakefromdeep):
			self.createSetup()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
	# end: for summary

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()

		configfile.save()
		try:
			self.scheduleInfo = AutoScheduleTimer.instance.doneConfiguring()
		except AttributeError as e:
			print "[EChannelizer] Timer.instance not available for reconfigure.", e
			self.scheduleInfo = ""


class  EChannelizerDaysScreen(ConfigListScreen, Screen):
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		Screen.setTitle(self, _('EChannelizer') + " - " + _("Select days"))
		self.skinName = ["Setup"]
		self.config = config.echannelizer
		self.list = []
		days = (_("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"), _("Sunday"))
		for i in sorted(self.config.days.keys()):
			self.list.append(getConfigListEntry(days[i], self.config.days[i]))
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"green": self.keySave,
			"save": self.keySave,
			"cancel": self.keyCancel,
			"ok": self.keySave,
		}, -2)

	def keySave(self):
		if not any([self.config.days[i].value for i in self.config.days]):
			info = self.session.open(MessageBox, _("At least one day of the week must be selected"), MessageBox.TYPE_ERROR, timeout = 30)
			info.setTitle(_('EChannelizer') + " - " + _("Select days"))
			return
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelCallback, MessageBox, _("Really close without saving settings?"))
		else:
			self.cancelCallback(True)

	def cancelCallback(self, answer):
		if answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False)


def Scheduleautostart(reason, session=None, **kwargs):
	pass
