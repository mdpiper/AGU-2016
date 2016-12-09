"""Make plots of the results of Dakotathon experiments."""

import os
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


TRANGE = [10., 20.]
PRANGE = [ 1.,  2.]
CSRANGE = [0., 500.]

plt.rcParams['mathtext.default'] = 'regular'
cmap = plt.cm.magma


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

    fig, ax = plt.subplots()

    nlevels = 11
    clevels = np.linspace(CSRANGE[0], CSRANGE[1], nlevels)
    c = ax.contourf(X, Y, Z, 10, cmap=cmap, levels=clevels)
    ax.scatter(x, y, s=10, c=cmap(0.9))
    plt.title('Hydrotrend: T-P samples and critical $C_s$ response')

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    plt.locator_params(axis='x', nbins=5)
    plt.locator_params(axis='y', nbins=5)
    ax.set_xlabel(r'$T\ [^{o}C]$')
    ax.set_ylabel('$P\ [m\ yr^{-1}]$')

    cbar = plt.colorbar(c, shrink=0.75, aspect=25)
    cbar.ax.set_ylabel('Critical $C_s$ event count [d]')

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_pdf_and_cdf_plot(z, outfile='histogram.png'):
    fig, ax1 = plt.subplots()

    nbins = 21
    bins = np.linspace(CSRANGE[0], CSRANGE[1], nbins)
    pdf, _, _ = ax1.hist(z, bins=bins, normed=True, color=cmap(0.4))
    plt.title('Hydrotrend: critical $C_s$ response distribution')

    ax1.set_xlabel('Critical $C_s$ event count [d]')
    ax1.set_ylabel('pdf')

    cdf = np.cumsum(pdf)
    cdf /= cdf.max()
    ax2 = ax1.twinx()
    ax2.plot(bins[:-1], cdf, color='b')

    ax2.set_ylabel('cdf')

    cs_mean = 177.35
    cs_stdv = 107.44
    cs_ci_lower = 156.03
    cs_ci_upper = 198.67
    top = ax2.get_ylim()[-1]
    right = ax2.get_xlim()[-1]
    ymrk = 0.95*top
    ax2.plot(cs_mean-cs_stdv, ymrk, '|', color=cmap(0.4), ms=15)
    ax2.plot(cs_mean+cs_stdv, ymrk, '|', color=cmap(0.4), ms=15)
    ax2.plot([cs_mean-cs_stdv, cs_mean+cs_stdv], [ymrk, ymrk], color=cmap(0.4), lw=0.5)
    ax2.plot(cs_mean, ymrk, 's', color=cmap(0.4))
    ax2.plot(cs_ci_lower, ymrk, '|', color=cmap(0.4), ms=10)
    ax2.plot(cs_ci_upper, ymrk, '|', color=cmap(0.4), ms=10)

    cs_median = 157
    RI = 1001. / cs_median
    ax2.text(0.75*right, 0.80*top, 'Median = ' + str(157), ha='center', size=15)
    ax2.text(0.75*right, 0.75*top, 'RI = {:.3} yr'.format(RI), ha='center', size=15)

    plt.savefig(outfile, dpi=150)
    plt.close()


if __name__ == '__main__':
    experiment_dir = os.getcwd()
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    T = dat[1,]
    P = dat[2,]
    nCs40 = dat[3,]

    # make_stacked_surface_plot(T, P, C_s)
    make_contour_plot(T, P, nCs40)
    make_pdf_and_cdf_plot(nCs40)
