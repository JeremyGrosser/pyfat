from struct import unpack
from os import SEEK_SET
import sys

class FAT32(object):
	def __init__(self, fd):
		self.fd = fd

		self.boot = self.parse_boot_sector(fd.read(36))
		self.boot.update(self.parse_fat32_boot(fd.read(476)))
	
	def get_cluster(self, num):
		cluster_size = self.boot['bytes_per_sector'] * self.boot['sectors_per_cluster']
		self.fd.seek(cluster_size * num, SEEK_SET)
		return self.fd.read(cluster_size)
	
	def parse_cluster(self, num):
		cluster = self.get_cluster(num)
		fat = cluster[:8]
		return fat
	
	def parse_boot_sector(self, block):
		info = {}
		data = unpack('<3c8sHcHcHHcHHHII', block)
		info['oemname'] = data[3].strip(' ')
		info['bytes_per_sector'] = data[4]
		info['sectors_per_cluster'] = ord(data[5])
		info['reserved_sector_count'] = data[6]
		info['num_tables'] = ord(data[7])
		info['max_root_entries'] = data[8]

		info['total_sectors'] = data[9]
		if info['total_sectors'] == 0:
			info['total_sectors'] = data[15]

		info['media_descriptor'] = ord(data[10])
		info['sectors_per_fat'] = data[11]
		info['sectors_per_track'] = data[12]
		info['num_heads'] = data[13]
		info['hidden_sectors'] = data[14]
		return info
	
	def parse_fat32_boot(self, block):
		info = {}
		data = unpack('<IHHIHH12scccI11s8s420s2s', block)
		info['sectors_per_fat'] = data[0]
		info['fat_flags'] = data[1]
		info['version'] = data[2]
		info['root_start'] = data[3]
		info['info_start'] = data[4]
		info['boot_start'] = data[5]
		#info['reserved'] = data[6]
		info['drive_num'] = ord(data[7])
		#info['reserved'] = ord(data[8])
		info['extended_signature'] = ord(data[9])
		info['serial'] = data[10]
		info['volume_label'] = data[11]
		info['fstype'] = data[12]
		info['boot_code'] = data[13]
		info['boot_signature'] = data[14]
		return info

if __name__ == '__main__':
	fs = FAT32(file('sdc.bin', 'rb'))

	for k, v in fs.boot.items():
		print '%s: %s' % (k, repr(v))

	print repr(fs.get_cluster(fs.boot['reserved_sector_count']))
	
	#last_cluster = fs.boot['total_sectors'] / fs.boot['sectors_per_cluster']
	#print 'last cluster:', last_cluster
	#for i in xrange(2, last_cluster):
	#	data = fs.get_cluster(i)
	#	if data != '\xff' * 4096 and data != '\x00' * 4096:
	#		print i, repr(fs.parse_cluster(i))
