import pickle
import json
import os

class gw_local_database(dict):
    
    def __init__(self, _dict):
        dict.__init__(self, _dict)
    
    @classmethod
    def load(cls, infile):
        print "Loading the local database %s..." % infile
        with open(infile, 'rb') as f:
            _dict = pickle.load(f)
        return cls(_dict)
    
    def save(self, outfile):
        print "Saving the database to %s..." % outfile
        with open(outfile, 'wb') as f:
            pickle.dump(dict(self), f)
    
    def _get_key(self, name, version):
        return '%s/%s' % (name, version)
    
    def initialize(self, name, version):
        _key = self._get_key(name, version)
        if not _key in self:
            self[_key] = {'Name' : name, 'Version' : version}
    
    def update(self, name, version, _dict):
        self.initialize(name, version)
        _key = self._get_key(name, version)
        self[_key].update(_dict)
    
    def get(self, name, version, key):
        _key = self._get_key(name, version)
        return self[_key].get(key, None)
    
    def set(self, name, version, key, value):
        self.initialize(name, version)
        _key = self._get_key(name, version)
        self[_key][key] = value
    
    def show(self):
        print json.dumps(self, indent=2, sort_keys=True)
    
    

if __name__ == '__main__':
    nfs_home='/nfs/farm/g/glast/u26/GWPIPELINE'
    db_file = os.path.join(nfs_home, 'output', 'db_gw_events.pkl')
    db = gw_local_database.load(db_file)
    db.show()
    #db.save(os.path.join(nfs_home, 'output', 'db_gw_events_copy.pkl'))
