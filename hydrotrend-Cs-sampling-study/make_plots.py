"""Make plots of the results of Dakotathon experiments."""

import os
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


TRANGE = [10., 20.]
PRANGE = [ 1.,  2.]
CSRANGE = [10., 45.0]

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
    grid_z = griddata(xy_t, z, (grid_x, grid_y), method='linear')
    return (grid_x, grid_y, grid_z)


def make_stacked_surface_plot(x, y, z, outfile='surface.png'):
    X, Y, Z = grid_samples(x, y, z)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.scatter(x, y, zs=CSRANGE[0], s=10, zdir='z', c='r')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.5, color=cmap(0.2))
    plt.title('Hydrotrend: T-P samples and max($C_s}$) response')

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    ax.set_zlim(CSRANGE)
    plt.locator_params(axis='x', nbins=5)
    plt.locator_params(axis='y', nbins=5)
    ax.set_autoscale_on(False)
    ax.set_xlabel(r'$T\ [^{o}C]$')
    ax.set_ylabel('$P\ [m\ yr^{-1}]$')
    ax.set_zlabel('$C_s\ [kg\ m^{-3}]$')
    ax.tick_params(axis='both', labelsize=10)

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_contour_plot(x, y, z, outfile='contour.png'):
    X, Y, Z  = grid_samples(x, y, z)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    nlevels = 8
    clevels = np.linspace(CSRANGE[0], CSRANGE[1], nlevels)
    c = ax.contourf(X, Y, Z, 10, cmap=cmap, antialiased=True, levels=clevels)
    ax.scatter(x, y, s=10, c=cmap(0.9))
    plt.title('Hydrotrend: T-P samples and max($C_s}$) response')

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    plt.locator_params(axis='x', nbins=5)
    plt.locator_params(axis='y', nbins=5)
    ax.set_xlabel(r'$T\ [^{o}C]$')
    ax.set_ylabel('$P\ [m\ yr^{-1}]$')

    cbar = plt.colorbar(c, shrink=0.75, aspect=25, extend='both')
    cbar.ax.set_ylabel('$C_s\ [kg\ m^{-3}]$')

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_pdf_and_cdf_plot(z, outfile='histogram.png'):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    pdf, bins, patches = ax.hist(z, bins=18, normed=True, color=cmap(0.5))
    cdf = np.cumsum(pdf)
    cdf /= cdf.max()
    ax.plot(bins[:-1], cdf, color=cmap(0.1))

    ax.set_xlabel('$C_s\ [kg\ m^{-1}]$')
    ax.set_ylabel('Probability')

    plt.savefig(outfile, dpi=150)
    plt.close()


if __name__ == '__main__':
    experiment_dir = os.getcwd()
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    T = dat[1,]
    P = dat[2,]
    C_s = dat[3,]

    make_stacked_surface_plot(T, P, C_s)
    make_contour_plot(T, P, C_s)
    make_pdf_and_cdf_plot(C_s)
