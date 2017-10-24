# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/DisplayControl/plugin.py
from Plugins.Plugin import PluginDescriptor
from enigma import *
from Screens.Standby import *
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigSlider, getConfigListEntry, ConfigYesNo, ConfigNothing
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Screens.Standby import TryQuitMainloop
from enigma import eDBoxLCD
from Components.SystemInfo import SystemInfo
import ServiceReference
import commands
import os
import time
if os.path.isfile('/usr/lib/enigma2/python/Components/Lcd.pyo') is True:
    try:
        from Components.Lcd import *
    except:
        pass

if os.path.isfile('/usr/lib/enigma2/python/Components/UsageConfig.pyo') is True:
    try:
        from Components.UsageConfig import *
    except:
        pass

setmodelist = {'mode1': _('Program'),
 'mode2': _('Clock'),
 'mode3': _('Remaining'),
 'mode4': _('Station'),
 'mode5': _('Provider'),
 'mode6': _('CHnumber')}
test = {'500': _('slow'),
 '300': _('normal'),
 '100': _('fast')}
test2 = {'10000': _('10 seconds'),
 '20000': _('20 seconds'),
 '30000': _('30 seconds'),
 '60000': _('1 minute'),
 '300000': _('5 minutes'),
 'noscrolling': _('off')}
config.plugins.DisplayControl = ConfigSubsection()
config.plugins.DisplayControl.setmode = ConfigSelection(choices=setmodelist, default='mode1')
config.usage.vfd_scroll_speed = ConfigSelection(choices=test, default='300')
config.usage.vfd_scroll_delay = ConfigSelection(choices=test2, default='10000')

