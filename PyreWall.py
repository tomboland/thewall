#!/usr/bin/env python

import config

class PyreWall(object):

    def __init__(self):

        self.backend_init()
        self.gui_init()

    def backend_init(self):

 #       try:
            self.backmod = __import__(config.backend)
            self.backend = getattr(self.backmod, config.backend)()
#        except:
  #          print 'there is no import for the backend config entry'

    def gui_init(self):
        
        try:
            self.guimod = __import__(config.gui)
        except:
            print 'there is no import for the GUI config entry'
        try:
            self.gui = getattr(self.guimod, config.gui)(self.backend)
        except:
            print "couldn't instantiate gui class"


    def backend_connect(self):
        
        print 'todo'

    def main(self):

        if config.backend == 'PyreTwisted':
            self.backend.main()
        else:
            self.gui.main()

if __name__ == "__main__":

    pyrewall = PyreWall()
    pyrewall.main()
