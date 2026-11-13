# -*- coding: utf-8 -*-
# Medlem – serveren til spillet. Virker på PC-en, på telefoner på samme Wi-Fi, og med --online for alle som har lenken.
# Start med Spill_Medlem_Lokal.bat, Spill_Medlem_Mobil.bat eller Spill_Medlem_Online.bat.
import http.server, socket, socketserver, os, sys, json, re, webbrowser, urllib.parse, urllib.request
import threading, time, secrets, gzip, subprocess, shutil, email.utils, posixpath

PORT = int(os.environ.get('MEDLEM_PORT') or 8090)
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.environ.get('MEDLEM_DATA') or os.path.join(ROOT, 'medlem-lagring')
KONTOER = os.path.join(BACKUP, 'kontoer')
PHONE = []  # nettverksadressene til spillet, fylles ut ved oppstart
ONLINE = {'url': None, 'status': 'av'}  # lenken alle kan bruke (med --online)
MOD_NAMES = {'barter'}  # moderatorer (samme som i spillet)
RESERVED = {'bayne', 'swagtv'}  # navn som spillet selv bruker
STATIC = ('/medlem-lokal/', '/furni/', '/items/', '/gordon/', '/textures/', '/ui/')  # bare dette kan lastes ned
LISTING = ('/furni/',)  # mappeoversikt (asset-katalogen)
LONG_CACHE = ('/furni/', '/items/', '/gordon/', '/textures/', '/ui/')  # endres aldri: nettleseren kan huske dem
PACK = ('text/html', 'application/javascript', 'application/json', 'text/css', 'image/svg+xml', 'text/plain')
NAME_RE = re.compile(r'^[A-Za-z0-9_æøåÆØÅ.\-]{2,16}$')
ID_RE = re.compile(r'^[a-z0-9]{6,24}$')
ALLOWED = [os.path.realpath(os.path.join(ROOT, d.strip('/'))) for d in STATIC]
GZ = {}  # ferdig pakkede filer (sti, endret, størrelse) -> bytes
GZ_LOCK = threading.Lock()