class ControlScreen(Screen, ConfigListScreen):
    skin = '\n\t\t<screen position="center,center" size="560,400" title="VU+Solo2 DisplayContol" >\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="110,10" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="310,10" size="140,40" alphatest="on" />\n\t\t\t<widget source="key_red" render="Label" position="110,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />\n\t\t\t<widget source="key_green" render="Label" position="310,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />\n\t\t\t<widget name="config" zPosition="2" position="5,70" size="550,200" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t<eLabel text="vuplus-images.co.uk" position="0,380" size="420,25" font="Regular;16" transparent="1" />\n\t\t\t<ePixmap position="160,210" size="218,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/DisplayControl/buttons/camd.png" zPosition="1" alphatest="on" />\n\t\t</screen>\n\t\t'

    def __init__(self, session):
        self.skin = ControlScreen.skin
        Screen.__init__(self, session)
        from Components.ActionMap import ActionMap
        from Components.Button import Button
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyGo,
         'save': self.keyGo,
         'cancel': self.keyCancel,
         'green': self.keyGo,
         'red': self.keyCancel}, -2)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        standby = config.lcd.standby.value
        bright = config.lcd.bright.value
        setmode = config.plugins.DisplayControl.setmode.value
        vfd_scroll_speed = config.usage.vfd_scroll_speed.value
        vfd_scroll_delay = config.usage.vfd_scroll_delay.value
        self.vfd_scroll_speed = ConfigSelection(choices=test, default=300)
        self.vfd_scroll_delay = ConfigSelection(choices=test2, default=10000)
        self.bright = ConfigSlider(default=5, limits=(0, 10))
        self.standby = ConfigSlider(default=1, limits=(0, 10))
        self.setmode = ConfigSelection(choices=setmodelist, default=setmode)
        self.vfd_scroll_speed = ConfigSelection(choices=test, default=vfd_scroll_speed)
        self.vfd_scroll_delay = ConfigSelection(choices=test2, default=vfd_scroll_delay)
        self.bright = ConfigSlider(default=bright, limits=(0, 10))
        self.standby = ConfigSlider(default=standby, limits=(0, 10))
        self.list.append(getConfigListEntry(_('Setup mode'), self.setmode))
        self.list.append(getConfigListEntry(_('VFD scroll speed '), self.vfd_scroll_speed))
        self.list.append(getConfigListEntry(_('VFD scroll delay'), self.vfd_scroll_delay))
        self.list.append(getConfigListEntry(_('Brightness'), self.bright))
        self.list.append(getConfigListEntry(_('Standby'), self.standby))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.setPreviewSettings()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.setPreviewSettings()

    def setPreviewSettings(self):
        applySettings(self.setmode.value, self.bright.value, self.standby.value, self.vfd_scroll_speed.value, self.vfd_scroll_delay.value)
        bright = self.bright.getValue()
        bright *= 255
        bright /= 10
        if bright > 255:
            bright = 255
        eDBoxLCD.getInstance().setLCDBrightness(bright)
        standby = self.standby.getValue()
        if standby:
            standby = 255
        eDBoxLCD.getInstance().setInverted(standby)

    def restartGuiNow(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def keyGo(self):
        config.plugins.DisplayControl.setmode.value = self.setmode.value
        config.lcd.bright.value = self.bright.value
        config.lcd.standby.value = self.standby.value
        config.usage.vfd_scroll_speed.value = self.vfd_scroll_speed.value
        config.usage.vfd_scroll_delay.value = self.vfd_scroll_delay.value
        config.plugins.DisplayControl.save()
        config.usage.vfd_scroll_speed.save()
        config.usage.vfd_scroll_delay.save()
        config.lcd.bright.save()
        config.lcd.standby.save()
        self.session.openWithCallback(self.restartGuiNow, MessageBox, _('Changes after a reboot ...\nRestart the GUI now?'), MessageBox.TYPE_YESNO, default=False)

    def keyCancel(self):
        setConfiguredSettings()
        self.close()


def applySettings(setmode, bright, standby, vfd_scroll_speed, vfd_scroll_delay):
    try:
        if setmode == 'mode1':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="session.Event_Now" render="RollerCharLCD" valign="center">',
             '<convert type="EventName">Name</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif setmode == 'mode2':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="global.CurrentTime" render="Label" valign="center">',
             '<convert type="ClockToText">Format:%H:%M</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif setmode == 'mode3':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="session.Event_Now" render="Label" valign="center">',
             '<convert type="EventTime">Remaining</convert>',
             '<convert type="RemainingToText">InMinutes</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif setmode == 'mode4':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="session.CurrentService" render="RollerCharLCD" valign="center">',
             '<convert type="ServiceName">Name</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif setmode == 'mode5':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="session.CurrentService" render="RollerCharLCD" valign="center">',
             '<convert type="ServiceName">Provider</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif setmode == 'mode6':
            os.system('rm -r /etc/enigma2/skin_user.xml &')
            os.system('touch /etc/enigma2/skin_user.xml &')
            file = open('/etc/enigma2/skin_user.xml', 'a')
            testList = ['<skin>',
             '<screen name="InfoBarSummary" position="0,0" size="200,20">',
             '<widget font="Regular;20" halign="center" position="0,0" size="200,20" source="session.CurrentService" render="RollerCharLCD" valign="center">',
             '<convert type="ExtendedServiceInfo">ServiceNumber</convert>',
             '</widget>',
             '</screen>',
             '</skin>']
            for i in testList:
                file.write(str(i) + '\n')

            file.close()
        elif vfd_scroll_speed == '500':
            usage.vfd_scroll_speed('500')
        elif vfd_scroll_speed == '300':
            usage.vfd_scroll_speed('300')
        elif vfd_scroll_speed == '100':
            usage.vfd_scroll_speed('100')
        elif vfd_scroll_delay == '10000':
            usage.vfd_scroll_delay('10000')
        elif vfd_scroll_delay == '20000':
            usage.vfd_scroll_delay('20000')
        elif vfd_scroll_delay == '30000':
            usage.vfd_scroll_delay('30000')
        elif vfd_scroll_delay == '60000':
            usage.vfd_scroll_delay('60000')
        elif vfd_scroll_delay == '300000':
            usage.vfd_scroll_delay('300000')
        elif vfd_scroll_delay == 'noscrolling':
            usage.vfd_scroll_delay('noscrolling')
    except:
        return


def setConfiguredSettings():
    applySettings(config.lcd.bright.value, config.usage.vfd_scroll_speed.value, config.usage.vfd_scroll_delay.value, config.lcd.standby.value, config.plugins.DisplayControl.setmode.value)


def main(session, **kwargs):
    session.open(ControlScreen)


def startup(reason, **kwargs):
    setConfiguredSettings()


def Plugins(**kwargs):
    return [PluginDescriptor(name='DisplayControl', description=_('VU+ Solo2 DisplayControl'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main), PluginDescriptor(name='DisplayControl', description=_('DisplayControl v0.4'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]