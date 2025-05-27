import hashlib

class Hash:
    def __init__(self):
        pass

    def HT(self, mess):
        m = hashlib.sha256()
        m.update(mess.encode('utf-8'))
        return m.hexdigest()

    def HF(self, path):
        m = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                m.update(chunk)
        return m.hexdigest()