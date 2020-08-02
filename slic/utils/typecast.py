
def downcast(obj, cls):
    """Downcast (specialize/narrow) object obj to child type cls"""
    obj_cls = type(obj)
    _ensure_inheritance(obj_cls, cls)
    return _cast(obj, cls)

def upcast(obj, cls):
    """Upcast (generalize/widen) object obj to parent type cls"""
    obj_cls = type(obj)
    _ensure_inheritance(cls, obj_cls)
    return _cast(obj, cls)

def _ensure_inheritance(parent_cls, child_cls):
    if not _is_parent(parent_cls, child_cls):
        _raise_error(parent_cls, child_cls)

def _is_parent(parent_cls, child_cls):
    all_parents = child_cls.__mro__
    return parent_cls in all_parents

def _raise_error(parent_cls, child_cls):
    parent_cls_name = parent_cls.__name__
    child_cls_name = child_cls.__name__
    raise TypeError(f"class {child_cls_name} is not a subclass of {parent_cls_name}")

def _cast(obj, cls):
    obj.__class__ = cls
    return obj





if __name__ == "__main__":

    class A:
        pass


    class B:
        def methB(self):
            return 1

    class S(B):
        def methS(self):
            res = self.methB()
            return (res, 2)

    class SS(S):
        def methSS(self):
            res1 = self.methB()
            res2 = self.methS()
            return (res1, res2, 3)


    b = B()

    #b.__class__ = SS
    downcast(b, SS)

    assert b.methB() == 1
    assert b.methS() == (1, 2)
    assert b.methSS() == (1, (1, 2), 3)


    a = A()

    try:
        downcast(a, SS)
    except TypeError as e:
        print(e)
    else:
        raise AssertionError

    try:
        upcast(a, SS)
    except TypeError as e:
        print(e)
    else:
        raise AssertionError


    b2 = B()

    try:
        upcast(b2, SS)
    except TypeError as e:
        print(e)
    else:
        raise AssertionError


    ss = SS()

    upcast(ss, B)

    assert ss.methB() == 1
    assert not hasattr(ss, "methS")
    assert not hasattr(ss, "methSS")