def jdump(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


EXTRA_LAN = tuple(x for x in os.environ.get('MEDLEM_LAN', '').split(',') if x)  # bare for testing


def private_ip(ip):
    ip = ip.split('%')[0]
    if EXTRA_LAN and ip.startswith(EXTRA_LAN):
        return True
    if ip.startswith('::ffff:'):
        ip = ip[7:]
    if ip in ('::1',) or ip.startswith('127.') or ip.startswith('10.') or ip.startswith('192.168.'):
        return True
    if ip.startswith('172.'):
        try:
            return 16 <= int(ip.split('.')[1]) <= 31
        except Exception:
            return False
    return ip.startswith('fe80:') or ip.startswith('fc') or ip.startswith('fd')


def write_json(f, o):
    os.makedirs(os.path.dirname(f), exist_ok=True)
    tmp = f + '.%s.tmp' % secrets.token_hex(3)
    with open(tmp, 'wb') as fh:
        fh.write(jdump(o))
    os.replace(tmp, f)


def read_json(f):
    try:
        with open(f, 'rb') as fh:
            return json.loads(fh.read().decode('utf-8'))
    except Exception:
        return None


# ---------------- flerspiller: hvem er inne og hva de gjør ----------------
class Net:
    HOLD = float(os.environ.get('MEDLEM_HOLD') or 20)  # så lenge en henting venter på at noe skjer
    DEAD = float(os.environ.get('MEDLEM_DEAD') or 30)  # borte etter så lenge uten kontakt

    def __init__(self):
        self.cv = threading.Condition()
        self.sid = secrets.token_hex(5)
        self.ver = 0
        self.peers = {}
        self.dbver = 0
        self.db = {}
        self.dbfile = os.path.join(BACKUP, 'net-db.json')
        saved = read_json(self.dbfile)
        if isinstance(saved, dict):
            for p, v in saved.items():
                self.dbver += 1
                self.db[p] = [v, self.dbver]

    def _touch(self, pid, sec):
        p = self.peers.get(pid)
        if p is None:
            if len(self.peers) >= 300:
                return None, False
            p = self.peers[pid] = {'s': sec, 'k': {}, 'v': 0, 'seen': time.time(), 'poll': 0}
            return p, True
        if p['s'] != sec:
            return None, False
        p['seen'] = time.time()
        return p, False

    def send(self, pid, sec, sid, patch):
        with self.cv:
            p, hello = self._touch(pid, sec)
            if p is None:
                return None
            nv = self.ver + 1
            changed = False
            for k, v in patch.items():
                if not isinstance(k, str) or len(k) > 12:
                    continue
                cur = p['k'].get(k)
                if v is None:
                    if cur is not None and cur[0] is not None:
                        p['k'][k] = [None, nv]
                        changed = True
                elif cur is None or cur[0] != v:
                    p['k'][k] = [v, nv]
                    changed = True
            if changed:
                self.ver = nv
                p['v'] = nv
                self.cv.notify_all()
            return {'sid': self.sid, 'v': self.ver, 'hello': hello}

    def poll(self, pid, sec, sid, v, dv):
        with self.cv:
            p, hello = self._touch(pid, sec)
            if p is None:
                return None
            if sid != self.sid:
                v, dv = 0, 0
                hello = hello or bool(sid)
            if v > self.ver or dv > self.dbver:
                v, dv = 0, 0
            p['poll'] += 1
            try:
                end = time.time() + self.HOLD
                while self.ver <= v and self.dbver <= dv and not hello and not p.get('kick'):
                    left = end - time.time()
                    if left <= 0:
                        break
                    self.cv.wait(left)
                out = {}
                for qid, q in self.peers.items():
                    if qid == pid or q['v'] <= v:
                        continue
                    d = {k: kv[0] for k, kv in q['k'].items() if kv[1] > v}
                    if d:
                        out[qid] = d
                ids = [qid for qid in self.peers if qid != pid]
                db = {path: val[0] for path, val in self.db.items() if val[1] > dv}
                r = {'sid': self.sid, 'v': self.ver, 'dv': self.dbver, 'peers': out, 'ids': ids, 'db': db, 'hello': hello}
                if p.pop('kick', False):
                    r['kicked'] = True
                return r
            finally:
                p['poll'] -= 1

    def auth(self, pid, sec, acct):
        # samme konto på en ny enhet: den gamle økten logges ut
        with self.cv:
            p = self.peers.get(pid)
            if not p or p['s'] != sec:
                return False
            if acct:
                for qid, q in self.peers.items():
                    if qid != pid and q.get('acct') == acct:
                        q.pop('acct', None)
                        q['kick'] = True
                p['acct'] = acct
            else:
                p.pop('acct', None)
            self.ver += 1
            self.cv.notify_all()
            return True

    def leave(self, pid, sec):
        with self.cv:
            p = self.peers.get(pid)
            if p and p['s'] == sec:
                del self.peers[pid]
                self.ver += 1
                self.cv.notify_all()

    def expire(self):
        while True:
            time.sleep(min(5.0, self.DEAD / 3))
            with self.cv:
                now = time.time()
                dead = [pid for pid, p in self.peers.items() if p['poll'] <= 0 and now - p['seen'] > self.DEAD]
                for pid in dead:
                    del self.peers[pid]
                if dead:
                    self.ver += 1
                    self.cv.notify_all()

    def db_get(self, path):
        with self.cv:
            v = self.db.get(path)
            return {'exists': v is not None and v[0] is not None, 'data': v[0] if v else None}

    def db_set(self, path, val):
        with self.cv:
            self.dbver += 1
            self.db[path] = [val, self.dbver]
            write_json(self.dbfile, {p: v[0] for p, v in self.db.items()})
            self.cv.notify_all()

    def count(self):
        with self.cv:
            return sum(1 for p in self.peers.values() if p['k'].get('n'))

    def online(self):
        # navn (små bokstaver) -> rommet de er i (None når de ikke er synlige)
        out = {}
        with self.cv:
            for p in self.peers.values():
                n = p['k'].get('n')
                if n and isinstance(n[0], str):
                    on = p['k'].get('on')
                    ar = p['k'].get('ar')
                    out[n[0].lower()] = ar[0] if ar and (not on or on[0] is not False) else None
        return out


NET = Net()


# ---------------- kontoer: lagringen til hver spiller ----------------
KLOCK = threading.Lock()
FAILS = {}  # (ip, navn) -> tidspunkter for feil passord


def konto_file(n):
    return os.path.join(KONTOER, n.lower().encode('utf-8').hex() + '.json')


def konto_get(n):
    k = read_json(konto_file(n))
    return k if isinstance(k, dict) and isinstance(k.get('pw'), str) else None


def public_profile(k, on, friends=False):
    # bare det alle kan se: aldri passord eller resten av lagringen
    s = k.get('save') if isinstance(k.get('save'), dict) else {}
    name = k.get('n') or s.get('name') or ''
    st = s.get('status')
    out = {'n': name, 'look': s.get('look') if isinstance(s.get('look'), dict) else None,
           'c': s.get('created') if isinstance(s.get('created'), (int, float)) else None,
           'status': st[:80] if isinstance(st, str) else '',
           'online': name.lower() in on, 'ar': on.get(name.lower())}
    if friends:
        fr = []
        for v in (s.get('venner') or [])[:4]:
            if isinstance(v, str) and NAME_RE.match(v):
                fk = konto_get(v)
                if fk:
                    fr.append(public_profile(fk, on))
        out['venner'] = fr
        out['nv'] = len(s.get('venner') or [])
    return out


def konto_search(q):
    if not isinstance(q, str):
        return []
    q = q.strip().lower()[:16]
    if not q:
        return []
    on = NET.online()
    names = set()
    try:
        for f in os.listdir(KONTOER):
            if f.endswith('.json'):
                try:
                    nm = bytes.fromhex(f[:-5]).decode('utf-8')
                except Exception:
                    continue
                if q in nm:
                    names.add(nm)
    except Exception:
        pass
    ordered = sorted(names, key=lambda x: (not x.startswith(q), x not in on, x))[:25]
    res = []
    for nm in ordered:
        k = konto_get(nm)
        if k:
            p = public_profile(k, on)
            res.append({'n': p['n'], 'online': p['online'], 'ar': p['ar'], 'status': p['status']})
    return res


def mod_account_exists():
    return any(konto_get(m) for m in MOD_NAMES)


def import_backups():
    # kontoer som allerede finnes på enhetene dine (sikkerhetskopiene) blir dine på serveren også
    n = 0
    try:
        files = [f for f in os.listdir(BACKUP) if f.endswith('.json') and f not in ('mod.json', 'net-db.json')]
        files.sort(key=lambda f: -os.path.getmtime(os.path.join(BACKUP, f)))  # nyeste først (enheten du brukte sist)
    except Exception:
        return 0
    for f in files:
        d = read_json(os.path.join(BACKUP, f))
        try:
            s = d.get('medlem_v2') if isinstance(d, dict) else None
            s = json.loads(s) if isinstance(s, str) else None
            name, pw = s.get('name'), s.get('pw')
            if not (isinstance(name, str) and isinstance(pw, str) and NAME_RE.match(name)):
                continue
        except Exception:
            continue
        with KLOCK:
            if konto_get(name):
                continue
            now = int(time.time() * 1000)
            write_json(konto_file(name), {'n': name, 'pw': pw, 'save': s, 't': now, 'c': now})
            n += 1
    return n


# ---------------- tunnel: lenken alle kan bruke ----------------
CF_URL = 'https://github.com/cloudflare/cloudflared/releases/latest/download/'
CHILD = []  # tunnelprogrammet som kjører


def stop_child():
    for p in CHILD:
        try:
            p.kill()
        except Exception:
            pass


__import__('atexit').register(stop_child)


def cf_name():
    if os.name == 'nt':
        return 'cloudflared.exe', 'cloudflared-windows-%s.exe' % ('amd64' if sys.maxsize > 2 ** 32 or os.environ.get('PROCESSOR_ARCHITEW6432') else '386')
    if sys.platform.startswith('linux'):
        import platform
        m = platform.machine().lower()
        return 'cloudflared', 'cloudflared-linux-%s' % ('arm64' if m in ('aarch64', 'arm64') else 'amd64')
    return None, None


def find_cloudflared():
    local, _ = cf_name()
    if local and os.path.isfile(os.path.join(ROOT, local)):
        return os.path.join(ROOT, local)
    return shutil.which('cloudflared')


def download_cloudflared():
    local, remote = cf_name()
    if not local:
        return None
    dst = os.path.join(ROOT, local)
    print('   Laster ned cloudflared (Cloudflare sitt tunnelprogram, gratis) ...')
    try:
        req = urllib.request.Request(CF_URL + remote, headers={'User-Agent': 'Medlem-server'})
        with urllib.request.urlopen(req, timeout=60) as r, open(dst + '.part', 'wb') as fh:
            total = int(r.headers.get('Content-Length') or 0)
            got = 0
            while True:
                b = r.read(1 << 16)
                if not b:
                    break
                fh.write(b)
                got += len(b)
                if total:
                    sys.stdout.write('\r   %d %%   ' % (got * 100 // total))
                    sys.stdout.flush()
        print()
        if got < 1000000:
            raise IOError('nedlastingen ble for liten (%d byte)' % got)
        os.replace(dst + '.part', dst)
        if os.name != 'nt':
            os.chmod(dst, 0o755)
        return dst
    except Exception as e:
        print()
        # prøv curl (finnes i Windows 10 og nyere) hvis Python ikke fikk det til
        if shutil.which('curl'):
            try:
                r = subprocess.run(['curl', '-L', '--fail', '-o', dst + '.part', CF_URL + remote], timeout=600)
                if r.returncode == 0 and os.path.getsize(dst + '.part') > 1000000:
                    os.replace(dst + '.part', dst)
                    if os.name != 'nt':
                        os.chmod(dst, 0o755)
                    return dst
            except Exception:
                pass
        print('   Klarte ikke å laste ned cloudflared: %s' % e)
        try:
            os.remove(dst + '.part')
        except Exception:
            pass
        return None


def log_tunnel(line):
    try:
        os.makedirs(BACKUP, exist_ok=True)
        f = os.path.join(BACKUP, 'tunnel.log')
        if os.path.isfile(f) and os.path.getsize(f) > 500000:
            os.replace(f, f + '.gammel')
        with open(f, 'a', encoding='utf-8') as fh:
            fh.write(line.rstrip() + '\n')
    except Exception:
        pass


def set_online(url):
    ONLINE['url'] = url
    ONLINE['status'] = 'starter'
    print()
    print('  ==========================================================')
    print('   Medlem er online! Send denne lenken til de du vil spille med:')
    print()
    print('      %s' % url)
    print()
    print('   Lenken virker så lenge dette vinduet er åpent og PC-en er på.')
    print('   Den blir ny hver gang du starter på nytt.')
    print('  ==========================================================')
    print()

    def check():
        # det tar gjerne noen sekunder før lenken virker overalt
        for _ in range(30):
            if ONLINE['url'] != url:
                return
            try:
                req = urllib.request.Request(url + '/medlem-net/ping', headers={'User-Agent': 'Medlem-server'})
                with urllib.request.urlopen(req, timeout=6) as r:
                    if r.status == 200:
                        break
            except Exception:
                pass
            time.sleep(3)
        if ONLINE['url'] == url:
            ONLINE['status'] = 'klar'
    threading.Thread(target=check, daemon=True).start()


def run_tunnel(cmd, pattern):
    # samme konsollvindu som serveren: lukkes vinduet, stopper tunnelen også
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             bufsize=1, universal_newlines=True, encoding='utf-8', errors='replace')
    except Exception as e:
        log_tunnel('start feilet: %s' % e)
        return False
    CHILD[:] = [p]
    found = False
    t0 = time.time()
    for line in p.stdout:
        log_tunnel(line)
        m = re.search(pattern, line)
        if m and not found:
            found = True
            set_online(m.group(0).rstrip('/'))
        if not found and time.time() - t0 > 90:
            break
    try:
        p.kill()
    except Exception:
        pass
    return found


def tunnel_loop():
    exe = find_cloudflared() or download_cloudflared()
    bad = 0
    while True:
        ONLINE['url'] = None
        ONLINE['status'] = 'kobler til'
        ok = False
        if exe and bad < 3:
            print('   Lager lenken (cloudflared) ...')
            ok = run_tunnel([exe, 'tunnel', '--no-autoupdate', '--url', 'http://127.0.0.1:%d' % PORT],
                            r'https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com')
        elif shutil.which('ssh'):
            print('   Lager lenken (localhost.run) ...')
            ok = run_tunnel(['ssh', '-T', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=' + os.devnull,
                             '-o', 'ServerAliveInterval=30', '-o', 'ExitOnForwardFailure=yes',
                             '-R', '80:127.0.0.1:%d' % PORT, 'nokey@localhost.run'],
                            r'https://[a-z0-9-]+\.(?:lhr\.life|localhost\.run)')
        else:
            ONLINE['status'] = 'feil'
            print('   Fant ikke noe tunnelprogram. Spillet virker bare på Wi-Fi-en din.')
            return
        bad = 0 if ok else bad + 1
        if ONLINE['url']:
            print('   Lenken stoppet. Lager en ny ...')
        ONLINE['url'] = None
        ONLINE['status'] = 'kobler til'
        time.sleep(4 if ok else 8)


# ---------------- selve serveren ----------------
class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    timeout = 75
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js': 'application/javascript', '.json': 'application/json', '.svg': 'image/svg+xml',
        '.mp3': 'audio/mpeg', '.png': 'image/png', '.jpg': 'image/jpeg', '.nitro': 'application/octet-stream',
        '.html': 'text/html', '.webp': 'image/webp',
    }

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header('Cache-Control', getattr(self, '_cc', None) or 'no-store')
        self.send_header('X-Medlem', '1')
        self._cc = None
        super().end_headers()

    def log_message(self, *a):
        pass

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionError, socket.timeout, OSError):
            self.close_connection = True

    # forespørsler fra PC-en eller Wi-Fi-en hjemme (ikke gjennom lenken)
    def lan(self):
        h = self.headers
        if h.get('Cf-Connecting-Ip') or h.get('X-Forwarded-For') or h.get('Cf-Ray') or h.get('X-Forwarded-Host') or h.get('Forwarded'):
            return False
        host = (h.get('Host') or '').strip().lower()
        if host.startswith('['):
            host = host[1:host.find(']')] if ']' in host else host
        else:
            host = host.rsplit(':', 1)[0]
        if not (host == 'localhost' or host == '::1' or re.fullmatch(r'\d+\.\d+\.\d+\.\d+', host)):
            return False
        return private_ip(self.client_address[0])

    def ip(self):
        h = self.headers
        return (h.get('Cf-Connecting-Ip') or (h.get('X-Forwarded-For') or '').split(',')[0].strip() or self.client_address[0])

    def _send(self, code, body=b'', ctype='application/json', head=False):
        self.send_response(code)
        self.send_header('Content-Type', ctype + ('; charset=utf-8' if ctype in PACK else ''))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if body and not head:
            self.wfile.write(body)

    def _json(self, code, o):
        return self._send(code, jdump(o))

    def _body(self, limit):
        self._read = True
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0 or n > limit:
            if n > 0:
                self.close_connection = True
            return None
        try:
            return json.loads(self.rfile.read(n).decode('utf-8'))
        except Exception:
            return None

    # ---- filer ----
    def _static(self, p, head=False):
        path = self.translate_path(p.path)
        if os.path.isdir(path):
            if not p.path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', p.path + '/' + ('?' + p.query if p.query else ''))
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            idx = os.path.join(path, 'index.html')
            if os.path.isfile(idx):
                path = idx
            elif p.path.startswith(LISTING):
                f = self.list_directory(path)
                if f:
                    try:
                        if not head:
                            shutil.copyfileobj(f, self.wfile)
                    finally:
                        f.close()
                return
            else:
                return self._send(404, b'null', head=head)
        real = os.path.realpath(path)
        if not any(real.startswith(d + os.sep) for d in ALLOWED) or not os.path.isfile(real):
            return self._send(404, b'null', head=head)
        name = os.path.basename(real).lower()
        if p.path.startswith('/medlem-lokal/') and not self.lan() and (name.startswith('test') or name.startswith('bedlab')):
            return self._send(404, b'null', head=head)
        st = os.stat(real)
        ctype = self.guess_type(real)
        etag = '"%x-%x"' % (int(st.st_mtime), st.st_size)
        cc = 'public, max-age=604800' if p.path.startswith(LONG_CACHE) else 'no-cache'
        if self.headers.get('If-None-Match') == etag:
            self.send_response(304)
            self.send_header('ETag', etag)
            self._cc = cc
            self.end_headers()
            return
        gz = ctype in PACK and st.st_size > 1024 and 'gzip' in (self.headers.get('Accept-Encoding') or '')
        if gz:
            key = (real, st.st_mtime, st.st_size)
            with GZ_LOCK:
                data = GZ.get(key)
            if data is None:
                with open(real, 'rb') as fh:
                    data = gzip.compress(fh.read(), 6)
                with GZ_LOCK:
                    if len(GZ) > 64:
                        GZ.clear()
                    GZ[key] = data
            self.send_response(200)
            self.send_header('Content-Type', ctype + ('; charset=utf-8' if ctype.startswith('text/') or ctype in PACK else ''))
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Vary', 'Accept-Encoding')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('ETag', etag)
            self.send_header('Last-Modified', email.utils.formatdate(st.st_mtime, usegmt=True))
            self._cc = cc
            self.end_headers()
            if not head:
                self.wfile.write(data)
            return
        size = st.st_size
        start, end = 0, size - 1
        rng = self.headers.get('Range')
        m = re.fullmatch(r'bytes=(\d*)-(\d*)', rng.strip()) if rng else None
        if m and (m.group(1) or m.group(2)) and size:
            if m.group(1):
                start = int(m.group(1))
                end = min(size - 1, int(m.group(2))) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            if start > end or start >= size:
                self.send_response(416)
                self.send_header('Content-Range', 'bytes */%d' % size)
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            self.send_response(206)
            self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        else:
            m = None
            self.send_response(200)
        self.send_header('Content-Type', ctype + ('; charset=utf-8' if ctype.startswith('text/') or ctype in PACK else ''))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1 if size else 0))
        self.send_header('ETag', etag)
        self.send_header('Last-Modified', email.utils.formatdate(st.st_mtime, usegmt=True))
        self._cc = cc
        self.end_headers()
        if head or not size:
            return
        with open(real, 'rb') as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                b = fh.read(min(1 << 16, left))
                if not b:
                    break
                self.wfile.write(b)
                left -= len(b)

    # ---- moderator-endringer: én felles fil som alle enheter leser ----
    def _mod_save(self):
        body = self._body(5000000)
        if not isinstance(body, dict) or not isinstance(body.get('data'), dict):
            return self._send(400, b'null')
        n, pw = body.get('n'), body.get('pw')
        ok = False
        if isinstance(n, str) and n.lower() in MOD_NAMES and isinstance(pw, str):
            k = konto_get(n)
            ok = bool(k and k['pw'] == pw) or (k is None and self.lan())
        elif self.lan() and not mod_account_exists():
            ok = True
        if not ok:
            return self._json(403, {'e': 'ikke moderator'})
        f = os.path.join(BACKUP, 'mod.json')
        with KLOCK:
            old = read_json(f)
            ver = int(old.get('ver') or 0) if isinstance(old, dict) else 0
            write_json(f, {'ver': ver + 1, 'data': body['data']})
        return self._json(200, {'ver': ver + 1})

    def _key(self, p):
        q = urllib.parse.parse_qs(p.query).get('d', [''])[0].lower()
        return re.sub(r'[^a-z0-9-]', '', q)[:40] or 'ukjent'

    # ---- kontoer ----
    def _konto(self):
        b = self._body(3000000)
        if not isinstance(b, dict):
            return self._json(400, {'e': 'feil'})
        op, n = b.get('op'), b.get('n')
        if op == 'sok':
            return self._json(200, {'res': konto_search(b.get('q'))})
        if not isinstance(n, str) or not NAME_RE.match(n):
            return self._json(400, {'e': 'navn'})
        low = n.lower()
        if op == 'ledig':
            taken = low in RESERVED or bool(konto_get(n)) or (low in MOD_NAMES and not self.lan())
            return self._json(200, {'ledig': not taken})
        if op == 'profil':
            k = konto_get(n)
            on = NET.online()
            if not k:
                return self._json(404, {'e': 'ingen'})
            return self._json(200, public_profile(k, on, True))
        pw = b.get('pw')
        if not isinstance(pw, str) or not (1 <= len(pw) <= 64):
            return self._json(400, {'e': 'passord'})
        key = (self.ip(), low)
        now = time.time()
        if len(FAILS) > 5000:
            FAILS.clear()
        fails = [t for t in FAILS.get(key, []) if now - t < 600]
        if len(fails) >= 8:
            return self._json(429, {'e': 'vent'})
        if op in ('venn', 'innboks'):
            k = konto_get(n)
            if not k or k['pw'] != pw:
                fails.append(now)
                FAILS[key] = fails
                return self._json(403, {'e': 'feil'})
            if op == 'innboks':
                with KLOCK:
                    k = konto_get(n)
                    box = k.pop('inbox', []) if k else []
                    if box:
                        write_json(konto_file(n), k)
                return self._json(200, {'inbox': box})
            til, typ = b.get('til'), b.get('type')
            if not isinstance(til, str) or not NAME_RE.match(til) or typ not in ('req', 'ok', 'nei', 'fjern') or til.lower() == low:
                return self._json(400, {'e': 'til'})
            with KLOCK:
                t = konto_get(til)
                if not t:
                    return self._json(404, {'e': 'ingen'})
                box = [m for m in t.get('inbox', []) if not (isinstance(m, dict) and m.get('fra', '').lower() == low)]
                box.append({'fra': k.get('n') or n, 't': typ, 'at': int(now * 1000)})
                t['inbox'] = box[-50:]
                write_json(konto_file(til), t)
            return self._json(200, {'ok': True, 'n': t.get('n') or til})
        if op == 'hent':
            k = konto_get(n)
            if not k:
                return self._json(404, {'e': 'ingen'})
            if k['pw'] != pw:
                fails.append(now)
                FAILS[key] = fails
                time.sleep(0.4)
                return self._json(403, {'e': 'feil'})
            return self._json(200, {'save': k.get('save'), 't': k.get('t', 0)})
        if op == 'lagre':
            s = b.get('save')
            if not isinstance(s, dict) or not isinstance(s.get('name'), str) or s['name'].lower() != low or s.get('pw') != pw:
                return self._json(400, {'e': 'lagring'})
            with KLOCK:
                k = konto_get(n)
                stamp = int(now * 1000)
                if k:
                    if k['pw'] != pw:
                        return self._json(403, {'e': 'tatt'})
                    k.update({'n': s['name'], 'save': s, 't': stamp})
                    write_json(konto_file(n), k)
                    return self._json(200, {'ok': True})
                if low in RESERVED or (low in MOD_NAMES and not self.lan()):
                    return self._json(403, {'e': 'tatt'})
                g = b.get('gammel')
                created = stamp
                if isinstance(g, dict) and isinstance(g.get('n'), str) and NAME_RE.match(g['n']) and g['n'].lower() != low:
                    old = konto_get(g['n'])
                    if old and old['pw'] == g.get('pw'):
                        created = old.get('c', stamp)
                        try:
                            os.remove(konto_file(g['n']))
                        except Exception:
                            pass
                write_json(konto_file(n), {'n': s['name'], 'pw': pw, 'save': s, 't': stamp, 'c': created})
                return self._json(200, {'ok': True, 'ny': True})
        return self._json(400, {'e': 'op'})

    # ---- flerspiller ----
    def _net(self, p, method):
        what = p.path[len('/medlem-net/'):]
        if what == 'ping':
            return self._json(200, {'ok': True, 'sid': NET.sid})
        if what == 'poll' and method == 'GET':
            q = urllib.parse.parse_qs(p.query)
            g = lambda k: (q.get(k) or [''])[0]
            pid, sec = g('id'), g('s')
            if not ID_RE.match(pid) or not (8 <= len(sec) <= 40):
                return self._json(400, {'e': 'id'})
            try:
                v, dv = int(g('v') or 0), int(g('dv') or 0)
            except ValueError:
                v, dv = 0, 0
            r = NET.poll(pid, sec, g('sid'), v, dv)
            return self._json(200, r) if r else self._json(403, {'e': 'id'})
        if what == 'send' and method == 'POST':
            b = self._body(200000)
            if not isinstance(b, dict) or not isinstance(b.get('p'), dict):
                return self._json(400, {'e': 'feil'})
            pid, sec = b.get('id'), b.get('s')
            if not isinstance(pid, str) or not ID_RE.match(pid) or not isinstance(sec, str) or not (8 <= len(sec) <= 40):
                return self._json(400, {'e': 'id'})
            r = NET.send(pid, sec, b.get('sid') or '', b['p'])
            return self._json(200, r) if r else self._json(403, {'e': 'id'})
        if what == 'auth' and method == 'POST':
            b = self._body(4000)
            if not isinstance(b, dict) or not isinstance(b.get('id'), str) or not isinstance(b.get('s'), str):
                return self._json(400, {'e': 'id'})
            n, pw = b.get('n'), b.get('pw')
            acct = None
            if n is not None:
                k = konto_get(n) if isinstance(n, str) and NAME_RE.match(n) else None
                if not k or k['pw'] != pw:
                    return self._json(403, {'e': 'konto'})
                acct = n.lower()
            return self._json(200, {'ok': NET.auth(b['id'], b['s'], acct)})
        if what == 'leave' and method == 'POST':
            b = self._body(2000)
            if isinstance(b, dict) and isinstance(b.get('id'), str) and isinstance(b.get('s'), str):
                NET.leave(b['id'], b['s'])
            return self._send(204)
        if what == 'db':
            if method == 'GET':
                path = (urllib.parse.parse_qs(p.query).get('p') or [''])[0]
                if not re.fullmatch(r'[a-z0-9_/\-]{1,60}', path):
                    return self._json(400, {'e': 'sti'})
                return self._json(200, NET.db_get(path))
            b = self._body(300000)
            if not isinstance(b, dict) or not isinstance(b.get('p'), str) or not re.fullmatch(r'[a-z0-9_/\-]{1,60}', b['p']):
                return self._json(400, {'e': 'sti'})
            n, pw = b.get('n'), b.get('pw')
            k = konto_get(n) if isinstance(n, str) and NAME_RE.match(n) else None
            ok = (isinstance(n, str) and n.lower() in MOD_NAMES and k and k['pw'] == pw) or (self.lan() and not mod_account_exists())
            if not ok:
                return self._json(403, {'e': 'ikke moderator'})
            NET.db_set(b['p'], b.get('v'))
            return self._json(200, {'ok': True})
        return self._send(404, b'null')

    def _clean(self):
        # '..' og %2e%2e løses opp før vi sjekker hva som er lov å laste ned
        p = urllib.parse.urlparse(self.path)
        raw = urllib.parse.unquote(p.path or '/')
        c = '/' + posixpath.normpath('/' + raw.replace('\\', '/')).lstrip('/')
        if raw.endswith('/') and c != '/':
            c += '/'
        return p._replace(path=c)

    def do_HEAD(self):
        p = self._clean()
        if p.path.startswith(STATIC):
            return self._static(p, head=True)
        return self._send(404, b'null', head=True)

    def do_GET(self):
        p = self._clean()
        if p.path + '/' in STATIC:
            self.send_response(301)
            self.send_header('Location', p.path + '/')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if p.path in ('/', ''):
            self.send_response(302)
            self.send_header('Location', '/medlem-lokal/')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if p.path.startswith('/medlem-net/'):
            return self._net(p, 'GET')
        if p.path == '/medlem-adresse.json':
            lan = self.lan()
            return self._json(200, {'urls': PHONE if lan else [], 'port': PORT, 'online': ONLINE['url'], 'status': ONLINE['status'], 'inne': NET.count() if lan else None})
        if p.path == '/medlem-mod':
            f = os.path.join(BACKUP, 'mod.json')
            if os.path.isfile(f):
                with open(f, 'rb') as fh:
                    return self._send(200, fh.read())
            return self._send(200, b'{"ver": 0, "data": null}')
        if p.path == '/medlem-lagring':
            if not self.lan():
                return self._send(403, b'null')
            f = os.path.join(BACKUP, self._key(p) + '.json')
            if os.path.isfile(f):
                with open(f, 'rb') as fh:
                    return self._send(200, fh.read())
            return self._send(404, b'null')
        if p.path.startswith(STATIC):
            return self._static(p)
        return self._send(404, b'null')

    def do_POST(self):
        # en forespørsel med innhold som ikke blir lest, må ikke blandes inn i den neste på samme forbindelse
        self._read = False
        try:
            self._post()
        finally:
            if not self._read and int(self.headers.get('Content-Length') or 0) > 0:
                self.close_connection = True

    def _post(self):
        p = self._clean()
        if p.path.startswith('/medlem-net/'):
            return self._net(p, 'POST')
        if p.path == '/medlem-konto':
            return self._konto()
        if p.path == '/medlem-mod':
            return self._mod_save()
        if p.path != '/medlem-lagring':
            return self._send(404, b'null')
        if not self.lan():
            return self._send(403, b'null')
        data = self._body(5000000)
        if not isinstance(data, dict):
            return self._send(400, b'null')
        write_json(os.path.join(BACKUP, self._key(p) + '.json'), data)
        return self._send(200, b'true')


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = os.name != 'nt'  # Windows: to servere kunne ellers fått samme port
    request_queue_size = 64


