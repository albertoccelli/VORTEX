# -*- coding: utf-8 -*-
"""
Created on Fri May 23 2014

Definitions from
 - ANSI S1.4-1983 Specification for Sound Level Meters, Section
   5.2 Weighting Networks, pg 5.
 - IEC 61672-1 (2002) Electroacoustics - Sound level meters,
   Part 1: Specification

"Above 20000 Hz, the relative response level shall decrease by at least 12 dB
per octave for any frequency-weighting characteristic"

Appendix C:

"it has been shown that the uncertainty allowed in the A-weighted frequency
response in the region above 16 kHz leads to an error which may exceed the
intended tolerances for the measurement of A-weighted sound level by a
precision (type 1) sound level meter."
"""

import numpy as np
from numpy import pi, log10
from scipy.signal import zpk2tf, zpk2sos, freqs, sosfilt

__all__ = ['abc_weighting', 'a_weighting', 'a_weight']


def _relative_degree(z, p):
    """
    Return relative degree of transfer function from zeros and poles
    """
    degree = len(p) - len(z)
    if degree < 0:
        raise ValueError("Improper transfer function. "
                         "Must have at least as many poles as zeros.")
    else:
        return degree


def _zpkbilinear(z, p, k, fs):
    """
    Return a digital filter from an analog one using a bilinear transform.

    Transform a set of poles and zeros from the analog s-plane to the digital
    z-plane using Tustin's method, which substitutes ``(z-1) / (z+1)`` for
    ``s``, maintaining the shape of the frequency response.

    Parameters
    ----------
    z : array_like
        Zeros of the analog IIR filter transfer function.
    p : array_like
        Poles of the analog IIR filter transfer function.
    k : float
        System gain of the analog IIR filter transfer function.
    fs : float
        Sample rate, as ordinary frequency (e.g. hertz). No prewarping is
        done in this function.

    Returns
    -------
    z : ndarray
        Zeros of the transformed digital filter transfer function.
    p : ndarray
        Poles of the transformed digital filter transfer function.
    k : float
        System gain of the transformed digital filter.

    """
    z = np.atleast_1d(z)
    p = np.atleast_1d(p)

    degree = _relative_degree(z, p)

    fs2 = 2.0 * fs

    # Bilinear transform the poles and zeros
    z_z = (fs2 + z) / (fs2 - z)
    p_z = (fs2 + p) / (fs2 - p)

    # Any zeros that were at infinity get moved to the Nyquist frequency
    z_z = np.append(z_z, -np.ones(degree))

    # Compensate for gain change
    k_z = k * np.real(np.prod(fs2 - z) / np.prod(fs2 - p))

    return z_z, p_z, k_z


def abc_weighting(curve='A'):
    """
    Design of an analog weighting filter with A, B, or C curve.

    Returns zeros, poles, gain of the filter.

    Examples
    --------
    Plot all 3 curves:

    >>> from scipy import signal
    >>> from numpy import logspace
    >>> import matplotlib.pyplot as plt
    >>> for w_curve in ['A', 'B', 'C']:
    ...     z, p, k = abc_weighting(w_curve)
    ...     w = 2*pi*logspace(log10(10), log10(100000), 1000)
    ...     w, h = signal.freqs_zpk(z, p, k, w)
    ...     plt.semilogx(w/(2*pi), 20*np.log10(h), label=w_curve)
    >>> plt.title('Frequency response')
    >>> plt.xlabel('Frequency [Hz]')
    >>> plt.ylabel('Amplitude [dB]')
    >>> plt.ylim(-50, 20)
    >>> plt.grid(True, color='0.7', linestyle='-', which='major', axis='both')
    >>> plt.grid(True, color='0.9', linestyle='-', which='minor', axis='both')
    >>> plt.legend()
    >>> plt.show()

    """
    if curve not in 'ABC':
        raise ValueError('Curve type not understood')

    # ANSI S1.4-1983 C weighting
    #    2 poles on the real axis at "20.6 Hz" HPF
    #    2 poles on the real axis at "12.2 kHz" LPF
    #    -3 dB down points at "10^1.5 (or 31.62) Hz"
    #                         "10^3.9 (or 7943) Hz"
    #
    # IEC 61672 specifies "10^1.5 Hz" and "10^3.9 Hz" points and formulas for
    # derivation.  See _derive_coefficients()

    z = [0, 0]
    p = [-2 * pi * 20.598997057568145,
         -2 * pi * 20.598997057568145,
         -2 * pi * 12194.21714799801,
         -2 * pi * 12194.21714799801]
    k = 1

    if curve == 'A':
        # ANSI S1.4-1983 A weighting =
        #    Same as C weighting +
        #    2 poles on real axis at "107.7 and 737.9 Hz"
        #
        # IEC 61672 specifies cutoff of "10^2.45 Hz" and formulas for
        # derivation.  See _derive_coefficients()

        p.append(-2 * pi * 107.65264864304628)
        p.append(-2 * pi * 737.8622307362899)
        z.append(0)
        z.append(0)

    elif curve == 'B':
        # ANSI S1.4-1983 B weighting
        #    Same as C weighting +
        #    1 pole on real axis at "10^2.2 (or 158.5) Hz"

        p.append(-2 * pi * 10 ** 2.2)  # exact
        z.append(0)

    # TODO: Calculate actual constants for this
    # Normalize to 0 dB at 1 kHz for all curves
    b, a = zpk2tf(z, p, k)
    k /= abs(freqs(b, a, [2 * pi * 1000])[1][0])

    return np.array(z), np.array(p), k


