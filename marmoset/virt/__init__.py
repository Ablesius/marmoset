from contextlib import contextmanager, closing
from functools import wraps
from os import path
from re import match
import libvirt
from .exceptions import Error
import xml.etree.ElementTree as ET
from string import Template


URI = 'qemu:///system'


@contextmanager
def connection():
    """
    Return a contextmanager for a libvirt connection.
    """
    with closing(libvirt.open(URI)) as conn:
        yield conn

def with_unit(value):
    """
    Return a string of the converted numerical @value with the proper
    unit name.
    """
    units = ['b', 'KiB', 'MiB', 'GiB', 'TiB']
    for unit in units:
        if value < 1024 or unit == units[-1]: break
        value = value / 1024
    return "%d %s" % (value, unit)

def parse_unit(obj):
    """
    Return value as int and unit as string parsed from @obj.
    @obj may be an int, which will always return 'b' as unit, or a
    string, which will be parsed for a unit (defaults to 'b' as well).
    """
    if obj is str:
        m = match('^(\d+) *(\w+)?$', obj)
        if m:
            value, unit = m.groups() 
    else:
        value, unit = obj, None
    return int(value), (unit if unit else 'b')


class Virt:

    TEMPLATE_DIR = path.join(path.dirname(__file__), 'templates')

    @classmethod
    def template_file(cls):
        file_name = cls.__name__.lower() + '.xml'
        return path.join(cls.TEMPLATE_DIR, file_name)

    @classmethod
    def xml_template(cls, **substitutes):
        with open(cls.template_file()) as f:
            template = Template(f.read())
        return template.substitute(substitutes)


    def attributes(self):
        attrs = {}
        for name, func in self.__class__.__dict__.items():
            if isinstance(func, property):
                value = getattr(self, name)
                if isinstance(value, list):
                    attrs[name] = [v.attributes() for v in value]
                else:
                    attrs[name] = value
        return attrs
       

class Parent(Virt):

    _func = {}

    @classmethod
    def all(cls):
        """
        Return a list with all instances. In order to work, the
        resource must provide the class variable 'func', which has to
        be a dict with at least the key 'all' and the the name of the
        libvirt function to call as value.
        """
        with connection() as conn:
            all = getattr(conn, cls._func['all'])()
        return [cls(i) for i in all]

    @classmethod
    def find_by(cls, attr, value):
        """"
        Return a class instance identified by specific attribute.
        
        @attr: identifier attribute
        @value: value to search for
        
        In order to work, the resource must provide the class variable
        'func', which has to be a dict with at least the name ot the 
        attributes to search for (like id, uuid, name) as keys and the
        respective libvirt function name to call as values.
        """
        with connection() as conn:
            try:
                funcname = cls._func[attr]
                func = getattr(conn, funcname)
                return cls(func(value))
            except KeyError:
                message = "dynamic finder method for attr '%s' not implemented"
                raise Exception(message % attr)
            except libvirt.libvirtError:
                return None


    def __init__(self, resource):
        self._resource = resource

    def get_xml(self, node=None):
        """
        Return the XML description of the libvirt instance. If @node is
        given, only the child node is returned instead of the root node.
        """
        xml = ET.fromstring(self._resource.XMLDesc())
        return xml if node is None else xml.find(node)


class Child(Virt):

    def __init__(self, xml, parent):
        """
        @xml: Libvirt XML Description of the resource part
        @parent: Parent object instance the child belongs to
        """
        self._xml = xml
        self._parent = parent


from .domain import Domain
from .network import Network
from .storage import Storage
from . import subparser

