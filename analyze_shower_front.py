import tables
import numpy as np
import matplotlib.pyplot as plt

import utils


def main():
    global data
    data = tables.openFile('data-e15-S250.h5', 'r')
    utils.set_suffix('E_1PeV')

    scatterplot_core_distance_vs_time()
    median_core_distance_vs_time()
    boxplot_core_distance_vs_time()
    hists_core_distance_vs_time()


def scatterplot_core_distance_vs_time():
    plt.figure()

    sim = data.root.showers.E_1PeV.zenith_0
    electrons = sim.electrons

    plt.loglog(electrons[:]['core_distance'], electrons[:]['arrival_time'], ',')
    plt.xlim(xmin=1e0)
    plt.ylim(ymin=1e-3)

    plt.xlabel("Core distance [m]")
    plt.ylabel("Arrival time [ns]")

    utils.title("Shower front timing structure")
    utils.saveplot()

def median_core_distance_vs_time():
    plt.figure()

    sim = data.root.showers.E_1PeV.zenith_0
    electrons = sim.electrons

    bins = np.logspace(0, 3, 25)
    x, y = [], []
    for low, high in zip(bins[:-1], bins[1:]):
        sel = electrons.readWhere('(low < core_distance) & (core_distance <= high)')
        median_arrival_time = np.median(sel[:]['arrival_time'])
        x.append(np.mean([low, high]))
        y.append(median_arrival_time)

    plt.loglog(x, y)

    plt.xlabel("Core distance [m]")
    plt.ylabel("Median arrival time [ns]")

    utils.title("Shower front timing structure")
    utils.saveplot()

def boxplot_core_distance_vs_time():
    plt.figure()

    sim = data.root.showers.E_1PeV.zenith_0
    electrons = sim.electrons

    bins = np.logspace(0, 3, 25)
    x, arrival_time, widths = [], [], []
    for low, high in zip(bins[:-1], bins[1:]):
        sel = electrons.readWhere('(low < core_distance) & (core_distance <= high)')
        x.append(np.mean([low, high]))
        arrival_time.append(sel[:]['arrival_time'])
        widths.append((high - low) / 2)

    plt.boxplot(arrival_time, positions=x, widths=widths)

    plt.xscale('log')
    plt.yscale('log')

    plt.xlim(1e0, 1e3)

    plt.xlabel("Core distance [m]")
    plt.ylabel("Arrival time [ns]")

    utils.title("Shower front timing structure")
    utils.saveplot()

def hists_core_distance_vs_time():
    plt.figure()

    sim = data.root.showers.E_1PeV.zenith_0
    electrons = sim.electrons

    bins = np.logspace(0, 3, 5)
    for low, high in zip(bins[:-1], bins[1:]):
        sel = electrons.readWhere('(low < core_distance) & (core_distance <= high)')
        arrival_time = sel[:]['arrival_time']
        plt.hist(arrival_time, bins=np.logspace(-2, 3, 50), histtype='step',
                 label="%.2f <= log10(R) < %.2f" % (np.log10(low),
                                                    np.log10(high)))

    plt.xscale('log')

    plt.xlabel("Arrival Time [ns]")
    plt.ylabel("Count")
    plt.legend(loc='upper left')

    utils.title("Shower front timing structure")
    utils.saveplot()


if __name__ == '__main__':
    main()