def a_weighting(fs, output='ba'):
    """
    Design of a digital A-weighting filter.

    Designs a digital A-weighting filter for
    sampling frequency `fs`.
    Warning: fs should normally be higher than 20 kHz. For example,
    fs = 48000 yields a class 1-compliant filter.

    Parameters
    ----------
    fs : float
        Sampling frequency
    output : {'ba', 'zpk', 'sos'}, optional
        Type of output:  numerator/denominator ('ba'), pole-zero ('zpk'), or
        second-order sections ('sos'). Default is 'ba'.

    Examples
    --------
    Plot frequency response

    >>> from scipy.signal import freqz
    >>> import matplotlib.pyplot as plt
    >>> fs = 200000
    >>> b, a = a_weighting(fs)
    >>> f = np.logspace(np.log10(10), np.log10(fs/2), 1000)
    >>> w = 2*pi * f / fs
    >>> w, h = freqz(b, a, w)
    >>> plt.semilogx(w*fs/(2*pi), 20*np.log10(abs(h)))
    >>> plt.grid(True, color='0.7', linestyle='-', which='both', axis='both')
    >>> plt.axis([10, 100e3, -50, 20])

    Since this uses the bilinear transform, frequency response around fs/2 will
    be inaccurate at lower sampling rates.
    """
    z, p, k = abc_weighting('A')

    # Use the bilinear transformation to get the digital filter.
    z_d, p_d, k_d = _zpkbilinear(z, p, k, fs)

    if output == 'zpk':
        return z_d, p_d, k_d
    elif output in {'ba', 'tf'}:
        return zpk2tf(z_d, p_d, k_d)
    elif output == 'sos':
        return zpk2sos(z_d, p_d, k_d)
    else:
        raise ValueError("'%s' is not a valid output form." % output)


def a_weight(signal, fs):
    """
    Return the given signal after passing through a digital A-weighting filter

    signal : array_like
        Input signal, with time as dimension
    fs : float
        Sampling frequency
    """
    # TODO: Upsample signal high enough that filter response meets Type 0
    # limits.  A passes if fs >= 260 kHz, but not at typical audio sample
    # rates. So upsample 48 kHz by 6 times to get an accurate measurement?
    # TODO: Also this could just be a measurement function that doesn't
    # save the whole filtered waveform.
    sos = a_weighting(fs, output='sos')
    return sosfilt(sos, signal)


def _derive_coefficients():
    """
    Calculate A- and C-weighting coefficients with equations from IEC 61672-1

    This is for reference only. The coefficients were generated with this and
    then placed in abc_weighting().
    """
    import sympy as sp

    # Section 5.4.6
    f_r = 1000
    f_l = sp.Pow(10, sp.Rational('1.5'))  # 10^1.5 Hz
    f_h = sp.Pow(10, sp.Rational('3.9'))  # 10^3.9 Hz
    d = sp.sympify('1/sqrt(2)')  # d^2 = 1/2

    f_a = sp.Pow(10, sp.Rational('2.45'))  # 10^2.45 Hz

    # Section 5.4.9
    c = f_l ** 2 * f_h ** 2
    b = (1 / (1 - d)) * (f_r ** 2 + (f_l ** 2 * f_h ** 2) / f_r ** 2 - d * (f_l ** 2 + f_h ** 2))

    f_1 = sp.sqrt((-b - sp.sqrt(b ** 2 - 4 * c)) / 2)
    f_4 = sp.sqrt((-b + sp.sqrt(b ** 2 - 4 * c)) / 2)

    # Section 5.4.10
    f_2 = (3 - sp.sqrt(5)) / 2 * f_a
    f_3 = (3 + sp.sqrt(5)) / 2 * f_a

    # Section 5.4.11
    assert abs(float(f_1) - 20.60) < 0.005
    assert abs(float(f_2) - 107.7) < 0.05
    assert abs(float(f_3) - 737.9) < 0.05
    assert abs(float(f_4) - 12194) < 0.5

    for f in ('f_1', 'f_2', 'f_3', 'f_4'):
        print('{} = {}'.format(f, float(eval(f))))

    # Section 5.4.8  Normalizations
    f = 1000
    c1000 = (f_4 ** 2 * f ** 2) / ((f ** 2 + f_1 ** 2) * (f ** 2 + f_4 ** 2))
    a1000 = (f_4 ** 2 * f ** 4) / ((f ** 2 + f_1 ** 2) * sp.sqrt(f ** 2 + f_2 ** 2) *
                                   sp.sqrt(f ** 2 + f_3 ** 2) * (f ** 2 + f_4 ** 2))

    # Section 5.4.11
    assert abs(20 * log10(float(c1000)) + 0.062) < 0.0005
    assert abs(20 * log10(float(a1000)) + 2.000) < 0.0005

    for norm in ('C1000', 'A1000'):
        print('{} = {}'.format(norm, float(eval(norm))))


if __name__ == '__main__':
    pass
