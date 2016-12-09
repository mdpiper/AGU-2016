"""Make plots of the results of Dakotathon experiments."""

import os
import numpy as np
from scipy.interpolate import griddata
import statsmodels.stats.api as sms
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


RUN_DURATION = 1000.0  # yr
TRANGE = [12.5, 16.0]
PRANGE = [ 1.4,  1.8]
RIRANGE = [4., 14.]

plt.rcParams['mathtext.default'] = 'regular'
cmap = plt.cm.magma_r


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


def calculate_recurrence_interval(n_Cs):
    return (RUN_DURATION + 1)/n_Cs


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

    ax.scatter(x, y, zs=RIRANGE[0], s=10, zdir='z', c='r')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, linewidth=0.5, color=cmap(0.2))
    plt.title('Hydrotrend: T-P samples and max($C_s}$) response')

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    ax.set_zlim(RIRANGE)
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
    clevels = np.linspace(RIRANGE[0], RIRANGE[1], nlevels)
    c = ax.contourf(X, Y, Z, 10, cmap=cmap, levels=clevels)
    ax.scatter(x, y, s=10, c=cmap(0.9))
    plt.suptitle('Hydrotrend: samples and recurrence interval', fontsize=20)

    ax.set_xlim(TRANGE)
    ax.set_ylim(PRANGE)
    plt.locator_params(axis='x', nbins=5)
    plt.locator_params(axis='y', nbins=5)
    ax.set_xlabel(r'$T\ [^{o}C]$', fontsize=18)
    ax.set_ylabel('$P\ [m\ yr^{-1}]$', fontsize=18)

    cbar = plt.colorbar(c, shrink=0.75, aspect=25)
    cbar.ax.set_ylabel('RI [yr]', fontsize=18)

    plt.savefig(outfile, dpi=150)
    plt.close()


def make_pdf_and_cdf_plot(z, outfile='histogram.png'):
    fig, ax1 = plt.subplots()

    nbins = 21
    bins = np.linspace(RIRANGE[0], RIRANGE[1], nbins)
    pdf, _, _ = ax1.hist(z, bins=bins, normed=True, color=cmap(0.5))
    plt.suptitle('Hydrotrend: recurrence interval distribution', fontsize=20)

    ax1.set_ylim(0.0, 0.4)
    ax1.set_xlabel('RI [yr]', fontsize=18)
    ax1.set_ylabel('pdf', fontsize=18)

    cdf = np.cumsum(pdf)
    cdf /= cdf.max()
    ax2 = ax1.twinx()
    ax2.plot(bins[:-1], cdf, color='b', lw=1.5)

    ax2.set_ylabel('cdf', fontsize=18)

    ri_median = np.median(z)
    ri_mean = z.mean()
    ri_stdv = z.std()
    ri_ci = sms.DescrStatsW(z).tconfint_mean()
    top = ax2.get_ylim()[-1]
    right = ax2.get_xlim()[-1]
    ymrk = 0.95*top
    ax2.plot([ri_mean-ri_stdv, ri_mean+ri_stdv], [ymrk, ymrk], color=cmap(0.5), lw=0.75)
    ax2.plot(ri_ci, [ymrk, ymrk], '|', color=cmap(0.5), ms=10, mew=1)
    ax2.plot(ri_mean, ymrk, 's', color=cmap(0.5), ms=5)
    ax2.plot(ri_median, ymrk, 'D', color=cmap(0.5), ms=5)

    print 'mean = {}'.format(ri_mean)
    print 'median = {}'.format(ri_median)
    print 'std = {}'.format(ri_stdv)
    print 'ci = {}'.format(ri_ci)

    plt.savefig(outfile, dpi=150)
    plt.close()


if __name__ == '__main__':
    experiment_dir = os.getcwd()
    dat_file = os.path.join(experiment_dir, 'dakota.dat')
    dat = read_dat_file(dat_file)

    T = dat[1,]
    P = dat[2,]
    n_Cs = dat[3,]

    RI = calculate_recurrence_interval(n_Cs)

    # make_stacked_surface_plot(T, P, C_s)
    make_contour_plot(T, P, RI)
    make_pdf_and_cdf_plot(RI)
