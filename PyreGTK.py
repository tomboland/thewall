import pygtk
pygtk.require('2.0')
import gtk
import egg.trayicon
import config
import gobject
import pdb
import time
import os
import signal
import GeoIP


class PyreGTK(object):
    
    def __init__(self, backend):
 
        self.backend = backend
        self.court = Court(self, backend)

        self.create_icon_menu()
        self.tray = egg.trayicon.TrayIcon('PyreWall')
        traybox = gtk.EventBox()
        self.tray.add(traybox)
        traybox.add(gtk.image_new_from_icon_name("pyrewall", gtk.ICON_SIZE_SMALL_TOOLBAR))
        self.tray.connect("event", self.icon_event)
        self.tray.show_all() 
        self.window = False

    def main_window(self, widget):
        
        self.window = PyreMainWindow(self, self.backend)
        self.window.connstat()    
        self.window.show_all()

    def icon_event(self, widget, event):
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.iconmenu.popup(None, None, None, event.button, event.time)
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            if self.window:
                self.window.destroy()
                self.window = False 
            else:
                self.main_window(widget)
            
    def create_icon_menu(self):

        self.iconmenu = gtk.Menu()
        self.menu_open_main = gtk.MenuItem("Connections")
        self.iconmenu.append(self.menu_open_main)
        self.menu_options = gtk.MenuItem("Options")
        self.iconmenu.append(self.menu_options)
        self.menu_queue = gtk.MenuItem("Queue")
        self.iconmenu.append(self.menu_queue)
        self.menu_exit = gtk.MenuItem("Exit")
        self.iconmenu.append(self.menu_exit)
        self.menu_root = gtk.MenuItem("menu")
        self.menu_root.set_submenu(self.iconmenu)
        self.menu_open_main.connect("activate", self.main_window)
        self.menu_open_main.show()
        self.menu_options.connect("activate", self.optionw)
        self.menu_options.show()
        self.menu_queue.connect("activate", self.dqueue)
        self.menu_queue.show()
        self.menu_exit.connect("activate", self.diediedie)
        self.menu_exit.show()
        self.iconmenu.show()

    def dqueue(self, widget, data=None):

        self.court.opencourt()
    
    def optionw(self, widget, data=None):

        optionsd = PyreOptions(self, self.backend)
        optionsd.set_modal(True)
        optionsd.show()

    def diediedie(self, widget, data=None):

        gtk.main_quit()

    def main(self):

        gobject.timeout_add(1000, self.court.process)
        gtk.main()

class PyreOptions(gtk.Dialog):

    def __init__(self, parent, backend):

        gtk.Dialog.__init__(self)

        self.okay = gtk.Button('OK')
        self.okay.connect("clicked", self.okay_button_clicked)
        self.vbox.pack_start(self.okay)
        self.okay.show()

    def okay_button_clicked(self, widget):

        self.destroy()

class Court(object):

    def __init__(self, father, backend):

        self.father = father
        self.backend = backend
        self.defendants = list()
        self.deathrow = list()

    def __iter__(self):

        for defendant in self.defendants:
            yield defendant

    def __iadd__(self, defendant):

        self.defendants += defendant

    def enter_defendant(self, stream):

        self.defendants += stream
        d = PopUpNotification(self, stream)

    def sentence(self, verdict, stream):

        if verdict <> 'Yes' and stream not in self.deathrow:
            self.deathrow += stream
        if verdict <> 'Yes' and stream in self.defendants:
            self.defendants.remove(stream)
        if verdict == 'Yes':
            self.defendants.remove(stream)
        self.backend.sentence(verdict, stream)

    def process(self):
        
        for defendant in self.backend:
            if defendant not in self and defendant not in self.deathrow:
                self.enter_defendant(defendant)
            if defendant in self.deathrow:
                self.sentence('No', defendant)

        return True

    def opencourt(self):

        try:
            getattr(self.courtroom, __init__)
            self.courtroom.show_all()
            self.courtoom.refresh()

        except (AttributeError, NameError):
            self.courtroom = Courtroom(self)
            self.courtroom.refresh()
            self.courtroom.show_all()
           

class Courtroom(gtk.Dialog):

    def __init__(self, father):

        gtk.Dialog.__init__(self)
        self.father = father
        names = ['lhost', 'lport', 'rhost', 'rport', 'remote location']
        self.geoip = GeoIP.new(GeoIP.GEOIP_STANDARD)

        self.list = gtk.ListStore(str, str, str, str, str)
        self.view = gtk.TreeView(self.list)
        self.sele = self.view.get_selection()
        
        for idx, name in enumerate(names):
            self.col = gtk.TreeViewColumn(name)
            self.view.append_column(self.col)
            self.cell = gtk.CellRendererText()
            self.col.pack_start(self.cell, True)
            self.col.add_attribute(self.cell, 'text', idx)
            self.view.set_search_column(idx)
            self.col.set_sort_column_id(idx)
        
        self.view.connect('event', self.rowselected)
        self.connect('delete-event', self.close)
        self.vbox.pack_start(self.view)
        
    def refresh(self):

        self.list.clear()
        for accused in self.father.defendants:
            self.list.append((accused.details[2], accused.details[3], accused.details[0], accused.details[1], self.geoip.country_name_by_addr(accused.details[0])))
        
    def rowselected(self, widget, event):

        if event.type == gtk.gdk.BUTTON_PRESS or event.type == gtk.gdk._2BUTTON_PRESS:
            x = int(event.x)
            y = int(event.y)
            pathnfo = self.view.get_path_at_pos(x,y)

            if pathnfo != None:

                iter = self.list.get_iter(pathnfo[0])
                path, col, cellx, celly = pathnfo
                for x in self.father.backend:
                    if x.stream[0] == self.father.defendants[path[0]]:
                        d = Judge(self.father, x)
                        d.set_modal(True)
                        d.show_all()

    def close(self, widget, data=None):

        self.hide_all()

