
from os.path import join
from bids import BIDSLayout, BIDSValidator
from bids.layout import parse_file_entities
from bids.tests import get_test_data_path
from bids.variables import variables

from sparc_me import Dataset

# import bids and associated metadata
layout = BIDSLayout('bids-examples/ds001')

# BIDS validator (limited edition!)
#pattern = "sub-{subject}[_run-{run}]_{suffix<z>}.nii.gz",
#entities = {
#   'subject': '01',
#   'suffix': 'T1w'
#}
#sel_bidsfile = layout.build_path(entities, pattern, validate=False)

sel_bidsfile = layout.get(extension='.nii.gz')[0]
entries = parse_file_entities(sel_bidsfile)
print('sel BIDS file entries=', entries)

#validator = BIDSValidator()
#validator.is_bids(sel_bidsfile)

subjlist = layout.get_subjects()
entities = layout.get_entities()

# get() to fetch a filename and its entries
sel_file = layout.get(suffix='participants')[0]
print('sel file=', sel_file)

all_me = sel_file.get_entities(metadata='all')
print(all_me)
#rint(all_files[1].get_metadata())
