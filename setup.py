#!/usr/bin/env python
import os
import sys
try:
	import setuptools
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
from setuptools import setup, find_packages

sys.path.insert(0, '.')
import zicbee_mplayer
VERSION=zicbee_mplayer.__version__

setup (
        name='zicbee-mplayer',
        version=VERSION,
        author='Fabien Devaux',
        author_email='fdev31@gmail.com',
        url = 'http://zicbee.gnux.info/',
        download_url='http://zicbee.gnux.info/hg/index.cgi/zicbee-mplayer/archive/%s.tar.bz2'%VERSION,
        license='BSD',
        platform='all',
        description='MPlayer backend for zicbee project',
        long_description='''
        With this package you can play your music in zicbee if mplayer is installed on your system
        ''',
        keywords = 'database music tags metadata management',
        packages = find_packages(),

        entry_points = """
        [zicbee.player]
        mplayer = zicbee_mplayer:Player
        """,

        dependency_links = [
            'eggs',
            'http://zicbee.gnux.info/files/',
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

