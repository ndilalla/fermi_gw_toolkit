
import os
from fermi_gw_toolkit import GPL_TASKROOT
from fermi_gw_toolkit.lib.local_database import gw_local_database

def check_event(key, threshold=250129):
    event_name, version = key.split('/')
    date = int(event_name[3:9])
    if int(date) >= threshold:
        return True
    return False

db_file_o4b = os.path.join(GPL_TASKROOT, 'gw', 'databases', 'db_gw_O4b_events.json')
db_file_o4c = os.path.join(GPL_TASKROOT, 'gw', 'databases', 'db_gw_O4c_events.json')

gw_local_database.create_empty(db_file_o4c)
db_o4b = gw_local_database.load(db_file_o4b, locking=True, timeout=10)
db_o4c = gw_local_database.load(db_file_o4c, locking=True, timeout=10)

for key, value in db_o4b.items():
    if check_event(key):
        db_o4c[key] = value
        print(f"Copying {key} to O4c database.")
        #input()
db_o4c.save(db_file_o4c)
db_o4b.release_lock()
db_o4c.release_lock()