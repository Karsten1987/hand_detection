'''
Created on Dec 2, 2012

@author: karsten
'''
try:
    import dbus
    from dbus import DBusException
except:
    print("ERROR: Could not load dbus.")
    
class Audacious(object):

    bus = None
    aud = None
    audtrackl = None
    audplayer = None

    # init.
    def __init__(self):
        self.bus = dbus.SessionBus()
        try:
            self.aud = self.bus.get_object("org.mpris.audacious","/org/atheme/audacious","org.freedesktop.MediaPlayer")
            self.audtrackl = self.bus.get_object("org.mpris.audacious","/TrackList","org.freedesktop.MediaPlayer")
            self.audplayer = self.bus.get_object("org.mpris.audacious","/Player","org.freedesktop.MediaPlayer")
        except DBusException:
            print("ERROR: Unable to contact media player.")

    # Play.
    def play(self):
        self.audplayer.Play()

    # Pause.
    def pause(self):
        self.aud.PlayPause()

    # Stop.
    def stop(self):
        self.audplayer.Stop()

    # Play next track.
    def play_next(self):
        self.audplayer.Next()

    # Play prev track.
    def play_prev(self):
        self.audplayer.Prev()

    # Eject.
    def eject(self):
        self.aud.Clear()
        self.playlist_add(True)

    # Jump playlist to.
    def jumpto(self, track):
        if track:
            print track
            self.aud.Jump(dbus.UInt32(int(track) - 1))

    # Repeat.
    def repeat(self):
        self.aud.ToggleRepeat()

    # Shuffle.
    def shuffle(self):
        self.aud.ToggleShuffle()

    # No playlist advance.
    def advance(self):
        self.aud.ToggleAutoAdvance()
        
    def introspec(self):
        title = self.audtrackl.Introspect()
        print title
        
    def meta(self):
        tracknumber = self.audtrackl.GetCurrentTrack()
        metadata = self.audtrackl.GetMetadata(tracknumber)
        for key in metadata.keys():
            print key
        print metadata['comment']
        