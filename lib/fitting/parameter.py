import numpy as np

class Parameter(object):
    """returns a parameter object: a floating point value with bounds that can
    be flagged as a variable for a fit, or given an expression to use to
    automatically evaluate its value (as a thunk).

    >>> x = param(12.0, vary=True, min=0)
    will set the value to 12.0, and allow it be varied by changing x._val,
    but its returned value will never go below 0.

    >>> x = param(expr='sqrt(2*a)')
    will have a value of sqrt(2*a) even if the value of 'a' changes after
    the creation of x
    """
    __invalid = "Invalid expression for parameter: '%s'"

    def __init__(self, val=0, min=None, max=None, vary=False,
                expr=None, _larch=None, name=None, **kws):
        self._val = val
        self._initval = val
        self.vary = vary
        self.min = min
        self.max = max
        self.name = name
        self._expr = expr
        self._ast = None
        self._larch = None
        if (hasattr(_larch, 'run') and
            hasattr(_larch, 'parse') and
            hasattr(_larch, 'symtable')):
            self._larch = _larch
        if self._larch is not None and name is not None:
            self._larch.symtable.set_symbol(name, self)

    @property
    def expr(self):
        return self._expr

    @expr.setter
    def expr(self, val):
        self._ast = None
        self._expr = val

    @property
    def value(self):
        return self._getval()

    @value.setter
    def value(self, val):
        self._val = val

    def _getval(self):
        if self._larch is not None and self._expr is not None:
            if self._ast is None:
                self._expr = self._expr.strip()
                self._ast = self._larch.parse(self._expr)
                if self._ast is None:
                    self._larch.writer.write(self.__invalid % self._expr)
            if self._ast is not None:
                self._val = self._larch.run(self._ast, expr=self._expr)
                # self._larch.symtable.save_frame()
                # self._larch.symtable.restore_frame()

        if self.min is None: self.min = -np.inf
        if self.max is None: self.max =  np.inf
        if self.max < self.min:
            self.max, self.min = self.min, self.max

        try:
            if self.min > -np.inf:
               self._val = max(self.min, self._val)
            if self.max < np.inf:
                self.value = min(self.max, self._val)
        except(TypeError, ValueError):
            self._val = np.nan

        return self._val

    def __hash__(self):
        return hash((self._getval(), self.min, self.max,
                     self.vary, self._expr))

    def __repr__(self):
        w = [repr(self._getval())]
        if self._expr is not None:
            w.append("expr='%s'" % self._expr)
        elif self.vary:
            w.append('vary=True')
        if self.min not in (None, -np.inf):
            w.append('min=%s' % repr(self.min))
        if self.max not in (None, np.inf):
            w.append('max=%s' % repr(self.max))
        return 'param(%s)' % ', '.join(w)

    #def __new__(self, val=0, **kws): return float.__new__(self, val)

    # these are more or less straight emulation of float,
    # but using _getval() to get current value
    def __str__(self):         return self.__repr__()

    def __abs__(self):         return abs(self._getval())
    def __neg__(self):         return -self._getval()
    def __pos__(self):         return +self._getval()
    def __nonzero__(self):     return self._getval() != 0

    def __int__(self):         return int(self._getval())
    def __long__(self):        return long(self._getval())
    def __float__(self):       return float(self._getval())
    def __trunc__(self):       return self._getval().__trunc__()

    def __add__(self, other):  return self._getval() + other
    def __sub__(self, other):  return self._getval() - other
    def __div__(self, other):  return self._getval() / other
    __truediv__ = __div__

    def __floordiv__(self, other):
        return self._getval() // other
    def __divmod__(self, other): return divmod(self._getval(), other)

    def __mod__(self, other):  return self._getval() % other
    def __mul__(self, other):  return self._getval() * other
    def __pow__(self, other):  return self._getval() ** other

    def __gt__(self, other):   return self._getval() > other
    def __ge__(self, other):   return self._getval() >= other
    def __le__(self, other):   return self._getval() <= other
    def __lt__(self, other):   return self._getval() < other
    def __eq__(self, other):   return self._getval() == other
    def __ne__(self, other):   return self._getval() != other

    def __radd__(self, other):  return other + self._getval()
    def __rdiv__(self, other):  return other / self._getval()
    __rtruediv__ = __rdiv__

    def __rdivmod__(self, other):  return divmod(other, self._getval())
    def __rfloordiv__(self, other): return other // self._getval()
    def __rmod__(self, other):  return other % self._getval()
    def __rmul__(self, other):  return other * self._getval()
    def __rpow__(self, other):  return other ** self._getval()
    def __rsub__(self, other):  return other - self._getval()

    #
    def as_integer_ratio(self):  return self._getval().as_integer_ratio()
    def hex(self):         return self._getval().hex()
    def is_integer(self):  return self._getval().is_integer()
    def real(self):        return self._getval().real()
    def imag(self):        return self._getval().imag()
    def conjugate(self):   return self._getval().conjugate()

    def __format__(self):  return format(self._getval())
    def fromhex(self, other):  self._val = other.fromhex()

    # def __getformat__(self, other):  return self._getval()
    # def __getnewargs__(self, other):  return self._getval()
    # def __reduce__(self, other):  return self._getval()
    # def __reduce_ex__(self, other):  return self._getval()
    # def __setattr__(self, other):  return self._getval()
    # def __setformat__(self, other):  return self._getval()
    # def __sizeof__(self, other):  return self._getval()
    # def __subclasshook__(self, other):  return self._getval()

def isParameter(x):
    return (isinstance(x, Parameter) or
            x.__class__.__name__ == 'Parameter')

def param_value(val):
    "get param value -- useful for 3rd party code"
    while isinstance(val, Parameter):
        val = val.value
    return val
