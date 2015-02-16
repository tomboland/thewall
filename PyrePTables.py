import os
import config

class PyrePTables(object):


    def __init__(self):
        
        self._ipt_cmd_ = config.iptables_command

    def advanced(self, chain, cinfo):

        pass

    def gather_current_rules(self):

        pass
    
    def BlockIP(self, stream):
    
        addr = stream.stream[0].header['srcaddr']

        os.system(self._ipt_cmd_ + ' -I INPUT -p tcp -s ' + addr + ' -m state --state NEW -j REJECT')
        
    def BlockIPonPort(self, stream):

        addr = stream.stream[0].header['srcaddr']
        port = stream.stream[0].header['dport']
        
        os.system(self._ipt_cmd_ + ' -I INPUT -p tcp -s ' + addr + ' --dport ' + str(port) + ' -m state --state NEW -j REJECT')

    def BlockPort(self, stream):

        port = stream.stream[0].header['dport']

        os.system(self._ipt_cmd_ + '  -I INPUT -p tcp --dport ' + str(port) + ' -m state --state NEW -j REJECT')

    def AllowIP(self, stream):

        addr = stream.stream[0].header['srcaddr']

        os.system(self._ipt_cmd_ + '  -I INPUT -p tcp -s ' + addr + ' -m state --state NEW -j ACCEPT')
       

    def AllowIPonPort(self, stream):

        addr = stream.stream[0].header['srcaddr']
        port = stream.stream[0].header['dport']

        os.system(self._ipt_cmd_ + '  -I INPUT -p tcp -s ' + addr + ' --dport ' + str(port) + ' -m state --state NEW -j ACCEPT')

    def AllowPort(self, stream):

        port = stream.stream[0].header['dport']

        os.system(self._ipt_cmd_ + '  -I INPUT -p tcp --dport ' + str(port) + ' -m state --state NEW -j ACCEPT')
