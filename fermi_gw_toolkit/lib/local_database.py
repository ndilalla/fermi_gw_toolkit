import pickle
import json
import os

from fermi_gw_toolkit import GPL_TASKROOT

class gw_local_database(dict):
    
    def __init__(self, _dict):
        dict.__init__(self, _dict) 
    
    @staticmethod
    def check_extension(file_path):
        if not file_path.endswith('.pkl'):
            raise RuntimeError("Input file must have '.pkl' extension.")
    
    @staticmethod
    def create_empty(file_path):
        gw_local_database.check_extension(file_path)
        if not os.path.isfile(file_path):
            with open(file_path, 'wb') as file:
                pickle.dump({}, file)
        else:
            print(f"{file_path} already exists!")

    @classmethod
    def load(cls, infile):
        print("Loading the local database %s..." % infile)
        cls.check_extension(infile)
        with open(infile, 'rb') as f:
            _dict = pickle.load(f)
        return cls(_dict)

    def save(self, outfile):
        print("Saving the database to %s..." % outfile)
        with open(outfile, 'wb') as f:
            pickle.dump(dict(self), f)
    
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
    
    def show(self):
        print(json.dumps(self, indent=2, sort_keys=True))
    
    

if __name__ == '__main__':
    db_file = os.path.join(GPL_TASKROOT, 'databases', 'db_gw_O4_events.pkl')
    gw_local_database.create_empty(db_file)
    db = gw_local_database.load(db_file)
    db.show()
    #db.save(os.path.join(GPL_TASKROOT, 'databases', 'db_gw_events_copy.pkl'))
