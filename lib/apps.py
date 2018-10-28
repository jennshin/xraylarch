import os
import sys
import numpy
import pkg_resources
from optparse import OptionParser

from pyshortcuts import make_shortcut
from pyshortcuts.shortcut import Shortcut

from .site_config import larchdir, home_dir, uname
from .shell import shell
from .xmlrpc_server import larch_server_cli

class LarchApp:
    """
    wrapper for Larch Application
    """
    def __init__(self, name, script, icon='larch', terminal=False):
        self.name = name
        self.script = script
        icon_ext = 'ico'
        if uname.startswith('darwin'):
            icon_ext = 'icns'
        self.icon = "%s.%s" % (icon, icon_ext)
        self.terminal = terminal
        bindir = 'bin'
        if uname.startswith('win'):
            bindir = 'Scripts'

        self.bindir = os.path.join(sys.prefix, bindir)
        self.icondir = os.path.join(larchdir, 'icons')

    def create_shortcut(self):
        try:
            script =os.path.join(self.bindir, self.script)
            scut = Shortcut(script, name=self.name, folder='Larch')
            make_shortcut(script, name=self.name,
                          icon=os.path.join(self.icondir, self.icon),
                          terminal=self.terminal,
                          folder='Larch')
            if uname.startswith('linux'):
                os.chmod(scut.target, 493)
        except:
            print("Warning: could not create shortcut to ", self.script)


APPS = (LarchApp('Larch CLI', 'larch', terminal=True),
        LarchApp('Larch GUI', 'larch --wxgui'),
        LarchApp('XAS Viewer',  'xas_viewer',  icon='onecone'),
        LarchApp('GSE Mapviewer', 'gse_mapviewer',  icon='gse_xrfmap'),
        LarchApp('GSE DTCorrect', 'gse_dtcorrect'),
        LarchApp('XRF Display',  'xrfdisplay',  icon='ptable'),
        LarchApp('Dioptas', 'dioptas', icon='dioptas'),
        LarchApp('2D XRD Viewer', 'diFFit2D'),
        LarchApp('1D XRD Viewer', 'diFFit1D') )


def make_desktop_shortcuts():
    """make desktop shortcuts for Larch apps"""
    for app in APPS:
        app.create_shortcut()


# entry points:
def run_gse_mapviewer():
    """GSE Mapviewer """
    from larch_plugins.wx import MapViewer
    os.chdir(home_dir)
    MapViewer().MainLoop()

def run_gse_dtcorrect():
    """GSE DT Correct """
    from larch_plugins.wx import DTViewer
    os.chdir(home_dir)
    DTViewer().MainLoop()


def run_xas_viewer():
    """XAS Viewer """
    from larch_plugins.xasgui import XASViewer
    os.chdir(home_dir)
    XASViewer().MainLoop()


def run_xrfdisplay():
    """ XRF Display"""
    from larch_plugins.wx import XRFApp
    os.chdir(home_dir)
    XRFApp().MainLoop()


def run_xrfdisplay_epics():
    """XRF Display for Epics Detectors"""
    from larch_plugins.epics import EpicsXRFApp
    os.chdir(home_dir)
    EpicsXRFApp().MainLoop()


def run_diffit1D():
    """XRD Display for 1D patternss"""
    from larch_plugins.diFFit.XRD1DViewer import diFFit1D
    os.chdir(home_dir)
    diFFit1D.MainLoop()


def run_diffit2D():
    """XRD Display for 2D patternss"""
    from larch_plugins.diFFit.XRD2DViewer import diFFit2D
    os.chdir(home_dir)
    diFFit2D.MainLoop()

def run_gse_dtcorrect():
    """GSE Deadtime corrections"""
    from larch_plugins.wx import DTViewer
    DTViewer().MainLoop()


def run_feff8l():
    "run feff8l"
    from larch_plugins.xafs.feffrunner import feff8l_cli
    feff8l_cli()


def run_larch_server():
    "run larch XMLRPC server"
    larch_server_cli()

## main larch cli or wxgui
def run_larch():
    """
    main larch application launcher, running either
    commandline repl program or wxgui
    """

    usage = "usage: %prog [options] file(s)"
    parser = OptionParser(usage=usage, prog="larch",
                          version="larch command-line version 0.2")

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                      default=False, help="set quiet mode, default = False")

    parser.add_option("-m", "--makeicons", dest="makeicons", action="store_true",
                      default=False, help="create desktop icons")

    parser.add_option("-x", "--nowx", dest="nowx", action="store_true",
                      default=False, help="set no wx graphics mode, default = False")

    parser.add_option("-e", "--exec", dest="noshell", action="store_true",
                      default=False, help="execute script only, default = False")

    parser.add_option("-r", "--remote", dest="server_mode", action="store_true",
                      default=False, help="run in remote server mode")

    parser.add_option("-p", "--port", dest="port", default='4966',
                      metavar='PORT', help="port number for remote server")

    parser.add_option("-w", "--wxgui", dest="wxgui", default=False,
                      action='store_true', help="run Larch GUI")

    parser.add_option("-c", "--echo", dest="echo", action="store_true",
                      default=False, help="tell remote server to echo commands")

    (options, args) = parser.parse_args()

    # create desktop icons
    if options.makeicons:
        make_desktop_shortcuts()

    # run in server mode
    elif options.server_mode:
        from larch.xmlrpc_server import LarchServer
        server = LarchServer(host='localhost', port=int(options.port))
        server.run()

    # run wx Larch GUI
    elif options.wxgui:
        from larch.wxlib.larchframe import LarchApp
        LarchApp().MainLoop()

    # run wx Larch CLI
    else:
        cli = shell(quiet=options.quiet, with_wx=(not options.nowx))
        # execute scripts listed on command-line
        if len(args)>0:
            for arg in args:
                cmd = "run('%s')" % arg
                if arg.endswith('.py'):
                    cmd = "import %s" %  arg[:-3]
                cli.default(cmd)

        # if interactive, start command loop
        if not options.noshell:
            try:
                cli.cmdloop()
            except ValueError:
                pass