def lan_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))  # sender ingenting, finner bare nettverkskortet som brukes
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    good = [ip for ip in ips if not ip.startswith('127.') and not ip.startswith('169.254.')]
    private = [ip for ip in good if private_ip(ip)]
    return private + [ip for ip in good if ip not in private]


def main():
    open_qr = '--qr' in sys.argv
    online = '--online' in sys.argv
    no_browser = '--no-browser' in sys.argv
    try:
        httpd = Server(('0.0.0.0', PORT), Handler)
    except OSError:
        print()
        print('  Port %d er allerede i bruk.' % PORT)
        print('  Lukk det andre svarte Medlem-vinduet og start på nytt.')
        print()
        return 1
    threading.Thread(target=NET.expire, daemon=True).start()
    imported = import_backups()
    ips = lan_ips()
    phone = ['http://%s:%d/medlem-lokal/' % (ip, PORT) for ip in ips]
    PHONE[:] = phone
    print()
    print('  ==========================================================')
    print('   Medlem kjører')
    print('  ==========================================================')
    if phone:
        print('   Åpne denne adressen på PC-en eller telefonen:')
        print()
        print('      %s' % phone[0])
        for u in phone[1:]:
            print('      (virker ikke den: %s)' % u)
        print()
        print('   Telefonen må være på samme Wi-Fi som PC-en.')
        print('   Spør Windows om brannmur: trykk "Tillat tilgang".')
    else:
        print('   Fant ingen nettverksadresse – er PC-en koblet til Wi-Fi?')
        print('   Spillet virker på denne PC-en: http://localhost:%d/medlem-lokal/' % PORT)
    if imported:
        print('   (%d konto%s fra enhetene dine er lagret på serveren)' % (imported, '' if imported == 1 else 'er'))
    print()
    print('   Lukk dette vinduet for å stoppe spillet.')
    print('  ==========================================================')
    print()
    if online:
        threading.Thread(target=tunnel_loop, daemon=True).start()
    if not no_browser:
        base = phone[0] if phone else 'http://localhost:%d/medlem-lokal/' % PORT
        if online:
            webbrowser.open('http://localhost:%d/medlem-lokal/online.html' % PORT)
        elif open_qr and phone:
            webbrowser.open(base + 'mobil.html#' + urllib.parse.quote('|'.join(phone), safe=''))
        else:
            webbrowser.open(base)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_child()
    return 0


if __name__ == '__main__':
    sys.exit(main())
