r"""theremin.py -- the PM theremin, modeled Clash-style on prelude.py + clash.py.

Every block below mirrors a real block from the FPGA theremin
(MAIDEN/theremin/clash) or the sleigh link (Oracle/pm-lib/PM.SleighSpeed):
a PURE step function plus a C.mealy wrapping -- the same shape as the
Haskell, so you can read the .hs and the .py side by side.

The physics in one line: your hand near the pitch antenna adds capacitance,
which LOWERS the antenna oscillator's frequency; the FPGA never sees an
analog voltage, only that square wave -- it MEASURES the period by counting
clock ticks between rising edges. Period math, not ADCs, is the whole trick.

Model scale: clock = 1 MHz (each tick = 1 us), antenna oscillator ~ 50 kHz.
Real numbers are 25 MHz / ~800 kHz -- same code, bigger constants.

Run:  python3 theremin.py          # demo: wave a simulated hand, watch Santa
      python3 -m doctest theremin.py
"""
import prelude as P
import clash as C

# ---- the antenna oscillator (the analog world, modeled) --------------------

BASE_PERIOD = 20            # ticks at 1 MHz = 50 kHz, hand far away

def osc_step(state, period):
    """NCO-as-oscillator: count down `period`, toggle the output bit.
    state = (countdown, level) -- the square wave the FPGA actually sees.
    >>> osc_step((1, 0), 4)
    ((4, 1), 1)
    >>> osc_step((3, 1), 4)
    ((2, 1), 1)
    """
    cnt, lvl = state
    if cnt <= 1:
        return (period, 1 - lvl), 1 - lvl
    return (cnt - 1, lvl), lvl

def antenna(hand_sig):
    """hand distance (0 = touching .. 15 = far) -> square wave signal.
    Nearer hand = more capacitance = LONGER period (lower tone).
    """
    period = (BASE_PERIOD + (15 - h) for h in hand_sig)
    return C.mealy(osc_step, (1, 0), period)

# ---- edge sampler: period measurement (the theremin's "ADC") ---------------

def edge_step(state, level):
    """Count ticks between rising edges; hold the last measured period.
    state = (prev_level, ticks_since_edge, held_period)
    >>> edge_step((0, 7, 99), 1)        # rising edge: capture 7, restart
    ((1, 1, 7), 7)
    >>> edge_step((1, 3, 7), 1)         # high, no edge: keep counting
    ((1, 4, 7), 7)
    """
    prev, cnt, held = state
    if level == 1 and prev == 0:
        return (1, 1, cnt), cnt
    return (level, cnt + 1, held), held

edge_sampler = lambda wave: C.mealy(edge_step, (0, 0, BASE_PERIOD), wave)

# ---- 1-pole IIR smoother (IirNStage's single stage) ------------------------

def iir_step(y8, x):
    """y += (x - y)/8 -- but carried in Q3 fixed point (state = y*8).
    The naive integer form `y += (x-y)>>3` has a DEADBAND: within 7 counts
    of the target the shift floors to 0 and y freezes short -- a real
    fixed-point hardware lesson. Keeping 3 fraction bits converges exactly.
    >>> P.take(3, C.mealy(iir_step, 0, C.pure(80)))
    [10, 18, 26]
    >>> P.take(1, C.mealy(iir_step, 80 * 8 * 8 // 8, C.pure(80)))  # settled
    [80]
    """
    y8b = y8 + ((x * 8 - y8) >> 3)
    return y8b, y8b >> 3

smooth = lambda sig: C.mealy(iir_step, 0, sig)

# ---- the audio NCO + quarter-wave sine (what the speaker would get) --------

QSINE = [0, 25, 49, 71, 90, 106, 117, 125]      # quarter wave, 8 entries, amp 127

def sine(idx32):
    """Full wave from the quarter table by symmetry (SineLut/Quarter).
    >>> [sine(i) for i in (0, 8, 16, 24)]        # the four quadrant corners
    [0, 127, 0, -127]
    >>> sine(4) == -sine(20)                     # half-wave antisymmetry
    True
    """
    q, i = divmod(idx32 % 32, 8)
    if q == 0: return QSINE[i]
    if q == 1: return 127 if i == 0 else QSINE[8 - i]
    if q == 2: return -QSINE[i]
    return -127 if i == 0 else -QSINE[8 - i]

