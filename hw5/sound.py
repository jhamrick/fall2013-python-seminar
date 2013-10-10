from scikits.audiolab import Sndfile
import numpy as np
import matplotlib.pyplot as plt

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def load(filename):
    """Load an audio file and average over channels. Returns the data as a
    numpy array and the sampling rate.

    """
    fh = Sndfile(filename, "r")
    data = fh.read_frames(fh.nframes)
    if data.ndim == 2:
        data = np.mean(data, axis=-1)
    rate = fh.samplerate
    return data, rate


def plot_amplitude(data, rate):
    """Plot time vs. amplitude of an audio signal."""
    time = np.arange(data.size) / float(rate)
    fig = plt.figure(figsize=(7, 4.5))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(time, data, color="red", linestyle="-")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")
    ax1.set_xlim(min(time), max(time))


def freq_power(data, rate):
    """Compute the frequency and power spectrum of an audio signal."""
    n = 10000
    fft = np.fft.fft(data, n)[1:n/2]
    power = np.abs(fft) ** 2
    freq = rate * np.fft.fftfreq(n)[1:n/2]

    return freq, power


def plot_power(freq, power):
    """Plot frequency vs. power of an audio signal."""
    plt.loglog(freq, power, basex=2, basey=2, color='r')
    plt.xlabel("Frequency")
    plt.ylabel("Power")

    fig = plt.gcf()
    fig.set_figwidth(10)
    fig.set_figheight(7)


def bin_notes(freq, power):
    """From the frequency and power spectrum of an audio signal, compute
    bins corresponding to musical notes. Each bin is the mean of the
    power spectrum for the corresponding note. Returns the log
    frequencies, note labels, and averaged power.

    """
    scale = ["%s%d" % (x, i) for i in xrange(9) for x in NOTES]
    scale = ["B-1"] + scale

    # B-1 to C8
    B_1 = 30.87 / 2
    C8 = 4186.01
    bins = np.logspace(np.log2(B_1), np.log2(C8), 8*12 + 2, base=2)

    scale, bins = zip(*zip(scale, bins))
    bins = np.array(bins)

    # halfway between B-1 and C0 to halfway between B8 and C8
    mids = (bins[:-1] + bins[1:]) / 2.
    lower = mids[:-1]
    upper = mids[1:]

    binned = np.empty(lower.size) * np.nan
    for i, (l, u) in enumerate(zip(lower, upper)):
        idx = (freq >= l) & (freq < u)
        binned[i] = np.mean(power[idx])

    X = np.log2(bins[1:-1])
    Xt = scale[1:-1]
    Y = binned

    return X, Xt, Y


def plot_notes(bins, power):
    """Plot power for notes C through B."""
    n = len(NOTES)
    m = power.size / n
    X = np.arange(n)
    powers = np.nansum(power.reshape((m, n)), axis=0)
    plt.bar(X, powers, align='center')
    plt.xticks(np.arange(12), NOTES)
    plt.xlim(-0.5, 11.5)
    plt.ylabel("Power")
    plt.xlabel("Musical Scale")


def pick_notes(power):
    """Identify notes from a binned power spectrum."""
    n = len(NOTES)
    m = power.size / n
    powers = np.nansum(power.reshape((m, n)), axis=0)

    best_idx = np.argmax(powers)
    idx = powers >= (powers[best_idx] / 2.)
    notes = list(np.array(NOTES)[idx])

    return notes
