from template import plugin, iterator

class Table(plugin.Plugin):
  def __init__(self, context, data, params=None):
    if isinstance(data, iterator.Iterator):
      data, error = data.get_all()
      if error:
        return self.error("iterator failed to provide data for table: %s" %
                          error)
    if not isinstance(data, (tuple, list)):
      return self.error("invalid table data, expecting a list")

    if params is None:
      params = {}
    if not isinstance(params, dict):
      return self.error("invalid table parameters, expecting a dict")

    # ensure keys are folded to upper case
    params.update(dict((str(key).upper(), value)
                  for key, value in params.iteritems()))

    size = len(data)
    overlap = params.get("OVERLAP", 0)

    rows = params.get("ROWS")
    cols = params.get("COLS")
    if rows:
      if size < rows:
        rows = size
        cols = 1
        coloff = 0
      else:
        coloff = rows - overlap
        cols = size / coloff + int(size % coloff > overlap)
    elif cols:
      if size < cols:
        cols = size
        rows = 1
        coloff = 1
      else:
        coloff = size / cols + int(size % cols > overlap)
        rows = coloff + overlap
    else:
      rows = size
      cols = 1
      coloff = 0

    self._DATA = data
    self._SIZE = size
    self._NROWS = rows
    self._NCOLS = cols
    self._COLOFF = coloff
    self._OVERLAP = overlap
    self._PAD = params.get("PAD")
    if self._PAD is None:
      self._PAD = 1

  def row(self, row=None):
    if row is None:
      return self.rows()
    if row >= self._NROWS or row < 0:
      return None
    index = row
    set = []
    for c in range(self._NCOLS):
      if index < self._SIZE:
        set.append(self._DATA[index])
      elif self._PAD:
        set.append(None)
      index += self._COLOFF
    return set

  def col(self, col=None):
    if col is None:
      return self.cols()
    if col >= self._NCOLS or col < 0:
      return None
    blanks = 0
    start = self._COLOFF * col
    end = start + self._NROWS - 1
    if end < start:
      end = start
    if end >= self._SIZE:
      blanks = end - self._SIZE + 1
      end = self._SIZE - 1
    if start >= self._SIZE:
      return None
    set = self._DATA[start:end+1]
    if self._PAD:
      set.extend([None] * blanks)
    return set

  def rows(self):
    return [row for row in [self.row(x) for x in range(self._NROWS)]
            if row is not None]

  def cols(self):
    return [col for col in [self.col(x) for x in range(self._NCOLS)]
            if col is not None]

  def data(self):
    return self._DATA

  def size(self):
    return self._SIZE

  def nrows(self):
    return self._NROWS

  def ncols(self):
    return self._NCOLS

  def overlap(self):
    return self._OVERLAP

  def pad(self):
    return self._PAD

table = Table
