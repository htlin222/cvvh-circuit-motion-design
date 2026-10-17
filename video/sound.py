import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000; DUR = 30.0
N = int(SR*DUR); t = np.arange(N)/SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def put(sig, start, pan=0.0, gain=1.0):
    i = int(start*SR); n = min(len(sig), N-i)
    if n <= 0: return
    L[i:i+n] += sig[:n]*gain*np.sqrt((1-pan)/2); R[i:i+n] += sig[:n]*gain*np.sqrt((1+pan)/2)
def env(n, a, d):
    e = np.ones(n); na = int(a*SR); nd = int(d*SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nd: e[-nd:] *= np.linspace(1, 0, nd)**2
    return e

SCENES = [0, 3, 7, 10, 14, 18, 21, 25, 28]

# 1. ambient drone: detuned low pad + slow-breathing filtered air
lfo = 0.6 + 0.4*np.sin(2*np.pi*t/9.0)
for f, g in [(55, .30), (82.41, .16), (110, .12), (164.8, .05)]:
    L += g*lfo*np.sin(2*np.pi*f*t); R += g*lfo*np.sin(2*np.pi*(f*1.004)*t + .7)
air = lp(rng.standard_normal(N), 420)*0.9
L += air*(0.5+0.5*np.sin(2*np.pi*t/7)); R += air[::-1]*(0.5+0.5*np.cos(2*np.pi*t/7))
master_env = env(N, 2.5, 2.0); L *= master_env; R *= master_env

# 2. machine bed: pump whirr (rotor-rate AM noise) + soft heartbeat-like pump pulse
whirr = bp(rng.standard_normal(N), 900, 2400)*0.05*(0.55+0.45*np.sin(2*np.pi*1.25*t))
L += whirr*.8; R += whirr
for k in np.arange(0.5, DUR, 0.8):
    n = int(0.18*SR); tt = np.arange(n)/SR
    thump = np.sin(2*np.pi*(58-20*tt/0.18)*tt)*np.exp(-tt*28)*0.22
    put(thump, k)

# 3. scene transitions: rising whoosh into a sub hit + shimmering chord
def whoosh(d=0.9):
    n = int(d*SR); x = rng.standard_normal(n); out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        fr = i/n; c = 300*(1-fr) + 4200*fr
        out[i:i+seg] = bp(x[i:i+seg], c*0.7, min(c*1.4, 20000))
    return out*np.linspace(0, 1, n)**2.5*0.5
def subhit():
    n = int(1.6*SR); tt = np.arange(n)/SR
    return (np.sin(2*np.pi*(90*np.exp(-tt*3)+38)*tt)*np.exp(-tt*2.4))*0.55
def shimmer(root):
    n = int(2.4*SR); tt = np.arange(n)/SR; s = np.zeros(n)
    for m, g in [(1, .5), (1.5, .35), (2, .25), (3, .12)]:
        s += g*np.sin(2*np.pi*root*m*tt)*(1+0.3*np.sin(2*np.pi*5.5*tt))
    return s*np.exp(-tt*1.4)*np.minimum(1, tt/0.03)*0.09
roots = [220, 246.9, 261.6, 293.7, 329.6, 293.7, 261.6, 246.9, 220]
for i, s0 in enumerate(SCENES):
    if s0 > 0: put(whoosh(), s0-0.9, pan=(-0.6 if i % 2 else 0.6), gain=.9)
    put(subhit(), s0, gain=.9 if s0 else .6)
    put(shimmer(roots[i]), s0+0.02, pan=0)

# 4. HUD data blips when the text panel builds
def blip(f, d=0.035):
    n = int(d*SR); tt = np.arange(n)/SR
    return np.sin(2*np.pi*f*tt)*np.exp(-tt*90)*np.minimum(1, tt/0.002)*0.12
for s0 in SCENES:
    fs = rng.choice([1760, 2093, 2349, 2637, 3136], size=7)
    for j, f in enumerate(fs):
        put(blip(f), s0+0.35+j*0.055, pan=0.75)
    put(blip(1318, .08), s0+0.8, pan=-0.75)  # left HUD value tick

# 5. zoom servo: filtered sweep under each camera move
for s0 in SCENES[1:]:
    n = int(1.1*SR); tt = np.arange(n)/SR
    f = 180+260*(tt/1.1)
    serv = np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/1.1)**2*0.06
    put(serv, s0, gain=1)

# 6. intro riser + outro tail
n = int(2.6*SR); tt = np.arange(n)/SR
riser = hp(rng.standard_normal(n), 2000)*(tt/2.6)**3*0.12
L[:n] += riser; R[:n] += riser
out_n = int(2.0*SR)
fade = np.ones(N); fade[-out_n:] = np.linspace(1, 0, out_n)**1.5

# simple stereo delay/reverb for space
def space(x, d, g):
    y = x.copy(); k = int(d*SR)
    for r in range(1, 5): y[k*r:] += x[:-k*r]*(g**r)
    return y
L2 = space(L, 0.23, .32); R2 = space(R, 0.29, .32)
mix = np.stack([L2*fade, R2*fade], 1)
mix = np.tanh(mix/np.max(np.abs(mix))*1.6)*0.82
wavfile.write('sound.wav', SR, (mix*32767).astype(np.int16))
print('ok', mix.shape)
