#!/usr/bin/python -u
import telnetlib
from time import sleep

tn = telnetlib.Telnet('dict.org', 2628)
sleep(1)
tn.write('define ! one\r\n')
sleep(1)
print tn.read_very_eager()
tn.write('define ! two\r\n')
sleep(1)
print tn.read_very_eager()
tn.write('define ! three\r\n')
sleep(1)
print tn.read_very_eager()
