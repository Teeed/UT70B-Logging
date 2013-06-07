# -*- coding: utf-8 -*-

# Appplication that parses RAW data from UT70B and outputs as XLS (tab separated)
# Copyright (C) 2013 Tadeusz Magura-Witkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys, binascii, struct
from time import time


buff = bytearray()
no = 0
ld = (0, 0, 0, 0)

print "No\tTime\tDC/AC\tValue\tUnit\tAUTO"

def p_data(dc_ac, value, unit, auto):
	global no, ld
	no += 1

	if ld[0] == dc_ac and ld[1] == value and ld[2] == unit and ld[3] == auto:
		return
		
	print "%s\t%s\t%s\t%s\t%s\t%s" % (no, int(time()), dc_ac, str(value).replace('.', ','), unit, auto)

	ld = (dc_ac, value, unit, auto)

while True:
	data = sys.stdin.read(11)
	buff += data

	# find the last good data
	lastpos = buff.rfind('\x0d\x0a')
	if len(buff) < 11 or lastpos < 11:
		continue

	packet = buffer(buff, lastpos-9, 11)
	buff = bytearray()

	rang, digit3, digit2, digit1, digit0, function, status, option1, option2, xr, xn = struct.unpack('BBBBBBBBBcc', packet)

	digit0 -= 48
	digit1 -= 48
	digit2 -= 48
	digit3 -= 48
	value = digit0 + digit1*10 + digit2*100 + digit3*1000

	unit = 'NULL'
	dc_ac = 'NULL'
	multipler = 1

	if status&(1<<2): # negative reading
		value *= -1

	if function == 0b00110100: # temperature
		unit = 'C' if status&(1<<3) else 'F'
	elif function == 0b00111011: # voltage
		unit = 'V'
		dc_ac = 'DC' if option2&(1<<3) else 'AC' if option2&(1<<2) else 'NULL'

		if rang == 0b00110000: # mV
			unit = 'mV'
			multipler = .1
		else:
			multipler = pow(.1, 4-(rang&0b00000111))

	value *= multipler

	if status&(1<<0): # overflow
		value = 'OL'

	p_data(dc_ac, value, unit, 'AUTO' if option2&0b0100000 else 'MANUAL')
