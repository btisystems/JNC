"""
Created on 16 jul 2012

@author: emil@tail-f.com

PyUnit is needed to run these tests.

To run, stand in project dir and enter:
$ python -m unittest discover -v
"""
import unittest

from pyang.plugins import jpyang  #@UnresolvedImport
from pyang.statements import Statement
from pyang import FileRepository
from pyang import Context


class DummyOption(object):
    """Used to initialize Context with option fields in test setUp"""
    
    def __init__(self, directory, debug, verbose):
        """Sets the directory field to the supplied value"""
        self.directory = directory
        self.debug = debug
        self.verbose = verbose


class Test(unittest.TestCase):
    """Contains all JPyang tests"""

    def setUp(self):
        """Runs before each test"""
        # Initialize context with directory 'gen'
        repo = FileRepository()
        self.ctx = Context(repo)
        self.ctx.opts = DummyOption('gen', False, False)
        
        ###### Construct a statement tree rooted at m
        
        # Module m with prefix p, container c and typedef t children
        self.m = Statement(None, None, None, 'module', arg='m')
        self.ns = Statement(self.m, self.m, None, 'namespace', arg='ns')
        self.p = Statement(self.m, self.m, None, 'prefix', arg='root-m')
        self.c = Statement(self.m, self.m, None, 'container', arg='c')
        self.t = Statement(self.m, self.m, None, 'typedef', arg='t')
        self.m.substmts = [self.p, self.ns, self.c, self.t]
        
        # list and leaf children of c
        self.l = Statement(self.m, self.c, None, 'list', arg='l')
        self.leaf = Statement(self.m, self.c, None, 'leaf', arg='leaf')
        self.c.substmts = [self.l, self.leaf]
        
        # type child of t
        self.ty = Statement(self.m, self.t, None, 'type', arg='int32')
        self.t.substmts = [self.ty]
        
        # key and leaf children of c/l
        self.key = Statement(self.m, self.l, None, 'key', arg='k my')
        self.k = Statement(self.m, self.l, None, 'leaf', arg='k')
        self.my = Statement(self.m, self.l, None, 'leaf', arg='my')
        self.l.substmts = [self.key, self.k, self.my]
        
        # type child of c/leaf
        self.leafty = Statement(self.m, self.leaf, None, 'type', arg='string')
        self.leaf.substmts = [self.leafty]
        
        # type child of c/l/k
        self.kty = Statement(self.m, self.k, None, 'type', arg='string')
        self.k.substmts = [self.kty]
        
        # type child of c/l/my
        self.myty = Statement(self.m, self.my, None, 'type', arg='t')
        self.myty.i_typedef = self.t
        self.my.substmts = [self.myty]
        
        ########
        
        # Create new Method Generators for the top level statements
        self.cgen = jpyang.MethodGenerator(self.c, self.ctx)
        self.lgen = jpyang.MethodGenerator(self.l, self.ctx)
        self.tgen = jpyang.MethodGenerator(self.t, self.ctx)

    def tearDown(self):
        """Runs after each test"""
        pass

    def testSetUp(self):
        """Statement tree in this test is properly constructed"""
        mystr = lambda l: str(map(lambda ll: map(lambda s: s.arg, ll), l))
        res = map(self.m.search, ['prefix', 'container', 'typedef'])
        assert res == [[self.p], [self.c], [self.t]], 'was: ' + mystr(res)
        res = map(self.c.search, ['list', 'leaf'])
        assert res == [[self.l], [self.leaf]], 'was: ' + mystr(res)
        res = map(self.t.search, ['type'])
        assert res == [[self.ty]], 'was: ' + mystr(res)
        res = map(self.l.search, ['key', 'leaf'])
        assert res == [[self.key], [self.k, self.my]], 'was: ' + mystr(res)
        self.stmt_type = self.leaf.search_one('type')
        assert self.stmt_type and self.stmt_type.arg == 'string'

    def testInit(self):
        """Values correct in Java Methods created in different ways"""
        return NotImplemented

    def testClone(self):
        """Clones have equal string representation but different reference"""
        method = self.cgen.empty_constructor()
        clone = method.clone()
        assert method is method, 'Sanity check'
        assert method == method, 'method.__eq__ should return True'
        assert method is not clone, 'Different reference'
        assert method != clone, 'method.__eq__ should (maybe) return False'
        assert method.as_string() == clone.as_string(), 'Same string repr'


if __name__ == "__main__":
    """Launch all unit tests"""
    #import sys;sys.argv = ['', 'Test.testCapitalize_first']  # Only one
    unittest.main()