class PopUpNotification(gtk.Window):

    def __init__(self, father, s):

        print s
        self.father = father
        self.s = s
        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)

        label = gtk.Label('Incoming Connection\nFrom: ' + str(s.stream[0].details[0]))
        evbox = gtk.EventBox()
        evbox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        evbox.connect("button-press-event", self.close)
        evbox.add(label)
        self.add(evbox)

        pos = self.father.father.tray.window.get_origin()
        size = self.father.father.tray.get_size()
        self.move(pos[0], pos[1]+size[1])
        gobject.timeout_add(5000, self.destroy)
        self.show_all()
        try:
            self.father.courtroom.refresh()
        except (AttributeError, NameError):
            pass

    def close(self, widget, event):

        self.father.opencourt()
        self.destroy()


class Judge(gtk.Dialog):

    def __init__(self, father, candle):   # connection handle duh!

        print candle
        self.geoip = GeoIP.new(GeoIP.GEOIP_STANDARD)
        self.father = father 
        
        gtk.Dialog.__init__(self)
        
        self.connect('delete_event', self.wclose)
 
        self.infobuffer = gtk.TextBuffer()
        self.infoview = gtk.TextView(buffer=self.infobuffer)
        self.infoview.set_editable(False)
        self.infoview.set_justification(gtk.JUSTIFY_CENTER)
        self.infotainer = gtk.VBox()
        self.infotainer.pack_start(self.infoview)
        self.infobuffer.set_text(self.info(candle))
        self.infotainer.show_all()
        
        self.vbox.pack_start(self.infotainer)
        self.judgeptions(candle)
        self.show_all()

    def judgeptions(self, candle):

        verdicts = ['Yes', 'No', 'BlockIP', 'BlockIPonPort', 'BlockPort', 'AllowIP', 'AllowIPonPort', 'AllowPort']
        self.buttons = {}
               
        for idx, verdict in enumerate(verdicts):
            self.buttons[verdict] = gtk.Button(verdict)
            self.buttons[verdict].connect("clicked", self.verdict, verdict, candle)
            self.action_area.pack_start(self.buttons[verdict])

    def wclose(self, widget, data=None):

        self.destroy()    

    def verdict(self, widget, verdict, s):

        self.father.sentence(verdict, s)
        self.father.courtroom.refresh()
        self.destroy()

    def info(self, candle):

        info = ""
        print candle.stream[0]
        if candle.stream[0].incoming == 1:

            info += 'An incoming connection has been attempted, do you want to allow it?' + '\n\n'
            info += 'in_interface:' + str(candle.stream[0].details[4]) + '\n'
            info += 'src_addr: ' + str(candle.stream[0].details[0]) + '\n'
            info += 'dest_port: ' + str(candle.stream[0].details[3]) + '\n'
            try:
                info += 'Country of origin: ' + self.geoip.country_name_by_addr(candle.stream[0].details[0])
            except TypeError:
                info += 'Country of origin unknown'

        elif candle.stream[0].incoming == -1:

            info += 'An outgoing connection has been attempted, do you wish to allow it?' + '\n\n'
            info += 'out_interface:' + str(candle.stream[0].details[5]) + '\n'
            info += 'Destination IP:' + str(candle.stream[0].details[2]) + '\n'
            info += 'Destination Port:' + str(candle.stream[0].details[3]) + '\n'
            try:
                info += 'Country of origin:' + self.geoip.country_name_by_addr(candle.stream[0].details[2]) + '\n'
            except TypeError:
                info += 'Country of origin unknown'

        elif candle.stream[0].incoming == 0:

            info += 'A looped back connection has been attempted, do you wish to allow it?' + '\n\n'
            info += 'Destination Port:' + str(candle.stream[0].details[3])

        return info


class Info(gtk.Dialog):

    def __init__(self, cinfo):

        gtk.Dialog.__init__(self)
        self.geoip = GeoIP.new(GeoIP.GEOIP_STANDARD)

        self.infobuffer = gtk.TextBuffer()
        self.infoview = gtk.TextView(buffer=self.infobuffer)
        self.infoview.set_editable(False)
        self.infoview.set_justification(gtk.JUSTIFY_CENTER)
        self.infotainer = gtk.VBox()
        self.infotainer.pack_start(self.infoview)
        self.infobuffer.set_text(self.prinfo(cinfo))
        self.infotainer.show_all()
        
        self.vbox.pack_start(self.infotainer)
        self.show_all()

    def prinfo(self, cinfo):
        
        info = ''
        info += 'Connection Info' + '\n\n'
        info += 'Process: ' + cinfo[1] + '\n'
        info += 'PID:' + cinfo[0] + '\n'
        info += 'Remote Host: ' + cinfo[4] + '\n'
        info += 'Remote Port: ' + cinfo[5] + '\n'
        info += 'Country of origin: ' + self.geoip.country_name_by_addr("82.33.126.55")
        return info

