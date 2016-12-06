"""Make plots of the results of Dakotathon experiments."""

import os
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


TRANGE = [12.8, 15.8]
PRANGE = [1.4, 1.8]
QSRANGE = [0.0, 6.0]

plt.rcParams['mathtext.default'] = 'regular'
cmap = plt.cm.YlGnBu_r


def read_dat_header(dat_file):
    try:
        with open(dat_file, 'r') as fp:
            names = fp.readline().split()
    except IOError:
        pass
    else:
        return names


def read_dat_file(dat_file):
    names = read_dat_header(dat_file)
    rnames = range(len(names))
    rnames.pop(names.index('interface'))
    return np.loadtxt(dat_file, skiprows=1, unpack=True, usecols=rnames)


def grid_samples(x, y, z):
    xy = np.array([x, y])
    xy_t = np.transpose(xy)
    grid_x, grid_y = np.mgrid[TRANGE[0] : TRANGE[1] : complex(20),
                              PRANGE[0] : PRANGE[1] : complex(20)]
    grid_z = griddata(xy_t, z, (grid_x, grid_y), method='cubic')
    return (grid_x, grid_y, grid_z)


def make_stacked_surface_plot(experiment_dir, outfile='surface_plot.png'):
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    T = dat[1,]
    P = dat[2,]
    Qs = dat[3,]
    gT, gP, gQs  = grid_samples(T, P, Qs)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.scatter(T, P, zs=0, s=10, zdir='z', c='r')
    ax.plot_surface(gT, gP, gQs, rstride=1, cstride=1, linewidth=0.5)

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    ax.set_zlim(QSRANGE)
    ax.set_autoscale_on(False)
    ax.set_xlabel(r'$T\ [^{o}C]$')
    ax.set_ylabel('$P\ [m\ yr^{-1}]$')
    ax.set_zlabel('$Qs\ [kg\ s^{-1}]$')
    plt.locator_params(axis='y', nbins=5)
    plt.locator_params(axis='x', nbins=7)
    ax.tick_params(axis='both', labelsize=10)

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_contour_plot(experiment_dir, outfile='contour_plot.png'):
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    T = dat[1,]
    P = dat[2,]
    Qs = dat[3,]
    gT, gP, gQs  = grid_samples(T, P, Qs)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    c = ax.contourf(gT, gP, gQs, 10, cmap=cmap, antialiased=True)
    ax.scatter(T, P, s=10, c='w')
    plt.title('Hydrotrend: T-P samples and $\overline{Qs}$ response')

    plt.locator_params(axis='y', nbins=5)
    plt.locator_params(axis='x', nbins=7)
    ax.set_xlabel(r'$T\ [^{o}C]$')
    ax.set_ylabel('$P\ [m\ yr^{-1}]$')

    cbar = plt.colorbar(c, shrink=0.75, aspect=25)
    cbar.ax.set_ylabel('$Qs\ [kg\ s^{-1}]$')

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_pdf_and_cdf_plot(experiment_dir, outfile='histogram_plot.png'):
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    Qs = dat[3,]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    pdf, bins, patches = ax.hist(Qs, bins=18, normed=True, color=cmap(0.5))
    cdf = np.cumsum(pdf)
    cdf /= cdf.max()
    ax.plot(bins[:-1], cdf, color=cmap(0.1))

    ax.set_xlabel('$Qs\ [kg\ s^{-1}]$')
    ax.set_ylabel('Probability')

    plt.savefig(outfile, dpi=150)
    plt.close()


if __name__ == '__main__':
    experiment_dir = './hydrotrend-sampling-study'
    make_stacked_surface_plot(experiment_dir)
    make_contour_plot(experiment_dir)
    make_pdf_and_cdf_plot(experiment_dir)
