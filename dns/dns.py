import sys
import re
import string

netnumber = "193.226.12"

# regular expressions
r = dict(map(lambda x: (x[0], re.compile(x[1])), (
("empty", "^\s*;*\s*$"),
("comment", "^\s*;+\s*(\S+.*)$"),
("reverse", "^\s*(\d{1,3})\s+IN\s+PTR\s+([A-Za-z0-9.-]+)\s*$"),
("reverse_free", "^\s*;\s*(\d{1,3})"),
("dns_origin", "^\s*\$ORIGIN\s+([A-Za-z0-9.-])\s*$"),
("dns", "\s*([A-Za-z0-9.-]+)\s+IN\s+((?:CNAME)|(?:A)|(?:TXT)|(?:NS)|(?:MX)|(?:HINFO))\s+(\S+)\s*"),
("dns_continued", "\s*IN\s+((?:CNAME)|(?:A)|(?:TXT)|(?:NS)|(?:MX)|(?:HINFO))\s+(\S+)\s*")
)))

# ips: 'ip_addr':(status, reverse, reverse_comment, direct, direct_comment)
ips = {}

import ipdb; ipdb.set_trace()

def makeip(net,host):
    return net+"."+host

# TODO: duplicate code in parse_dns and parse_reverse

def parse_dns(f):
    group = False
    domain=""
    for line in f:
        match = r["dns_origin"].match(line)
        if match:
            domain = match.group(1)
            continue
        if r["empty"].match(line):
            group = False
            continue
        match = r["comment"].match(line)
        if match:
            comment = match.group(1)
            group = True
            continue
        print "Warning: unfathomable line: ", line

def parse_reverse(f):
    group = False
    for line in f:
        match = r["reverse_free"].match(line)
        if match:
            hostnumber = match.group(1)
            ips[makeip(netnumber,hostnumber)] = ("free","","")
            continue
        match = r["reverse"].match(line)
        if match:
            hostnumber = match.group(1)
            fqdn = match.group(2)
            ips[makeip(netnumber,hostnumber)] = (
                "used", fqdn, comment if group else "")
            continue
        if r["empty"].match(line):
            group = False
            continue
        match = r["comment"].match(line)
        if match:
            comment = match.group(1)
            group = True
            continue
        print "Warning: unfathomable line: ", line

with open("master/0-24.12.226.193.in-addr.arpa") as f:
    parse_reverse(f)

#with open("master/cs.upt.ro") as f:
#    parse_dns(f)

for ip in sorted(ips.keys(), key=lambda x: int(x[x.rindex(".")+1:])):
    print ip,":",ips[ip]
