#!/usr/bin/env python3
"""Exercise rebound sneak, sprint, and physical Shift through a real game, with isolated data."""
import argparse
import ctypes
import ctypes.util
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('version_dir', type=Path)
    a = p.parse_args()
    version = a.version_dir.resolve()
    resources = next((version / '.local/horizon-client').glob('*/worldgen/world_presets.json')).parent.parent
    metadata = version / "native-mods.json"
    if metadata.exists():
        assert any(m["id"] == "tectonic_horizon" for m in json.loads(metadata.read_text())["mods"]), "Tectonic must be compiled into this version"
    results = []
    for enabled in [True, False]:
        with tempfile.TemporaryDirectory(prefix='tectonic-rebind-') as tmp:
            work = Path(tmp)
            sock = work / 'control.sock'
            env = os.environ.copy()
            for k in ['WAYLAND_DISPLAY', 'HORIZON_CONTROL']:
                env.pop(k, None)
            for k in ['HORIZON_HOME', 'HORIZON_LAUNCHER_HOME', 'XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_RUNTIME_DIR']:
                d = work / k.lower()
                d.mkdir(mode=0o700)
                env[k] = str(d)
            env['HORIZON_HOME'] = str(work)
            env.update(HORIZON_NO_AUDIO='1', HORIZON_NO_DISCORD='1', HORIZON_TELEMETRY_URL='off', WINIT_UNIX_BACKEND='x11')
            env['VK_ICD_FILENAMES'] = '/usr/share/vulkan/icd.d/lvp_icd.json'
            (work / 'horizon-mods.txt').write_text('\n'.join((f'mod.{k}:false' for k in ['lunatic', 'biomesoplenty', 'zoom', 'appleskin', 'chatheads', 'eatinganimation', 'minimap'])) + f'\nmod.tectonic_horizon:{str(enabled).lower()}\n')
            (work / 'horizon-graphics.txt').write_text('lodDistance:0\nworkers:2\n')
            (work / 'options.txt').write_text('renderDistance:2\nsimulationDistance:2\nmaxFps:30\nenableVsync:false\nfullscreen:false\npauseOnLostFocus:false\ntoggleCrouch:false\ntoggleSprint:false\nkey_key.sneak:key.keyboard.c\nkey_key.jump:key.keyboard.left.shift\n')
            with (work / 'game.log').open('w') as log:
                game = subprocess.Popen(['xvfb-run', '-a', '-s', '-screen 0 1280x720x24', 'sh', '-c', 'printf "%s" "$DISPLAY" > "$1"; shift; exec "$@"', 'rebind', str(work / 'display'), str(version / 'horizon-client'), '--resources', str(resources), '--game-dir', str(work), '--world', 'Rebind', '--seed', '1234', '--creative', '--render-distance', '2', '--control-socket', str(sock)], cwd=work, env=env, stdout=log, stderr=log, start_new_session=True)

                def ctl(*words):
                    r = subprocess.run([str(version / 'horizon-ctl'), '--socket', str(sock), *map(str, words)], cwd=work, env=env, capture_output=True, text=True, timeout=30)
                    lines = r.stdout.strip().splitlines()
                    v = json.loads(lines[-1]) if lines else {'error': r.stderr}
                    if r.returncode or 'error' in v:
                        raise RuntimeError(f'{words}: {v}')
                    return v
                try:
                    deadline = time.monotonic() + 180
                    while True:
                        if game.poll() is not None:
                            raise RuntimeError((work / 'game.log').read_text()[-6000:])
                        if sock.exists():
                            try:
                                if ctl('state').get('screen') == 'playing':
                                    break
                            except (RuntimeError, subprocess.TimeoutExpired):
                                pass
                        if time.monotonic() > deadline:
                            raise RuntimeError('world did not open: ' + (work / 'game.log').read_text()[-4000:])
                        time.sleep(0.3)
                    x = ctypes.CDLL(ctypes.util.find_library('X11'))
                    xt = ctypes.CDLL(ctypes.util.find_library('Xtst'))
                    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
                    x.XOpenDisplay.restype = ctypes.c_void_p
                    x.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
                    x.XDefaultRootWindow.restype = ctypes.c_ulong
                    x.XQueryTree.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)), ctypes.POINTER(ctypes.c_uint)]
                    x.XFetchName.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_char_p)]
                    x.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
                    x.XStringToKeysym.argtypes = [ctypes.c_char_p]
                    x.XStringToKeysym.restype = ctypes.c_ulong
                    x.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
                    x.XKeysymToKeycode.restype = ctypes.c_uint
                    x.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
                    xt.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
                    display = x.XOpenDisplay((work / 'display').read_bytes())
                    assert display
                    root = ctypes.c_ulong()
                    parent = ctypes.c_ulong()
                    children = ctypes.POINTER(ctypes.c_ulong)()
                    count = ctypes.c_uint()
                    assert x.XQueryTree(display, x.XDefaultRootWindow(display), ctypes.byref(root), ctypes.byref(parent), ctypes.byref(children), ctypes.byref(count))
                    windows = []
                    for i in range(count.value):
                        title = ctypes.c_char_p()
                        x.XFetchName(display, children[i], ctypes.byref(title))
                        if title.value and b'Horizon' in title.value:
                            windows.append(children[i])
                    assert windows, 'no game window'
                    x.XSetInputFocus(display, windows[-1], 2, 0)
                    x.XSync(display, 0)
                    ctl('options-set', 'key_key.sneak', 'key.keyboard.c')
                    ctl('options-set', 'key_key.jump', 'key.keyboard.left.shift')

                    snapshots = list(work.rglob("horizon-worldgen-mods.json"))
                    if snapshots:
                        flags = json.loads(snapshots[0].read_text())["mods"]
                        assert flags["tectonic_horizon"] == enabled, flags

                    def held(key, logical, physical):
                        code = x.XKeysymToKeycode(display, x.XStringToKeysym(key.encode()))
                        assert code
                        xt.XTestFakeKeyEvent(display, code, 1, 0)
                        x.XSync(display, 0)
                        ctl('wait', '12')
                        s = ctl('status')
                        assert logical in s['keys'], (key, s['keys'], s['physical_keys'])
                        assert physical in s['physical_keys'], (key, s['physical_keys'])
                        if physical not in ['ShiftLeft', 'ShiftRight']:
                            assert 'ShiftLeft' not in s['physical_keys'], s['physical_keys']
                        xt.XTestFakeKeyEvent(display, code, 0, 0)
                        x.XSync(display, 0)
                        ctl('wait', '3')
                        assert logical not in ctl('status')['keys']
                    held('c', 'ShiftLeft', 'KeyC')
                    held('Shift_L', 'Space', 'ShiftLeft')
                    ctl('options-set', 'key_key.sneak', 'key.keyboard.left.control')
                    ctl('options-set', 'key_key.sprint', 'key.keyboard.x')
                    held('Control_L', 'ShiftLeft', 'ControlLeft')
                    held('x', 'ControlLeft', 'KeyX')
                    results.append({'tectonic': enabled, 'sneak_C': True, 'sneak_Ctrl': True, 'jump_Shift': True, 'sprint_X': True})
                    ctl('quit')
                    game.wait(timeout=20)
                except Exception:
                    Path('/tmp/tectonic-rebind-failure.log').write_text((work / 'game.log').read_text())
                    raise
                finally:
                    if game.poll() is None:
                        os.killpg(game.pid, signal.SIGTERM)
                        game.wait(timeout=20)
    print(json.dumps(results, indent=2))
if __name__ == '__main__':
    main()
