import ipqueue, dns, sys, os, select, socket, struct, string, pdb

# A single TCP packet, code for parsing the TCP header pillaged from pylibpcaps sniff.py (but cleaned up), this is the only code remaining from pynetstat, hence it seems a bit out of place ..

class APacket(object):

    def __init__(self, packet):

        self.packet = packet[9]
        self.pmeta = self.decode_meta_packet(packet)
        self.header = self.decode_ip_packet(packet[9])

        self.details = []
        
        names = ['srcaddr', 'sport', 'destaddr', 'dport']
        for name in names:
            self.details += [self.header[name]]
        
        names = ['inface', 'outface']
        for name in names:
            self.details += [self.pmeta[name]]

        self.incoming = cmp(self.pmeta['inface'], self.pmeta['outface']) # 1&1=0, 1&0=1, 0&1=-1

    def decode_meta_packet(self, s):

        d = dict() 
        names = ['packid', 'mark', 'timestamp', 'socket', 'inface', 'outface', 'hwproto', 'hw_type', 'addrlen', 'data']

        for x, name in enumerate(names):
            d[name] = s[x]

        return(d)

    def decode_ip_packet(self, s): #stole this one from sniff.py in pylibpcap
        
        def ntoa(s):
            return ".".join(map(str,(s & 0xff, (s >> 8) & 0xff, (s >> 16) & 0xff, (s >> 24) & 0xff)))

        d = {}
        d['version']        =(ord(s[0]) & 0xf0) >> 4
        d['header_len']     =ord(s[0]) & 0x0f
        d['tos']            =ord(s[1])
        d['total_len']      =socket.ntohs(struct.unpack('H',s[2:4])[0])
        d['id']             =socket.ntohs(struct.unpack('H',s[4:6])[0])
        d['flags']          =(ord(s[6]) & 0xe0) >> 5
        d['fragment_offset']=socket.ntohs(struct.unpack('H',s[6:8])[0] & 0x1f)
        d['ttl']            =ord(s[8])
        d['protocol']       =ord(s[9])
        d['checksum']       =socket.ntohs(struct.unpack('H',s[10:12])[0])
        d['srcaddr']        =ntoa(struct.unpack('i',s[12:16])[0])
        d['destaddr']       =ntoa(struct.unpack('i',s[16:20])[0])
        
        if d['header_len']>5:
            d['options']    =s[20:4*(d['header_len']-5)]
        else:
            d['options']    =None
            d['data']       =s[4*d['header_len']:]
        (d['sport'], 
         d['dport'],
         d['seq'],
         d['ack'],
         d['x2off'],
         d['flags'],
         d['win'],
         d['sum'],
         d['urp']) = struct.unpack("!HHLLBBHHH", d['data'][:20])
        print d
        return d


# A single stream of packets, Each instance currently comprises any packets matching source host/port dest host/port and the interfaces that they are going to/from.  As long as the conntracks is polled at some point to eliminate dead connections, this should do fine.

class AStream(object):

    def __init__(self, packet):
        
        self.stream = list()
        self.stream = [packet]

    def __iter__(self):

        for x in self.stream: 
            yield x
        return        

    def __iadd__(self, packet): # append a packet to the stream, ask no questions

        self.stream.append(packet)
        return self 

    def __eq__(self, packet): # source and destination hosts and ports + interfaces are equal?

        if packet.details == self.stream[0].details: 
            return True or False


# Handles and organises the packets coming from userspace

class IPQueue(object): 

    streamtracker = list() # list of existing streams

    def __init__(self):

        self.streamengine = ipqueue.new(ipqueue.IPQ_COPY_PACKET)

    def pending(self): # are there any packets pending from the ipqueue?

        if select.select([self.streamengine], [], [], 0)[0]:
            return True or False

    def __iter__(self): # yield the existing packet streams 

        self.process()
        for x in self.streamtracker:
            yield x
        return
    
    def __iadd__(self, packet): # append a packet to the stream

        self.streamtracker.append(AStream(packet))
        return self

    def process(self): # get pending packets, create streams, or add to existing streams
        
        while True:
            
            found = False
            
            if self.pending():
                
                pinfo = self.streamengine.read()
                tpacket = APacket(pinfo)
                for s in self: # using self.__iter__()
                    if tpacket.details == s.stream[0].details:
                        s += tpacket
                        found = True
                        break
                    
                if not found:
                    self += tpacket # this uses self.__iadd__() to create a new stream
            
            else: return
    
    def sentence(self, verdict, s):  # Hot or not (the connection...)

            if verdict == 'Yes': 
                for x in s:
                    self.streamengine.set_verdict(x.pmeta['packid'], ipqueue.NF_ACCEPT)
                self.streamtracker.remove(s.stream[0])
            
            else: 
                for x in s:
                    self.streamengine.set_verdict(x.pmeta['packid'], ipqueue.NF_DROP)
                self.streamtracker.remove(s.stream[0])
