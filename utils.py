class Buffer:
    """A simple circular buffer"""

    def __init__(self, maxlen, data=None):
        if maxlen < 1:
            raise ValueError("maxlen must be at least 1")

        self.maxlen = maxlen
        self.data = [] if data is None else list(data)[:maxlen]
        self.pos = len(self.data)

    def __getitem__(self, index):
        """Get element by index, relative to most recently pushed value"""
        return self.data[(self.pos - 1 + index) % len(self.data)]

    def __repr__(self):
        return f"Buffer(pos={self.pos}, maxlen={self.maxlen}, data={self.data})"

    def __iter__(self):
        """Iterator from oldest to newest value"""
        for i in range(len(self.data)):
            yield self.__getitem__(i + 1)

    def push(self, e):
        if len(self.data) == self.maxlen:
            self.data[self.pos] = e
        else:
            self.data.append(e)
        self.pos = (self.pos + 1) % self.maxlen

    def clear(self):
        self.pos = 0
        self.data = []