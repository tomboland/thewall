import PyPQ, PyreStat, PyrePTables

class PyreInProcess(object):

    def __init__(self):

        self.q = PyPQ.IPQueue()
        self.stat = PyreStat.PyreStat()
        self.iptables = PyrePTables.PyrePTables()

    def main(self):

        if self.q.pending:
            self.q.process()
        for x in self:
            print x
        return True

    def sentence(self, verdict, stream):

        if verdict in ['Yes', 'No']:
            self.q.sentence(verdict, stream)
        else:
            getattr(self.iptables, verdict)(stream)

    def pyrestat(self):

        return self.stat.refresh()

    def __iter__(self):

        for x in self.q:
            yield x
        return

