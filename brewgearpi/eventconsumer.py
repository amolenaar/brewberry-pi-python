
class EventConsumers(object):

    def __init__(self):
        self._consumers = []

    def add(self, consumer):
        self._consumers.append(consumer)

    def remove(self, consumer):
        self._consumers.remove(consumer)

    def notify(self, **kwargs):
        for c in self._consumers:
            c(**kwargs)

# vim:sw=4:et:ai