def nco_step(phase, inc):
    p = (phase + inc) % (1 << 16)
    return p, sine(p >> 11)                      # top 5 bits index the wave

nco = lambda inc_sig: C.mealy(nco_step, 0, inc_sig)

# ---- the sleigh mapping (PM.SleighSpeed.speedOf, verbatim port) ------------

# the oscillator toggles every half-period, so a MEASURED period (rising
# edge to rising edge) is 2*(BASE_PERIOD + 15 - hand): 40 hands-far .. 70
# hand-touching. Constants below interpret measured values.
FAR_PERIOD = 2 * BASE_PERIOD                     # 40: hand fully away
PITCH_MIN, SHIFT, VOL_TH = FAR_PERIOD, 0, 6      # model-scale hwSleighCfg

def speed_of(pitch, vol):
    """0 when the volume hand kills it (dead-man), else clamp 1..255.
    >>> speed_of(45, 10), speed_of(39, 10), speed_of(200, 10), speed_of(200, 3)
    (5, 1, 160, 0)
    """
    if vol < VOL_TH:
        return 0
    return max(1, min(255, (max(0, pitch - PITCH_MIN)) >> SHIFT))

# ---- SensorTop: the whole instrument, wired --------------------------------

def sensor_top(pitch_hand, vol_hand):
    """hand signals in -> (smoothed pitch period, vol level, sleigh speed)."""
    period = smooth(edge_sampler(antenna(pitch_hand)))
    vol = smooth(edge_sampler(antenna(vol_hand)))
    # volume LEVEL: hand NEAR the volume antenna = quiet (that is how a real
    # theremin plays); near = long measured period, so map back to 15..0:
    lvl = ((FAR_PERIOD + 30 - p) // 2 for p in vol)
    # period and lvl each feed TWO consumers (the caller and the speed path):
    # C.fanout, never zip-with-self (see clash.py fanout's docstring)
    per_a, per_b = C.fanout(period)
    lvl_a, lvl_b = C.fanout(lvl)
    speed = (speed_of(pt, lv) for pt, lv in C.bundle(per_a, lvl_a))
    return per_b, lvl_b, speed

# ---- demo: play the sleigh with your (simulated) hands ---------------------

def demo(ticks_per_pose=4000):
    poses = [                                    # (pitch hand, volume hand)
        ("hands far        ", 15, 15),
        ("pitch hand in    ",  6, 15),
        ("pitch hand close ",  1, 15),
        ("volume hand KILL ",  1,  0),
        ("volume back, mid ",  8, 15),
    ]
    pitch_sig = C.fromList(P.concat([P.replicate(ticks_per_pose, p)
                                     for _, p, _ in poses]))
    vol_sig = C.fromList(P.concat([P.replicate(ticks_per_pose, v)
                                   for _, _, v in poses]))
    per, lvl, spd = sensor_top(pitch_sig, vol_sig)
    rows = list(zip(C.sampleN(len(poses) * ticks_per_pose, per),
                    C.sampleN(len(poses) * ticks_per_pose, lvl),
                    C.sampleN(len(poses) * ticks_per_pose, spd)))
    print("pose               | pitch period | vol level | sleigh speed")
    print("-------------------+--------------+-----------+-------------")
    for k, (name, _, _) in enumerate(poses):
        p_, l_, s_ = rows[(k + 1) * ticks_per_pose - 1]   # settled value
        santa = "PARKED" if s_ == 0 else ("#" * max(1, s_ // 8))
        print(f"{name}|      {p_:3d}     |    {l_:3d}    | {s_:3d} {santa}")

if __name__ == "__main__":
    import doctest
    fails, total = doctest.testmod()
    print(f"theremin.py doctests: {total - fails}/{total} pass\n")
    demo()
