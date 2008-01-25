# vim: et ts=4 sw=4
import itertools
from zicdb.zutils import duration_tidy, parse_line

DEFAULT_NAME='songs'

def init(args=None):
    clean_args = args or sys.argv[2:]
    globals().update(
            dict(songs=Database(os.environ.get('ZDB', DEFAULT_NAME)),
                args=clean_args)
            )
    sys.argv = sys.argv[2:]

def do_list():
    for i in os.listdir(DB_DIR):
        if os.path.isfile(os.path.join(DB_DIR, i, '__info__')):
            txt = "%s # %d records"%(i, len(Database(i)))
            if i == DEFAULT_NAME:
                txt += ' [default]'
            print txt
def do_shell():
    import pdb; pdb.set_trace()

def do_bundle():
    if len(args) != 1:
        sys.exit("Need filename name as agment !")
    songs.dump_archive(args[0])

def do_reset():
    songs.destroy()
    print "Database cleared!"

def do_help():
        print "Welcome to ZicDB!".center(80)
        print """
use
    Not a command by itself, used to specify active database (default: songs)
    Exemple:
    %% %(prog)s use lisa search artist: dire st

serve
    Runs a user-accessible www server on port 8080

list
    List available Databases.

reset
    Erases the Database (every previous scan is lost!)

bundle <filename>
    Create a bundle (compressed archive) of the database

scan <directory|archive> [directory|archive...]
    Scan directories/archive for files and add them to the database

search[::out] <match command>

  out:
    specifies the output format (for now: m3u or null or default)

  Match commands composition:
    field: value [ [or|and] field2: value2 ]...
    for length, value may be preceded by "<" or ">"
    if field name starts with a capital, the search is case-sensitive

  Possible fields:
\t- %(tags)s

  Exemple:
  %% %(prog)s search filename: shak length > 3*60
    """%dict(
            tags = '\n\t- '.join(valid_tags),
            prog = "zicdb")

def do_search(out=None):
    duration = 0
    start_t = time()

    fields = list(valid_tags)
    fields.remove('filename')
    fields = tuple(fields)

    if out == 'm3u':
        def song_output(song):
            print song.filename
    elif out == 'null':
        def song_output(song): pass
    else:
        def song_output(song):
            txt = '%s :\n%s '%(repr(song.filename), '| '.join('%s: %s'%(f, getattr(song, f)) for f in fields if f[0] != '_' and getattr(song, f)))
            print txt.decode('utf8').encode('utf8')

    num = 0
    pat, kw = parse_line(' '.join(args))
    for num, res in enumerate(songs.search(None, pat, **kw)):
        song_output(res)
        duration += res.length

    print "# %d results in %s for a total of %s!"%(
            num,
            duration_tidy(time()-start_t),
            duration_tidy(duration)
            )

def do_scan():
    if not args:
        sys.exit('At least one argument must be specified!')

    newline_iterator = itertools.cycle(x == 10 for x in xrange(11))
    orig_nb = len(songs)
    start_t = time()

    archives = []
    directories = []

    exp_vars = os.path.expandvars
    exp_usr = os.path.expanduser
    for path in args:
        path = exp_usr(exp_vars(path))
        if os.path.isdir(path):
            directories.append(path)
        else:
            archives.append(path)

    def _scan(**kw):
        print ', '.join(':'.join((k,v)) for k,v in kw.iteritems())
        try:
            for status_char in songs.merge(**kw):
                print status_char,
                if newline_iterator.next():
                    print ''
                sys.stdout.flush()
        except Exception, e:
            print "ERROR!", str(e)
            import traceback
            traceback.print_exc()

    for path in archives:
        _scan(archive=path)

    for path in directories:
        _scan(directory=path)

    elapsed = time() - start_t
    delta = len(songs)-orig_nb
    print "\nProcessed %d (%s%d) songs in %s (%.2f/s.)"%(
            len(songs),
            '-' if delta < 0 else '+',
            delta,
            duration_tidy(elapsed),
            len(songs)/elapsed)


def do_serve():
    import web
    import urllib

    from pkg_resources import resource_filename
    render = web.template.render(resource_filename('zicdb', 'web_templates'))
    os.chdir( resource_filename('zicdb', 'static')[:-6] )

    urls = (
            '/(.*)', 'index',
            )

    artist_form = web.form.Form(
            web.form.Hidden('id'),
            web.form.Textbox('pattern'),
            web.form.Checkbox('m3u'),
            )

    class index:
        def GET(self, name):
            t0 = time()
            if artist_form.validates():
                artist_form.fill()
                filename = artist_form['id'].value
                if name.startswith("get") and filename:
                    web.header('Content-Type', 'application/x-audio')
                    web.header('Content-Disposition',
                            'attachment; filename:%s'%filename.rsplit('/', 1)[-1], unique=True)

                    CHUNK=1024
                    in_fd = file(filename)
                    web.header('Content-Length', str( os.fstat(in_fd.fileno()).st_size ) )

                    while True:
                        data = in_fd.read(CHUNK)
                        if not data: break
                        yield data
                    return

            if artist_form['m3u'].value:
                web.header('Content-Type', 'audio/x-mpegurl')
                format = 'm3u'
            elif web.input().get('plain'):
                web.header('Content-Type', 'text/plain')
                format = 'plain'
            elif web.input().get('json'):
                web.header('Content-Type', 'text/plain')
                format = 'json'
            else:
                web.header('Content-Type', 'text/html; charset=utf-8')
                format = 'html'

            pattern = artist_form['pattern'].value
            if pattern is None:
                res = None
            else:
                pat, vars = parse_line(pattern)
                web.debug(pattern, pat, vars)
                home = web.ctx['homedomain']+'/get?'
                urlencode = web.http.urlencode
                res = (
                        (home+urlencode({'id':r.filename}), r)
                        for r in songs.search(None, pat, **vars)
                        )
            t_sel = time()

            if format == 'm3u':
                yield render.playlist(web.http.url, res)
            elif format == 'plain':
                yield render.plain(web.http.url, res)
            elif format == 'json':
                try:
                    from cjson import encode as jdump
                except ImportError:
                    from simplejson import dumps as jdump
                quote = urllib.quote
                from itertools import izip

# Experimental code:
#                lbls = ('genre', 'artist', 'album', 'title', 'length')
#                idxs = (3, 4, 5, 6, 8)
#                fields = ('__id__', '__version__', 'filename', 'genre', 'artist', 'album', 'title', 'track', 'length')
#                dict_list = [
#                        (s0, dict(izip(lbls, s1._get_val_iter(*idxs))))
#                        for (s0, s1) in res]
                dict_list = [
                        (s[0],
                            dict( (f, getattr(s[1], f))
                            for f in s[1].fields if f[0] not in 'f_')
                            )
                        # /tuple(uri, dict)
                        for s in res]

                web.debug('handled in %.2fs (%.2f for select)'%(time() - t0, t_sel - t0))
                yield jdump(dict_list)
            else:
                yield render.index(artist_form, res)


    # UGLY !
    sys.argv = ['zicdb', '9090']
    web.run(urls, locals())

### INTERNAL ###

import os, sys
from time import time
from zicdb.dbe import Database, valid_tags, DB_DIR

