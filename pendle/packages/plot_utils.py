import numpy as np
import matplotlib.pyplot as plt

def plot_signals(ROI_gauss, freqs, fourier, fourier_average, bpm_cache, ax):
    # Clear the axes
    for row in ax:
        for a in row:
            a.clear()

    # Plot the raw signal
    raw_signal = np.real(ROI_gauss).mean(axis=(1, 2, 3))
    ax[0, 0].plot(raw_signal, color='black') 
    ax[0, 0].set_title("Raw Signal")
    ax[0, 0].set_xlabel("Frame")
    ax[0, 0].set_ylabel("Amplitude")

    # Plot the frequency signals
    ax[0, 1].plot(fourier, color='black')
    ax[0, 1].set_title("Frequency Signals")
    ax[0, 1].set_xlabel("Frequency (Hz)")
    ax[0, 1].set_ylabel("Amplitude")

    # Plot the filtered Fourier transform data
    ax[1, 0].plot(freqs, np.abs(fourier_average), color='black')
    ax[1, 0].set_title("Filtered Signals")
    ax[1, 0].set_xlabel("Frequency (Hz)")
    ax[1, 0].set_ylabel("Amplitude")
    
    # Plot the BPM
    ax[1, 1].plot(bpm_cache[-30:], color='black')
    ax[1, 1].set_title("Heart Rate")
    ax[1, 1].set_xlabel("Sample")
    ax[1, 1].set_ylabel("BPM")
    
    plt.tight_layout()
    plt.ion()
    plt.draw()
    plt.pause(0.001)