class PyreMainWindow(gtk.Dialog):

    def __init__(self, father, backend):
        
        self.existing_inodes = {}
        self.pid_ptr = {}
        self.backend = backend
        self.father = father
        
        self.court = self.father.court
        
        gtk.Dialog.__init__(self)
        self.init_table()
        self.set_size_request(config.wgeometryx, config.wgeometryy)
        self.connect("delete_event", self.wclose)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.create_menu()

        self.pview.connect("event", self.cell_selected)
        self.hbox = gtk.HBox()

        self.option_button = gtk.Button('Options')
        self.option_button.connect('clicked', father.optionw, None)
                
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw.add(self.pview)
        self.vbox.pack_start(self.sw)
        self.action_area.pack_start(self.option_button)
        gobject.timeout_add(3000, self.connstat)

    def init_table(self):

        names = config.columns
        self.plist = gtk.TreeStore(*[str for x in xrange(len(names))])
        
        self.pview = gtk.TreeView(self.plist)
        self.psel = self.pview.get_selection()
        self.psel.set_mode(gtk.SELECTION_MULTIPLE)
        
        for idx, name in enumerate(names):
            self.pv_col = gtk.TreeViewColumn(name)
            self.pview.append_column(self.pv_col)
            self.pv_cell = gtk.CellRendererText()
            self.pv_col.pack_start(self.pv_cell, True)
            self.pv_col.add_attribute(self.pv_cell, 'text', idx)
            self.pview.set_search_column(idx)
            self.pv_col.set_sort_column_id(idx)

    def connstat(self):

        inodes = self.backend.pyrestat()
        
        for x in inodes:
            if x not in self.existing_inodes:
                self.existing_inodes[x] = inodes[x]
# go through the existing inodes removing any that don't exist in the fresh copy
        for x in self.existing_inodes.copy():
            if x not in inodes:
                del self.existing_inodes[x]

        self.display_tree(self.existing_inodes)
        self.existing_pids = []

        return True

    def display_tree(self, inodes):
        
        rexpand = {}
        
        for x in self.pid_ptr:
            if self.pview.row_expanded(self.plist.get_path(self.pid_ptr[x])):
                    rexpand[x] = True 
            
        self.existing_pids = []
        self.old_pids = [] 
        self.pid_ptr = {}
        
        self.plist.clear()

        for x in inodes:
            if inodes[x][0] not in self.existing_pids:
                self.existing_pids.append(inodes[x][0])
                self.pid_ptr[inodes[x][0]] = self.plist.append(None, [inodes[x][0], inodes[x][1], '-', '-', '-', '-', inodes[x][6]])
                self.plist.append(self.pid_ptr[inodes[x][0]], inodes[x])
            else:
                self.plist.append(self.pid_ptr[inodes[x][0]], inodes[x])
       
        for x in rexpand:
            if x in self.existing_pids:
                self.pview.expand_row(self.plist.get_path(self.pid_ptr[x]), True)

        self.old_pids = self.existing_pids

    def cell_selected(self, widget, event):
    
        if event.type == gtk.gdk.BUTTON_PRESS or event.type == gtk.gdk._2BUTTON_PRESS:
        
            x = int(event.x)
            y = int(event.y)
            gtk.gdk.beep() 
            pathinfo = self.pview.get_path_at_pos(x,y)
            
            if pathinfo != None:
                
                piter = self.plist.get_iter(pathinfo[0])
                path, col, cellx, celly = pathinfo
                
                if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:

                    if self.plist.iter_has_child(piter):
                        pass
                    else:
                        d = Info(self.plist[path])
                        d.set_modal(True)
                        d.show_all
                
                if event.button == 3:
            
                    self.popup_menu(event,event.time,self.plist[path])

    def create_menu(self):
        
        self.menu = gtk.Menu()
        self.menu_kill = gtk.MenuItem("Kill")
        self.menu.append(self.menu_kill)
        self.menu_fwrule = gtk.MenuItem("Add FW rule")
        self.menu.append(self.menu_fwrule)
        self.menu_item = gtk.MenuItem("menu")
        self.menu_item.set_submenu(self.menu)
        self.menu_kill.connect("activate", self.kill_pid)
        self.menu_kill.show()
        self.menu_fwrule.show()
        self.menu_item.show()
        self.menu.show()
    
    def popup_menu(self, event, time):
        
        self.menu.popup(None, None, None, event.button, time)

    def kill_pid(self,widget,pid):
        
        os.kill(int(pid), signal.SIGINT)

    def wclose(self,  widget, data=None):

        self.destroy()
    
