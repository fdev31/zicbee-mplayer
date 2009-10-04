__all__ = ['Player']
__version__ = '0.9'

from .mp import MPlayer

class Player(MPlayer):
    def set_cache(self, val):
        """ Sets the cache value in kilobytes """
        MPlayer.set_cache(self, val)

    def volume(self, val):
        """ Sets volume [0-100] """
        MPlayer.volume(self, int(val))

    def seek(self, val):
        """ Seeks specified number of seconds (positive or negative) """
        MPlayer.seek(self, int(val))

    def pause(self):
        """ Toggles pause mode """
        MPlayer.pause(self)

    def respawn(self):
        """ Restarts the player """
        MPlayer.respawn(self)

    def load(self, uri):
        """ Loads the specified URI """
        MPlayer.loadfile(self, uri)

    def quit(self):
        """ De-initialize player and wait for it to shut down """
        try:
            MPlayer.quit(self)
        except Exception, e:
            print "E: %s"%e
        finally:
            MPlayer.wait(self)

    @property
    def position(self):
        """ returns the stream position, in seconds """
        p = self.prop_stream_pos
        try:
            return None if p is None else p/10000
        except TypeError: # got a string
            return 0


