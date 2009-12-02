#Subject.py

class Subject:
    """Used to implement observer pattern"""
    
    def __init__(self):
        """constructor"""
        self._observers = []

    def attach(self, observer):
        """add an observer"""
        if not observer in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """remove an observer"""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, update, **kwargs):
        """notify all observers"""
        for observer in self._observers:
            observer.update(update, **kwargs)
