# -*- coding: utf-8 -*-
import http.server
import socketserver
import json
import gzip
import urllib.parse
import os
import sys
import webbrowser
import subprocess
import threading
import time
import re
import atexit

PORT = int(os.environ.get("PORT", 8080))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(DIRECTORY, "world_state.json")
NET_DB_FILE = os.path.join(DIRECTORY, "medlem_multiplayer_state.json")
ONLINE_LINK_FILE = os.path.join(DIRECTORY, "online_link.txt")
PID_FILE = os.path.join(DIRECTORY, "server.pid")
LOG_FILE = os.path.join(DIRECTORY, "server.log")
ONLINE_STATUS = {"url": None, "status": "starter", "clients": 0}
CHILD_PROCESSES = []

# Safe stdout/stderr for pythonw (windowless background execution)
if sys.stdout is None or sys.stderr is None:
    try:
        log_fh = open(LOG_FILE, "a", encoding="utf-8")
        sys.stdout = log_fh
        sys.stderr = log_fh
    except Exception:
        pass

def cleanup_children():
    for p in CHILD_PROCESSES:
        try:
            p.kill()
        except Exception:
            pass
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

atexit.register(cleanup_children)

# Save current PID
try:
    with open(PID_FILE, "w", encoding="utf-8") as pf:
        pf.write(str(os.getpid()))
except Exception:
    pass

# ----------------- World State Persistence -----------------
def load_world_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Feil ved lesing av world_state: {e}")
    return {"furni": {}, "settings": {}}

def save_world_state(state):
    try:
        tmp_file = STATE_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, STATE_FILE)
    except Exception as e:
        print(f"Feil ved lagring av world_state: {e}")


# ----------------- Real-time Multiplayer Engine -----------------
class NetSyncServer:
    def __init__(self):
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.version = 1
        self.db = {} # path -> val
        self.history = [] # (version, path, val, client_id)
        self.clients = {} # client_id -> last_seen

        if os.path.exists(NET_DB_FILE):
            try:
                with open(NET_DB_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self.db = saved
            except Exception:
                pass

    def save_db(self):
        try:
            tmp = NET_DB_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.db, f, ensure_ascii=False)
            os.replace(tmp, NET_DB_FILE)
        except Exception:
            pass

    def update_values(self, updates, client_id=None):
        if not isinstance(updates, dict) or not updates:
            return self.version
        with self.cv:
            self.version += 1
            for path, val in updates.items():
                if not isinstance(path, str) or not path:
                    continue
                path = path.strip("/")
                if val is None:
                    self.db.pop(path, None)
                elif isinstance(val, dict) and path in self.db and isinstance(self.db[path], dict):
                    self.db[path].update(val)
                else:
                    self.db[path] = val
                self.history.append((self.version, path, self.db.get(path), client_id))
            
            if len(self.history) > 2000:
                self.history = self.history[-1000:]
            if client_id:
                self.clients[client_id] = time.time()
            self.cv.notify_all()
            return self.version

    def poll(self, client_v, client_id=None, timeout=20.0):
        with self.cv:
            now = time.time()
            if client_id:
                self.clients[client_id] = now
            # Prune dead clients (inactive > 60s)
            dead = [cid for cid, t in self.clients.items() if now - t > 60.0]
            for cid in dead:
                self.clients.pop(cid, None)

            if self.version <= client_v:
                self.cv.wait(timeout)

            # Full snapshot if client is new or history pruned
            min_hist_v = self.history[0][0] if self.history else 1
            if client_v <= 0 or client_v < min_hist_v:
                return {
                    "v": self.version,
                    "full": True,
                    "updates": dict(self.db),
                    "onlineCount": len(self.clients)
                }

            # Incremental updates
            changes = {}
            for v, p, val, cid in self.history:
                if v > client_v and cid != client_id:
                    changes[p] = val
            return {
                "v": self.version,
                "full": False,
                "updates": changes,
                "onlineCount": len(self.clients)
            }

    def get_value(self, path):
        with self.lock:
            path = path.strip("/")
            if path in self.db:
                return self.db[path]
            # Smart fallback for usernames/<name>
            if path.startswith("usernames/"):
                uname = path[len("usernames/"):].lower().strip()
                # 1. Search profiles/<uid>/name
                for p, v in self.db.items():
                    if p.startswith("profiles/") and p.endswith("/name") and isinstance(v, str):
                        if v.lower().strip() == uname:
                            uid = p.split("/")[1]
                            self.db[path] = uid
                            return uid
                # 2. Search room players
                for p, v in self.db.items():
                    if "/players/" in p and isinstance(v, dict):
                        pname = str(v.get("name", "")).lower().strip()
                        if pname == uname:
                            uid = v.get("uid") or p.split("/players/")[-1].split("/")[0]
                            if uid:
                                self.db[path] = uid
                                return uid
                # 3. If uname looks like a valid uid itself
                if uname in ("barter6", "admin", "adminsidia") or len(uname) >= 3:
                    for p in self.db.keys():
                        if p.startswith(f"profiles/{uname}"):
                            self.db[path] = uname
                            return uname

            prefix = path + "/"
            sub = {}
            found = False
            for p, v in self.db.items():
                if p.startswith(prefix):
                    found = True
                    rest = p[len(prefix):]
                    sub[rest] = v
            if found:
                return sub
            return None

