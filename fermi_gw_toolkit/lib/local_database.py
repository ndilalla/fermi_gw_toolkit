import pickle
import json
import os

from filelock import Timeout, FileLock

from fermi_gw_toolkit import GPL_TASKROOT

class gw_local_database(dict):
    
    def __init__(self, _dict):
        dict.__init__(self, _dict)

    @staticmethod
    def get_obs_run(file_path):
        if 'O3' in os.path.basename(file_path):
            return 'O3'
        elif 'O4a' in os.path.basename(file_path):
            return 'O4a'
        elif 'O4b' in os.path.basename(file_path):
            return 'O4b'
        else:
            raise RuntimeError("Unknown observing run in db file %s" %\
                               os.path.basename(file_path))

    @staticmethod
    def check_extension(file_path):
        if file_path.endswith('.pkl'):
            return '.pkl'
        elif file_path.endswith('.json'):
            return '.json'
        else:
            raise RuntimeError("Database must have '.pkl' or '.json' extension.")
    
    @staticmethod
    def create_empty(file_path):
        gw_local_database.check_extension(file_path)
        if not os.path.isfile(file_path):
            db = gw_local_database({})
            db.save(file_path)
        else:
            print(f"{file_path} already exists!")

    @classmethod
    def load(cls, file_path, locking=True, **kwargs):
        print("Loading the local database %s..." % file_path)
        ext = cls.check_extension(file_path)
        if locking:
            lock_path = file_path.replace(ext, '.lock')
            cls.acquire_lock(cls, lock_path, **kwargs)
        if file_path.endswith('.pkl'):
            with open(file_path, 'rb') as f:
                _dict = pickle.load(f)
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                _dict = json.load(f)
        c = cls(_dict)
        c.obs_run = c.get_obs_run(file_path)
        return c

    def save(self, file_path, protocol=2):
        self.check_extension(file_path)
        print("Saving the database to %s..." % file_path)
        if file_path.endswith('.pkl'):
            with open(file_path, 'wb') as outfile:
                pickle.dump(dict(self), outfile, protocol=protocol)
        elif file_path.endswith('.json'):
            json_object = json.dumps(self, indent=2, sort_keys=True)
            with open(file_path, 'w') as outfile:
                outfile.write(json_object)
        self.release_lock()
    
    def acquire_lock(self, lock_path, **kwargs):
        args = (kwargs.get('timeout', -1), kwargs.get('poll_interval', 5))
        self.lock = FileLock(lock_path)
        try:
            self.lock.acquire(*args, blocking=True)
            print('Lock acquired.')
        except Timeout:
            raise RuntimeError("Could not acquire the lock to open the database.")

    def release_lock(self, force=False):
        if hasattr(self, 'lock'):
            if self.lock.is_locked:
                self.lock.release(force)
                print('Lock released.')
                #os.chmod(self.lock.lock_file, 0o0777)

    
    def get_key(self, name, version):
        return '%s/%s' % (name, version)
    
    def initialize(self, name, version):
        _key = self.get_key(name, version)
        if not _key in self:
            self[_key] = {'Name' : name, 'Version' : version}
    
    def update(self, name, version, _dict):
        """ Update the internal dictionary
        """
        self.initialize(name, version)
        _key = self.get_key(name, version)
        self[_key].update(_dict)
    
    def get_value(self, name, version, key):
        _key = self.get_key(name, version)
        return self[_key].get(key, None)
    
    def set_value(self, name, version, key, value):
        """ Set a single key/value of the internal dictionary
        """
        self.initialize(name, version)
        _key = self.get_key(name, version)
        self[_key][key] = value
    
    def dump(self, name, version):
        _key = self.get_key(name, version)
        return json.dumps(self[_key], indent=4)
    
    def show(self, name=None, version=None):
        if name is not None and version is not None:
            print(self.dump(name, version))
        else:
            print(json.dumps(self, indent=4, sort_keys=True))
    
if __name__ == '__main__':
    from fermi_gw_toolkit.utils.slack import send_chat
    #db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4a_events.json')
    db_file = os.path.join(GPL_TASKROOT, 'gw', 'databases', 'test_O4a.json')
    gw_local_database.create_empty(db_file)
    db = gw_local_database.load(db_file, locking=False, timeout=10)
    db.release_lock()
    # print(db.obs_run)
    #name = 'bnS240116z'
    #version = 'v01'
    #msg = "Event details:\n %s" % db.dump(name, version)
    #print(msg)
    # send_chat(msg, channel='bot-testing')
    # db.save(os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4b_events.json'))
