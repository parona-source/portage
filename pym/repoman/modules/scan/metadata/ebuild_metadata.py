# -*- coding:utf-8 -*-

'''Ebuild Metadata Checks'''

import re
import sys

if sys.hexversion >= 0x3000000:
	basestring = str

from repoman.modules.scan.scanbase import ScanBase
from repoman.qa_data import missingvars

NON_ASCII_RE = re.compile(r'[^\x00-\x7f]')


class EbuildMetadata(ScanBase):

	def __init__(self, **kwargs):
		self.qatracker = kwargs.get('qatracker')

	def invalidchar(self, **kwargs):
		ebuild = kwargs.get('ebuild').get()
		for k, v in ebuild.metadata.items():
			if not isinstance(v, basestring):
				continue
			m = NON_ASCII_RE.search(v)
			if m is not None:
				self.qatracker.add_error(
					"variable.invalidchar",
					"%s: %s variable contains non-ASCII "
					"character at position %s" %
					(ebuild.relative_path, k, m.start() + 1))
		return False

	def missing(self, **kwargs):
		ebuild = kwargs.get('ebuild').get()
		live_ebuild = kwargs.get('live_ebuild').get()
		for pos, missing_var in enumerate(missingvars):
			if not ebuild.metadata.get(missing_var):
				if kwargs.get('catdir') == "virtual" and \
					missing_var in ("HOMEPAGE", "LICENSE"):
					continue
				if live_ebuild and missing_var == "KEYWORDS":
					continue
				myqakey = missingvars[pos] + ".missing"
				self.qatracker.add_error(myqakey, '%s/%s.ebuild'
					% (kwargs.get('xpkg'), kwargs.get('y_ebuild')))
		return False

	def old_virtual(self, **kwargs):
		ebuild = kwargs.get('ebuild').get()
		if ebuild.metadata.get("PROVIDE"):
			self.qatracker.add_error("virtual.oldstyle", ebuild.relative_path)
		return False

	def virtual(self, **kwargs):
		ebuild = kwargs.get('ebuild').get()
		if kwargs.get('catdir') == "virtual":
			for var in ("HOMEPAGE", "LICENSE"):
				if ebuild.metadata.get(var):
					myqakey = var + ".virtual"
					self.qatracker.add_error(myqakey, ebuild.relative_path)
		return False

	@property
	def runInPkgs(self):
		return (False, [])

	@property
	def runInEbuilds(self):
		return (True, [self.invalidchar, self.missing, self.old_virtual, self.virtual])
