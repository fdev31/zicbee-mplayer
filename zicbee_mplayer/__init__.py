# TODO: export fetch_playlist & playlist handling out of player class
__all__ = ['Player']

from .mp import MPlayer

class Player(MPlayer):
    def set_cache(self, val):
        """ Sets the cache value in kilobytes """
        MPlayer.set_cache(val)

    def volume(self, val):
        """ Sets volume [0-100] """
        MPlayer.volume(int(val))

    def seek(self, val):
        """ Seeks specified number of seconds (positive or negative) """
        MPlayer.seek(int(val))

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
        return self.prop_stream_pos/10000


