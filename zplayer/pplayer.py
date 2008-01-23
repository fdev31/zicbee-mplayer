#!/usr/bin/env python
# http://www.micahcarrick.com/12-24-2007/gtk-glade-tutorial-part-1.html

import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

import mp
import gobject
import urllib
import random
import traceback

from zicdb.zshell import duration_tidy
from pkg_resources import resource_filename

class DelayedAction(object):
    def __init__(self, fn, *args, **kw):
        self.fn = fn
        self.args = args
        self.kw = kw
        self.running = None
        self._delay = 1

    def _run(self):
        try:
            self.fn(*self.args, **self.kw)
            self.running = None
        except Exception, e:
            traceback.print_stack()
            traceback.print_exc()
        return False

    def start(self, delay):
        """ start action after 'delay' seconds. """
        self.stop()
        self.running = gobject.timeout_add(int(delay*1000), self._run)

    def stop(self):
        if self.running is not None:
            gobject.source_remove(self.running)
        self.running = None

class PPlayer(object):

    def __init__(self):
        self.player = mp.MPlayer()
        self.playlist = []
        self._cur_song_pos = -1
        gobject.timeout_add(1666, self._tick_generator().next)
        self._running = False
        self._paused = False
        self._position = None
        self._play_timeout = DelayedAction(self._play_now)
        self._seek_action = DelayedAction(self._seek_now)

        self._wtree = gtk.glade.XML(resource_filename('zplayer', 'pplayer.glade'))

        self.win = self._wtree.get_widget('main_window')
        self.list_w = self._wtree.get_widget('songlist_tv')
        self.list_store = gtk.ListStore(str, str, str)
        self.list_w.set_model(self.list_store)
        for i, name in enumerate(('Artist', 'Album', 'Title')):
            col = gtk.TreeViewColumn(name, gtk.CellRendererText(), text=i)
            col.set_resizable(True)
            self.list_w.append_column( col )

        self.pat = self._wtree.get_widget('pattern_entry')
        self.pat.grab_focus()
        self.info_lbl = self._wtree.get_widget('info_label')
        # position
        self.cursor = self._wtree.get_widget('cursor')
        self.cursor.set_range(0, 100)
        # volume
        self.volume_w = self._wtree.get_widget('volume')
        self.volume_w.set_range(0, 100)
        self.volume_w.set_value(100)
        self._volume_action = DelayedAction(self.player.volume)

        self.hostname_w = self._wtree.get_widget('hostname')
        if len(sys.argv) == 2:
            self.hostname_w.set_text(sys.argv[1])

        self.status_w = self._wtree.get_widget('statusbar')
        self.status_w_ctx = self.status_w.get_context_id('player')
        self._push_status('idle')

        handlers = dict( (prop, getattr(self, prop))
            for prop in dir(self)
            if prop[0] != '_' and callable(getattr(self, prop))
            )
        self._wtree.signal_autoconnect(handlers)
        self.win.connect('destroy', gtk.main_quit)
        self.win.show()

    def _push_status(self, txt):
        self.status_w.push(self.status_w_ctx, txt)

    def _pop_status(self):
        self.status_w.pop(self.status_w_ctx)

    def _tick_generator(self):
        while True:
            try:
                if self._paused \
                or self._play_timeout.running \
                or not self.playlist \
                or self._seek_action.running:
                    # Do nothing if paused or actualy changing the song
                    yield True
                    continue
                if self._running:
                    self._position = self.player.get_time_pos()
                    if self._position is None:
                        self.cursor.set_value(self.selected['length'])
                        try:
                            self.play_next(None)
                        except IndexError:
                            self._running = False
                            self.info_lbl.set_text('Not Playing.')
                    else:
                        self.cursor.set_value(float(self._position))
            except Exception, e:
                traceback.print_stack()
                traceback.print_exc()
            finally:
                yield True

    def change_volume(self, w, value):
        if not (0 <= value <= 100):
            return False
        self._volume_action.args = (value, 1)
        self._volume_action.start(0.1)

    def _seek_now(self, val):
        if 0 <= val <= 100:
            self.player.seek('%d'%val, 1)

    def absolute_seek(self, w, type, val):
        #     |      Seek to some place in the movie.
        #     |          0 is a relative seek of +/- <value> seconds (default).
        #     |          1 is a seek to <value> % in the movie.
        #     |          2 is a seek to an absolute position of <value> seconds.
        self._seek_action.args = (val,)
        self._seek_action.start(0.2)

    def validate_pattern(self, w):
        txt = self.pat.get_text()
        if not txt:
            txt = 'True'

        if len(txt) > 2 and txt[0] == txt[-1] == '"':
            txt = txt.lower()
            txt = '%(txt)s in artist@L or %(txt)s in title@L or %(txt)s in album@L or %(txt)s in filename@L'%dict(txt=txt)
        params = {'pattern':txt}
        hostname = self.hostname_w.get_text()
        if ':' not in hostname:
            hostname += ':9090'
        uri = 'http://%s/?json=1&%s'%(hostname, urllib.urlencode(params))
        try:
            from cjson import decode as jload
        except ImportError:
            from simplejson import loads as jload

        self._pop_status()
        try:
            self.playlist = jload(urllib.urlopen(uri).read())
            DelayedAction(self._fill_playlist).start(0.5)
        except:
            self._push_status('Empty')
        else:
            self._push_status('Connected')
        self._cur_song_pos = 0
        try:
            self._play_selected()
        except:
            return
        else:
            self._running = True

    def _fill_playlist(self):
        # Fills the gtk list store
        self.list_store.clear()
        add = self.list_store.append
        for uri, infos in self.playlist:
            add((infos.get('artist', ''), infos.get('album', ''), infos.get('title', '')))

    def shuffle_playlist(self, w):
        print "Mixing", len(self.playlist), "elements."
        random.shuffle(self.playlist)
        self._cur_song_pos = -1
        self._fill_playlist()

    def toggle_pause(self, w):
        self.player.pause()
        self._paused = not self._paused

    def play_prev(self, w):
        if self._cur_song_pos <= 0:
            return
        self._cur_song_pos -= 1
        if self._cur_song_pos < 0:
            raise IndexError()
        try:
            self._play_selected()
        except:
            pass
        else:
            if not self._play_timeout.running:
                self._push_status('seeking...')

    def play_next(self, *args):
        if self._cur_song_pos > len(self.playlist):
            return
        self._cur_song_pos += 1
        try:
            self._play_selected()
        except:
            pass
        else:
            if not self._play_timeout.running:
                self._push_status('seeking...')

    def _play_now(self):
        self._pop_status()
        uri = self.selected_uri
        idx = uri.index('id=')
        self._push_status('playing %s'%repr(urllib.unquote_plus(uri[idx+3:])))
        self.player.loadfile(str(uri))
        try:
            self.volume_w.set_value(float(self.player.prop_volume))
        except TypeError:
            self.play_next()
        return False

    def force_change_song(self, treeview, path, treeview_col):
        self._cur_song_pos = path[0]
        self._play_selected()

    def _play_selected(self):
        m_d = self.selected
        self.cursor.set_value(0.0)
        self.cursor.set_range(0, m_d['length'])
        self.cursor.set_fill_level(m_d['length'])
        if m_d.get('album'):
            meta = '%s\n%s - %s'%(
                    m_d.get('title', 'Untitled'),
                    m_d.get('artist', 'Anonymous'), m_d.get('album'))
        else:
            meta = '%s\n%s'%(
                    m_d.get('title', 'Untitled'),
                    m_d.get('artist', 'Anonymous'))
        if 'length' in m_d:
            meta += '\n%s'%duration_tidy(m_d['length'])

        self.info_lbl.set_text(meta)
        self.list_w.set_cursor( (self._cur_song_pos, 0) )

        self._play_timeout.start(1)


    selected = property(lambda self: self.playlist[self._cur_song_pos][1] if self._cur_song_pos != -1 else None)

    selected_uri = property(lambda self: self.playlist[self._cur_song_pos][0] if self._cur_song_pos != -1 else None)

def main():
    pp = PPlayer()
    gtk.main()
    pp.player.quit()

if __name__ == '__main__':
    main()
