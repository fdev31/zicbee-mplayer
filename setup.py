#!/usr/bin/env python
import os
import sys
try:
	import setuptools
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
from setuptools import setup, find_packages

VERSION='0.9-wip'

setup (
        name='zicbee-mplayer',
        version=VERSION,
        author='Fabien Devaux',
        author_email='fdev31@gmail.com',
        url = 'http://box.gnux.info/zicbee/',
        download_url='http://box.gnux.info/hg/index.cgi/zicbee-player/archive/wip.tar.bz2',
        license='BSD',
        platform='all',
        description='MPlayer backend for zicbee project',
        long_description='''
ZicBee is a project grouping multiple applications to manage play and handle music databases.
It takes ideas from Quodlibet and Mpd, both very good music mplayers with their own strengths.

For now there is a Swiss-army knife tool: zicdb

Some plugins for quodlibet has also be developed. ZicBee is fast,
portable (but not very ported...) and flexible.

While the project is stable and usable (there are online docs and a nice www gui),
it's mostly interesting for hackers and developers from now, I didn't confront to real users yet :P

See features list, it's mostly handy for people with large databases,
with optionally multiple computers.
It can be adapted to handle video too, hacking some bit of code.
        ''',
        keywords = 'database music tags metadata management',
        packages = find_packages(),

        entry_points = """
        [zicbee.player]
        mplayer = zicbee_mplayer.mp:MPlayer
        """,

        dependency_links = [
            'eggs',
            'http://box.gnux.info/zicbee/files/',
            'http://webpy.org/',
            'http://buzhug.sourceforge.net/',
            'http://code.google.com/p/quodlibet/downloads/list',
#            'http://sourceforge.net/project/showfiles.php?group_id=167078&package_id=190037&release_id=664931',
#            'http://code.google.com/p/pyglet/downloads/list',
            ],
        classifiers = [
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
#                'Intended Audience :: End Users/Desktop',
                'Operating System :: OS Independent',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Programming Language :: Python',
                'Environment :: Console',
                'Environment :: No Input/Output (Daemon)',
                'Environment :: X11 Applications',
                'Natural Language :: English',
                'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
                'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                'Topic :: Software Development',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: Multimedia :: Sound/Audio :: Players',
                'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
                'Topic :: Text Processing :: Markup',
                'Topic :: Utilities',
                ],

        )

if 'build' in sys.argv or 'install' in sys.argv or any(a for a in sys.argv if 'dist' in a):
    # test copied from zicbee/player/_mpgen.py [and mp.py]:
    exe_name = 'mplayer' if os.sep == '/' else 'mplayer.exe'
    import subprocess
    try:
        ret = subprocess.Popen([exe_name, '-really-quiet']).wait()
    except OSError:
        ret = 255
    if ret:
        dec = "*"*80
        print dec
        print dec
        print ''
        print "* WARNING !! mplayer seems not accessible, please install properly."
        print dec
        print "* YOU NEED MPLAYER IN YOUR PATH TO GET PLAYER FEATURES"
        print ''
        print dec
        print dec

