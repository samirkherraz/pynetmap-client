#!/usr/bin/python
from threading import Lock


class Table:
    def __init__(self, name):
        self._head = None
        self._name = name
        self._lock = Lock()

    def get_data(self):
        return self._head

    def set_data(self, data):
        with self._lock:
            self._head = data

    def set(self, key, value):
        with self._lock:
            self._head[key] = value

    def get(self, key):
        try:
            return self._head[key]
        except:
            return key

    def set_attr(self, id, key, value):
        with self._lock:
            self._head[id][key] = value

    def get_attr(self, id, key):
        try:
            return self._head[id][key]
        except:
            return id

    def cleanup(self, lst=None):
        with self._lock:
            for k in self._head.keys():
                if lst != None and k not in lst:
                    del self._head[k]
                else:
                    for e in self._head[k].keys():
                        if not e.startswith(self._name):
                            del self._head[k][e]
            if lst != None:
                for k in lst:
                    if k not in self._head:
                        self._head[k] = {}

    def delete(self, key):
        with self._lock:
            try:
                del self._head[key]
            except:
                pass
