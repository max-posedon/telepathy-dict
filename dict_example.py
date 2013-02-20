#!/usr/bin/python -u
import telnetlib

tn = telnetlib.Telnet('dict.org', 2628)
print tn.read_very_eager()
tn.write('AUTH max_posedon xxx')
print tn.read_all()
