import os, glob

class PyreStat(object):

    def get_conns_tcp(self):

        inodes = {}
        tinodes = {}
        connections = []
        f = open('/proc/net/tcp')
        f.readline()
        while(1):
            line = f.readline()

            if line == '': break
            line = line.split()
            inode = line[9]

            [lhost, lport] = line[1].split(':', 1)
            [rhost, rport] = line[2].split(':', 1)
            status = line[3]

            if int(status,16) == 0x01:
                status = "ESTABLISHED"
            elif int(status,16) == 0x0A:
                status = "LISTENING"
            elif int(status, 16) == 0x100:
                status = "WAITING"
            else:
                status = '-'
                continue

            lhost = int(lhost, 16)
            rhost = int(rhost, 16)
            lport = str(int(lport, 16))
            rport = str(int(rport, 16))
            lhost = ".".join(map(str,(lhost & 0xff, (lhost >> 8) & 0xff, (lhost >> 16) & 0xff, (lhost >> 24) & 0xff)))
            rhost = ".".join(map(str,(rhost & 0xff, (rhost >> 8) & 0xff, (rhost >> 16) & 0xff, (rhost >> 24) & 0xff)))
            inodes[inode] = [lhost, lport, rhost, rport, status]

        inodeGen = self.get_inodes(inodes)
        for x in inodeGen:
            lhost,lport,rhost,rport,status = inodes[x[0]]
            tinodes[x[0]] = [x[1], x[2], lhost, lport, rhost, rport, status]
        return tinodes

    def get_inodes(self, inodes):
        for file in glob.glob('/proc/[1-9]*/fd/*'):
            try:
                s = os.readlink(file)
                if s[0:8] == 'socket:[':
                    pinode = s[8:-1]
                    if pinode in inodes:
                        pid = file.split('/')[2]
                        try:
                            f = open('/proc/' + pid + '/status')
                            name = f.readline().split()[-1].rstrip()
                            f.close()
                        except IOError:
                            name = '?'
                        yield [pinode, pid, name]
            except os.error:
                pass

    def refresh(self):

        return self.get_conns_tcp()
