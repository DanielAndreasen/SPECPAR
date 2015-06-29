#!/usr/bin/python

import numpy as np
import Util
import read_moog_plot as rmoog
import re


def remove_outliers_from_linelist(linelist, moog_result, new_linelist, nsigma):
    """
    From a linelist with a correspondent moog result will create a new
    linelist with some outlier removal at sigma sigma
    """
    linesfe1 = []
    linesfe2 = []
    data = rmoog.read_moog(moog_result, linesfe1, linesfe2)
    abfe1 = np.array([float(val.split()[5]) for val in linesfe1])
    llfe1 = np.array([float(val.split()[0]) for val in linesfe1])
    abfe2 = np.array([float(val.split()[5]) for val in linesfe2])
    llfe2 = np.array([float(val.split()[0]) for val in linesfe2])
    mfe1 = abfe1.mean()
    stdfe1 = abfe1.std()
    mfe2 = abfe2.mean()
    stdfe2 = abfe2.std()

    # Getting the lines to be removed
    ll_remove1 = llfe1[abs(abfe1[i]-mfe1) > nsigma*stdfe1]
    ll_remove2 = llfe2[abs(abfe2[i]-mfe2) > nsigma*stdfe2]
    ll_remove = np.concatenate((ll_remove1, ll_remove2))

    with open(linelist, 'r') as lines:
        lines_filein = lines.readlines()

    with open(new_linelist, 'w') as fileout:
        fileout.write(lines_filein[0])
        for line in lines_filein[1:]:
            ll = float(line.strip().split()[0])
            res = np.where(abs(ll_remove-ll) < 0.1)
            if len(res[0]) == 0:
                fileout.write(line)

    return len(ll_remove)


def read_ares_file_old(path, fileares):
    """
    Read the ares old output file into a numpy array
    with the respective names in the columns
    """
    # TODO: Maybe you can just have 'fname' as input which is the full path?
    # TODO: Do you really need a rec array here (array with names)? It is
    # easier to read with normal numpy.loadtxt
    data = np.loadtxt(path+fileares,
                      dtype={'names': ('lambda_rest', 'ngauss', 'depth', 'fwhm', 'ew', 'c1', 'c2', 'c3'),
                             'formats': ('f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4')})
    return data


def read_ares_file(path, fileares):
    """
    Read the ares new output file into a numpy array
    with the respective names in the columns
    """
    # TODO: Same as above...
    data = np.loadtxt(path+fileares, dtype={'names': ('lambda_rest', 'ngauss', 'depth', 'fwhm', 'ew', 'ew_er', 'c1', 'c2', 'c3'),
                                            'formats': ('f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4')})
    return data


def read_linelist_file(path, filelinelist):
    """
    Read the linelist file into a numpy array
    with the respective names in the columns
    This skips header with 2 lines
    """
    # TODO: And again...
    data = np.loadtxt(path+filelinelist, dtype={'names': ('lambda_rest', 'EP', 'loggf', 'ele', 'atom'),
                                                'formats': ('f4', 'f4', 'f4', 'a4', 'f4')},
                      skiprows=2)
    return data


def ares_get_fwhm_average(ares_data):
    """
    Returns the average fwhm of the measured lines
    """
    fwhm_arr = ares_data['fwhm']
    data, mask = Util.sigma_clip(fwhm_arr, 2, 3)
    return np.mean(data)


def make_lines_moog_file(filename, filename_out, ares_data, linelist_data,
                         llmin, llmax, ewmin, ewmax):
    """
    Creates the lines.file.ares formated for moog with the atomic data
    """
    fileout = open(filename_out, 'w')
    fileout.write(' '+filename+'\n')
    for datai in ares_data:
        lambda_ares = datai['lambda_rest']
        # Below (commented) solution is easier to read
        # atomic_data = linelist_data[abs(lambda_ares-linelist_data['lambda_rest']) < 0.1]
        atomic_data = linelist_data[np.where(abs(lambda_ares-linelist_data['lambda_rest']) < 0.1)]
        ew = datai['ew']
        # Look here for another way of saving the data: https://github.com/DanielAndreasen/astro_scripts/blob/master/numpy2moog.py#L14
        if len(atomic_data) > 0 and ew < ewmax and ew > ewmin and lambda_ares > llmin and lambda_ares < llmax:
            print '{: 9.2f}{: 8.1f}{: 12.2f}{: 11.3f}{: 28.1f}'.format(float(datai['lambda_rest']),float(atomic_data['atom']),float(atomic_data['EP']),float(atomic_data['loggf']),float(datai['ew']))
            fileout.write('{: 9.2f}{: 8.1f}{: 12.2f}{: 11.3f}{: 28.1f}\n'.format(float(datai['lambda_rest']),float(atomic_data['atom']),float(atomic_data['EP']),float(atomic_data['loggf']),float(datai['ew'])))


def ares_to_lines(filename_ares, filename_lines, filename_out,
                  llmin, llmax, ewmin, ewmax):
    """
    This is actually the public function that transforms a file into
    another file
    """
    ares_data = read_ares_file("", filename_ares)
    linelist_data = read_linelist_file("", filename_lines)
    make_lines_moog_file(filename_ares, filename_out, ares_data,
                         linelist_data, llmin, llmax, ewmin, ewmax)


def read_parameters_moogfile(filename_moog):
    with open(filename_moog, 'r') as f:
        lines = f.readlines()

    expr1 = re.compile('Teff')
    atmparam = ''
    for line in lines:
        match1 = expr1.search(line)
        if match1 is None:
            atmparam = match1.string

    atmparam = atmparam.split()
    teff = float(atmparam[1])
    logg = float(atmparam[4])
    vtur = float(atmparam[6])
    feh = float((atmparam[-1].split('='))[-1])
    return (teff, logg, feh, vtur)


def main():
    # path = '/home/sousasag/Programas/SPECPAR/'
    path = './'
    path_linelist = './linelistDir/'
    file_ares = 'test.cmine'
    file_linelist = 'riscas_harps_ok1_50x4500.dat'
    ares_data = read_ares_file(path, file_ares)
    linelist_data = read_linelist_file(path_linelist, file_linelist)
    # print data_ares
    # print data_ares['lambda_rest']
    print ares_get_fwhm_average(ares_data)
    filename_out = 'lines.'+file_ares
    make_lines_moog_file(file_ares, filename_out, ares_data, linelist_data,
                         4000, 9999, 5, 150)

if __name__ == "__main__":
    main()
