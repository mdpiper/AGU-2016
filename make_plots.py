"""Make plots of the results of Dakotathon experiments."""

import numpy as np
import matplotlib.pyplot as mpl



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


def make_stacked_surface_plot():
    pass


def make_pdf_and_cdf_plot():
    pass


if __name__ == '__main__':
    make_stacked_surface_plot()
    make_pdf_and_cdf_plot()
