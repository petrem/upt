import string
import sys

(HOST_START, HOST_END, CONTENT, BOGUS) = range(4)
(FSM_OUTSIDE, FSM_INSIDE, FSM_ERROR) = range(3)

ips = {}

def linetype(str):
    if str.find("host") == 0:
        return HOST_START
    elif str.find("}") == 0:
        return HOST_END
    elif str == "" or str.find("#") == 0:
        return BOGUS
    else:
        return CONTENT

def parse_dhcphosts(f, target):
    state = FSM_OUTSIDE
    host = []
    comment = [""]

    def gather(l, s):
        l.append(s)

    def finalize(l, s):
        if comment[0].find("#") == 0:
            l.append("comment "+comment[0].lstrip("# "))
        target(l)
        l[:] = []

    def getdhcphostname(l, s):
        atoms = s.split()
        if len(atoms) > 1 and atoms[1] != "{":
            l.append("host " + atoms[1])

    def keep(l, s):
        comment[0] = s

    # for each state: INPUT (line type), ACTION
    fsm = [
        # FSM_OUTSIDE: HOST_START, HOST_END, CONTENT, BOGUS
        [(getdhcphostname, FSM_INSIDE), (None, FSM_OUTSIDE), (None, FSM_OUTSIDE), (keep, FSM_OUTSIDE)],
        # FSM_INSIDE:  HOST_START, HOST_END, CONTENT, BOGUS
        [(gather, FSM_INSIDE), (finalize, FSM_OUTSIDE), (gather, FSM_INSIDE), (None, FSM_INSIDE)]
    ]
    for line in f:
        line2=line.strip()
        (act, state) = fsm[state][linetype(line2)]
        if state == FSM_ERROR:
            print "(FSM) Error parsing file: ", line2
            sys.exit(1)
        #print state, linetype(line2), line2
        if act != None:
            act(host, line2)

def parsehost(host):
    macs = []
    dhcphostname = None
    ip = None
    comment = None
    for statement in host:
        if statement.find("hardware") == 0:
            macs.append(statement.split()[2].strip(";"))
        elif statement.find("fixed-address") == 0:
            ip = statement.split()[1].strip(";")
        elif statement.find("host") == 0:
            dhcphostname = statement.split()[1].strip(";")
        elif statement.find("comment") == 0:
            comment = statement.split(" ",1)[1]
        else:
            print "Unknown statement", statement
            sys.exit(1)
    if ip == None:
        print "Warning: host declaration without a fixed address, ignoring it"
        return
    if ip in ips.keys():
        print "Warning: redefining", ip
    ips[ip] = (macs, dhcphostname, comment)

with open("dhcpd.conf", 'r') as f:
    parse_dhcphosts(f, parsehost)

for ip in sorted(ips.keys(),key=lambda x: int(x[x.rindex(".")+1:])):
    print ip, ":", ips[ip]