NET_SYNC = NetSyncServer()


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


# ----------------- HTTP Request Handler -----------------
class GameRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Silence frequent polling to prevent terminal spam
        return

    def guess_type(self, path):
        if path.endswith(".js"):
            return "application/javascript"
        if path.endswith(".css"):
            return "text/css"
        if path.endswith(".svg"):
            return "image/svg+xml"
        if path.endswith(".mp3"):
            return "audio/mpeg"
        if path.endswith(".wav"):
            return "audio/wav"
        if path.endswith(".m4a"):
            return "audio/mp4"
        if path.endswith(".json"):
            return "application/json"
        if path.endswith(".nitro"):
            return "application/octet-stream"
        if path.endswith(".ico"):
            return "image/x-icon"
        if path.endswith(".png"):
            return "image/png"
        if path.endswith(".jpg") or path.endswith(".jpeg"):
            return "image/jpeg"
        if path.endswith(".woff2"):
            return "font/woff2"
        if path.endswith(".woff"):
            return "font/woff"
        if path.endswith(".ttf"):
            return "font/ttf"
        return super().guess_type(path)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        req_path = getattr(self, 'path', '')
        if req_path.startswith('/api/') or req_path.endswith('.html') or req_path in ('/', ''):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        elif any(req_path.endswith(ext) for ext in ('.js', '.css', '.png', '.jpg', '.jpeg', '.svg', '.json', '.mp3', '.ogg', '.wav', '.woff', '.woff2', '.ico', '.nitro')):
            self.send_header('Cache-Control', 'public, max-age=86400, stale-while-revalidate=3600')
        else:
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_HEAD(self):
        p = urllib.parse.urlparse(self.path)
        if p.path in ("/", "", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        return super().do_HEAD()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)

        # Health check
        if p.path == "/healthz":
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', '2')
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Root redirect to play.html
        if p.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/play.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # Online status check
        if p.path in ("/api/online-status", "/medlem-adresse.json"):
            ONLINE_STATUS["clients"] = len(NET_SYNC.clients)
            data = json.dumps(ONLINE_STATUS).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Real-time Multiplayer Poll
        if p.path == "/api/net/poll":
            qs = urllib.parse.parse_qs(p.query)
            try:
                client_v = int(qs.get("v", [0])[0])
            except ValueError:
                client_v = 0
            client_id = qs.get("cid", [None])[0]
            res = NET_SYNC.poll(client_v, client_id, timeout=20.0)
            data = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Real-time Multiplayer Get
        if p.path == "/api/net/get":
            qs = urllib.parse.parse_qs(p.query)
            path = qs.get("p", [""])[0]
            val = NET_SYNC.get_value(path)
            data = json.dumps({"exists": val is not None, "val": val}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # World state
        if p.path in ("/api/world-state", "/api/room-furni"):
            state = load_world_state()
            data = json.dumps(state).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Fast gzip static file serving
        clean_path = p.path.split('?')[0]
        file_path = self.translate_path(clean_path)
        if os.path.isfile(file_path) and any(clean_path.endswith(ext) for ext in ('.js', '.css', '.json', '.svg')):
            if "gzip" in self.headers.get("Accept-Encoding", ""):
                try:
                    with open(file_path, "rb") as f:
                        raw_data = f.read()
                    if len(raw_data) > 512:
                        ctype = self.guess_type(clean_path)
                        compressed = gzip.compress(raw_data, compresslevel=6)
                        self.send_response(200)
                        self.send_header('Content-Type', ctype)
                        self.send_header('Content-Encoding', 'gzip')
                        self.send_header('Content-Length', str(len(compressed)))
                        self.end_headers()
                        self.wfile.write(compressed)
                        return
                except Exception:
                    pass

        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        p = urllib.parse.urlparse(self.path)

        # Real-time Multiplayer Send
        if p.path == "/api/net/send":
            try:
                payload = json.loads(post_data.decode("utf-8"))
                client_id = payload.get("clientId")
                updates = payload.get("updates", {})
                new_v = NET_SYNC.update_values(updates, client_id)
                resp = json.dumps({"ok": True, "v": new_v}).encode("utf-8")
            except Exception as e:
                resp = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return

        # World state: save furniture
        if p.path == "/api/save-room-furni":
            try:
                payload = json.loads(post_data.decode("utf-8"))
                room_id = payload.get("room")
                furni_list = payload.get("furni")
                if room_id and isinstance(furni_list, list):
                    state = load_world_state()
                    if "furni" not in state or not isinstance(state["furni"], dict):
                        state["furni"] = {}
                    state["furni"][room_id] = furni_list
                    save_world_state(state)
            except Exception as e:
                print(f"Feil i /api/save-room-furni: {e}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true, "saved": true}')
            return

        # World state: save full state
        if p.path == "/api/save-world-state":
            try:
                payload = json.loads(post_data.decode("utf-8"))
                state = load_world_state()
                if "furni" in payload and isinstance(payload["furni"], dict):
                    if "furni" not in state or not isinstance(state["furni"], dict):
                        state["furni"] = {}
                    state["furni"].update(payload["furni"])
                if "settings" in payload and isinstance(payload["settings"], dict):
                    if "settings" not in state or not isinstance(state["settings"], dict):
                        state["settings"] = {}
                    state["settings"].update(payload["settings"])
                if "setting" in payload and isinstance(payload["setting"], dict):
                    k = payload["setting"].get("key")
                    v = payload["setting"].get("val")
                    if k:
                        if "settings" not in state or not isinstance(state["settings"], dict):
                            state["settings"] = {}
                        state["settings"][k] = v
                save_world_state(state)
            except Exception as e:
                print(f"Feil i /api/save-world-state: {e}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true, "saved": true}')
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')


# ----------------- Cloudflare Tunnel (--online) -----------------
def start_online_tunnel(port):
    exe = os.path.join(DIRECTORY, "cloudflared.exe")
    if not os.path.isfile(exe):
        print("\n[ADVARSEL] Fant ikke cloudflared.exe i mappen. Tunnel kunne ikke startes.")
        ONLINE_STATUS["status"] = "feil"
        return

    cmd = [exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"]
    ONLINE_STATUS["status"] = "kobler_til"

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        CHILD_PROCESSES.append(proc)
    except Exception as e:
        print(f"[ONLINE FEIL] Kunne ikke starte cloudflared: {e}")
        ONLINE_STATUS["status"] = "feil"
        return

    url_re = re.compile(r'https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com')
    found_url = None

    for line in proc.stdout:
        m = url_re.search(line)
        if m:
            found_url = m.group(0)
            ONLINE_STATUS["url"] = found_url
            ONLINE_STATUS["status"] = "klar"

            try:
                with open(ONLINE_LINK_FILE, "w", encoding="utf-8") as f:
                    f.write(found_url)
            except Exception:
                pass

            print("\n" + "=" * 70)
            print("  🩸 UNDERGRUNN MEDLEM ONLINE ER NÅ DIREKTE TILGJENGELIG OVERALT PÅ INTERNETT!")
            print("=" * 70)
            print(f"\n  🌐 OFFENTLIG SPILLENKE (VIRKER PÅ ALLE WI-FI, 4G, 5G OG TELEFONER):")
            print(f"\n      >> {found_url} <<\n")
            print("  1. Send denne lenken til venner du vil spille med.")
            print("  2. De kan åpne lenken på iPhone, Android eller PC.")
            print("  3. Dere spiller sammen i samme rom i sanntid!")
            print("=" * 70 + "\n")
            break

    def drain():
        for _ in proc.stdout:
            pass
    threading.Thread(target=drain, daemon=True).start()


# ----------------- Server Launcher -----------------
def run_server():
    os.chdir(DIRECTORY)
    is_online = "--online" in sys.argv
    is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT"))

    if is_cloud:
        actual_port = PORT
        httpd = ThreadingServer(("0.0.0.0", PORT), GameRequestHandler)
    else:
        actual_port = PORT
        httpd = None
        for p in range(PORT, PORT + 20):
            try:
                httpd = ThreadingServer(("", p), GameRequestHandler)
                actual_port = p
                break
            except OSError:
                continue
        if httpd is None:
            actual_port = PORT
            httpd = ThreadingServer(("", PORT), GameRequestHandler)

    local_url = f"http://localhost:{actual_port}/play.html"
    online_helper_url = f"http://localhost:{actual_port}/online.html"

    print("=" * 70)
    print("  🩸 UNDERGRUNN MEDLEM - FLERSPILLER SERVER")
    print(f"  Lokal adresse: {local_url}")
    print("=" * 70)

    if is_online:
        threading.Thread(target=start_online_tunnel, args=(actual_port,), daemon=True).start()
        time.sleep(1)
        if not os.environ.get("RENDER") and not os.environ.get("PORT"):
            try:
                webbrowser.open(online_helper_url)
            except Exception:
                pass
    else:
        if not os.environ.get("RENDER") and not os.environ.get("PORT"):
            try:
                webbrowser.open(local_url)
            except Exception:
                pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stoppet.")
        cleanup_children()
        httpd.server_close()

if __name__ == "__main__":
    run_server()
