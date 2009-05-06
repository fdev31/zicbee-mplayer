# TODO: export fetch_playlist & playlist handling out of player class
__all__ = ['Player']

from .mp import MPlayer

class Player(MPlayer):
    # close() # closes the player
    # quit()
    # wait()
    # set_cache(size)
    # loadfile(filename)
    # volume(value(0-100))
    # seek(val(seconds))
    # respawn() # restarts the process (in case of error)
    # pause() # toggles pause
# to rename:
    # ._cur_song_pos
    # ._paused
    # ._prop_stream_pos

# generic player stuff (return to zicbee core!!)
    # fetch_playlist
    # delete_entry
    # move_entry
    # playlist_change
    # shuffle
    # clear
    # select
    # tag
    # rate
    # .playlist
    # ._position (to rename also)
    # .selected
    pass

