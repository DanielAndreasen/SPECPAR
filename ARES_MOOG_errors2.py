#!/usr/bin/python2.7
# S. Sousa
# Code to determine the errors on the stellar parameters, determined
# by MOOG. Plots can be generated as well. Based on python script
# from Annelies, which was Based on an idea in Santos et al. 2000 AND
# Gonzalez & Vanture Partly translated from the sm-code from Nuno
#
# Use: it reads the file "moog_files" in which each line is an "Out_moog_file"
#      moog_errors
#
# Warning!! Change the MOOG-directory down here.
# imports:

import re
import math
import numpy as np
import os
import matplotlib.pyplot as plt
from glob import glob
import Run_Programs as rp


# My functions:
def run_moog(teff, logg, metal, vtur):
    run_moog_kurucz(teff, logg, metal, vtur)
#  run_moog_marcs(teff, logg, metal, vtur)


def run_moog_kurucz(teff, logg, metal, vtur):
    rp.create_model_kurucz('./', teff, logg, metal, vtur)
    rp.run_MOOG('./', 'abfind.par')


# def run_moog_marcs(teff, logg, metal, vtur):
#     os.system('interpol_marcs %s %s %s %s' % (teff, logg, metal, vtur))
#     os.system('echo abfind.par | ' + moogcommand)


def readmoog(filename):
    """Function that reads the file output by the MOOG and results in the
    variables.
    """
    with open(filename) as f:
        lines = f.readlines()

    expr1 = re.compile('Teff')
    expr2 = re.compile('#lines')
    expr3 = re.compile('correlation')
    expr4 = re.compile('OH NO')
    Felines = ''
    Correlation = ''
    extraline = False
    atmparam = ''
    for line in lines:
        match1 = expr1.search(line)
        if match1 is not None:
            atmparam = match1.string
        match2 = expr2.search(line)
        if match2 is not None:
            Felines += match2.string
        match3 = expr3.search(line)
        if match3 is not None:
            Correlation += match3.string
        match4 = expr4.search(line)
        if match4 is not None:
            extraline = True

    atmparam = atmparam.split()
    teff = float(atmparam[1])
    logg = float(atmparam[4])
    vt = float(atmparam[6])
    metal = float((atmparam[-1].split('='))[-1])

    Felines = Felines.split()

    nfe1 = int(Felines[10])
    nfe2 = int(Felines[21])
    fe1 = float(Felines[3])
    sigfe1 = float(Felines[7])
    fe2 = float(Felines[14])
    sigfe2 = float(Felines[18])
    correlation = Correlation.split()
    slopeEP = float(correlation[4])
    # This will catch when you don't have RW statistics in the output,
    # later below it will derive our own slope in this case
    try:
        slopeRW = float(correlation[16])
    except IndexError:
        slopeRW = 9999.
    # read the actual lines of FeI and FeII
    if extraline:
        linesFe1 = lines[7:7+int(nfe1)]
    else:
        linesFe1 = lines[6:6+int(nfe1)]
    EP1 = []
    logRW1 = []
    abund1 = []
    offset1 = []
    lam1 = []
    for line in linesFe1:
        line = line.split()
        EP1.append(float(line[1]))
        logRW1.append(float(line[4]))
        abund1.append(float(line[5]))
        offset1.append(float(line[6].strip('\n')))
        lam1.append(float(line[0]))

    if extraline:
        linesFe2 = lines[int(nfe1)+14:int(nfe1)+14+int(nfe2)]
    else:
        linesFe2 = lines[int(nfe1)+13:int(nfe1)+13+int(nfe2)]
    lam2 = []
    offset2 = []
    abund2 = []
    EP2 = []
    for line in linesFe2:
        line = line.split()
        abund2.append(float(line[5]))
        offset2.append(float(line[6].strip('\n')))
        lam2.append(float(line[0]))
        EP2.append(float(line[1]))

    if slopeRW > 9500:
        a, b, sig_a, sig_b = lsq(logRW1, abund1)
        print a, b
        slopeRW = a

    result = (teff, logg, vt, metal, nfe1, fe1, sigfe1, nfe2, fe2, sigfe2,
              slopeEP, slopeRW, abund1, abund2, offset1, offset2, lam1,
              lam2, EP1, logRW1, EP2)
    return result


def lsq(x, y):
    """
    Function to do a least squares fit to a set of vectors
    Fit line y2=$a*x2+$b to x & y
    and calculate rms residual
    """
    n = len(x)
    sx = sum(x)
    sy = np.sum(y)

    x2 = np.mean(x)
    y2 = np.mean(y)

    xy = [(i-x2)*(j-y2) for i, j in zip(x, y)]
    sxy = sum(xy)

    xx = [(i-x2)*(i-x2) for i in x]
    sxx = sum(xx)

    a = sxy / sxx
    b = y2 - a * x2

    axby = [j - a*i - b for i, j in zip(x, y)]
    axby2 = [i*i for i in axby]

    chi2 = sum(axby2)

    sig_a = math.sqrt(chi2 / ((n-2)*sxx))
    sig_b = sig_a * math.sqrt(sxx/n + sx*sx / (n*n))

    return a, b, sig_a, sig_b


def error(filename, fix_logg=False):
    """
    Computes the errors
    """

    # Read the file
    logout = readmoog(filename)

    # First determine the set of variables that will be needed to
    # determine the errors.
    teff = logout[0]
    logg = logout[1]
    vt = logout[2]
    metal = logout[3]
    abundfe = (logout[5] + logout[8])/2.
    sigmafe1 = logout[6]/np.sqrt(logout[4])
    sigmafe2 = logout[9]/np.sqrt(logout[7])

    # Do least squaresfits for FeI vs EW and EP
    a1, b1, siga1, sigb1 = lsq(logout[19], logout[12])
    a2, b2, siga2, sigb2 = lsq(logout[18], logout[12])

    # Build new abfind.par file
    linesfile = filename.replace('Out_moog_', '')
    linesfile = linesfile.replace('b.', '')
    rp.create_abfind_par('./', linesfile)

    ##############################
    # VT: Run MOOG with +0.1 dex #
    ##############################

    # Make intermod and transform file
    run_moog(teff, logg, metal, vt + 0.10)

    # Read the results
    logoutvt = readmoog('abund_plan_tspec.test')

    # Error on microturbulence
    if logoutvt[11] == 0:
        errormicro = abs(siga1/0.001) * 0.10
    else:
        errormicro = abs(siga1/logoutvt[11]) * 0.10

    # Determine the variation of FeI
    deltafe1micro = abs((errormicro/0.10) * (logoutvt[5]-abundfe))

    #########
    # TEFF: #
    #########

    # With these values, calculate the error on the slope of FeI with
    # excitation potential
    addslope = (errormicro/0.10) * logoutvt[10]

    # Add this quadratically to the error on the original FeI-EP slope
    errorslopeEP = np.hypot(addslope, siga2)

    # Run MOOG with teff 100K extra
    run_moog(teff + 100, logg, metal, vt)

    # Read the results
    logoutteff = readmoog('abund_plan_tspec.test')

    # Error on temperature (assume the variation on the slope is linear
    # with the error)
    errorteff = abs(errorslopeEP/logoutteff[10]) * 100

    # Determine the variation of FeI
    deltafe1teff = abs((errorteff/100.) * (logoutteff[5]-abundfe))

    #########
    # logg: #
    #########

    if not fix_logg:
        # Calculate the variation that the error in Teff caused in the
        # abundances of FeII
        addfe2error = abs((errorteff/100.) * (logoutteff[8]-abundfe))

        # Quadratically add it to the original abundance error
        sigmatotalfe2 = np.hypot(sigmafe2, addfe2error)

        # Run MOOG with logg minus 0.20
        run_moog(teff, logg - 0.20, metal, vt)

        # Read the results
        logoutlogg = readmoog('abund_plan_tspec.test')

        # Error on logg
        errorlogg = abs(sigmatotalfe2 / (logoutlogg[8]-abundfe) * 0.2)
    else:
        errorlogg = 0.0

    ###########
    # [Fe/H]: #
    ###########

    # Take into account the dispersion errors on FeI by teff and vt errors
    # Add them quadratically
    print sigmafe1, deltafe1teff, deltafe1micro
    errormetal = math.sqrt(sigmafe1**2 + deltafe1teff**2 + deltafe1micro**2)

    result = (teff, errorteff, logg, errorlogg, vt, errormicro, metal,
              errormetal, logout[4], logout[7], logout[6], logout[9])

    return result


def plots(filename, err, par):
    """
    Program to make plots. If err = 1, errors are also in there, defined
    in par If err != 1, then the parameters (defined in par) are just
    shown without errors par is een empty string
    """

    # Read the moog-file
    logout = readmoog(filename)

    # Get the needed lists
    abund1 = logout[12]
    abund2 = logout[13]
    ep1 = logout[18]
    logrw1 = logout[19]
    ep2 = logout[20]

    # Define the figure
    fig = plt.figure(figsize=(9, 12), frameon=False)

    # Make the plot FeI vs EP
    a, b, sig_a, sig_b = lsq(ep1, abund1)
    xfit = [min(ep1) - 0.1, max(ep1) + 0.1]
    fit = [a * i + b for i in xfit]
    ax = plt.axes([.1, .7, .8, .2])
    plt.scatter(ep1, abund1, marker='o', color='k', s=25)
    plt.xlabel('EP (eV)')
    plt.ylabel('log FeI')
    plt.plot(xfit, fit, '-k')
    plt.text(0.05, 0.05, 'slope = %.3f' % a, transform=ax.transAxes)

    # Make the plot FeI vs log (RW)
    a, b, sig_a, sig_b = lsq(logrw1, abund1)
    xfit = [min(logrw1) - 0.1, max(logrw1) + 0.1]
    fit = [a * i + b for i in xfit]
    ax = plt.axes([.1, .4, .8, .2])
    plt.scatter(logrw1, abund1, marker='o', color='k', s=25)
    plt.xlabel('log RW')
    plt.ylabel('log FeI')
    plt.plot(xfit, fit, '-k')
    plt.text(0.05, 0.05, 'slope = %.3f' % a, 3, transform=ax.transAxes)

    # Make the plot FeII vs EP
    ax = plt.axes([.1, .1, .3, .2])
    plt.scatter(ep2, abund2, marker='o', color='k', s=25)
    plt.xlabel('EP (eV)')
    plt.ylabel('log FeII')

    # Put the title on
    starname = filename
    fig.text(0.5, 0.92, starname, horizontalalignment='center', fontsize=16)

    # Put the abundances with its errors
    fig.text(0.5, 0.29, u'FeI = %.3f\u00B1 %.3f' % (logout[5], logout[6]))
    fig.text(0.5, 0.29, u'FeII = %.3f\u00B1 %.3f' % (logout[8], logout[9]))
    fig.text(0.5, 0.23, 'FeI - FeII = %.3f' % (logout[5] - logout[8]))

    # Define the errors of the parameters, if available
    if err:
        errors = [u'\u00B1 %.3f' % par[i] for i in [1, 3, 5, 7]]
    else:
        errors = [par for _ in range(4)]

    # Put the parameters on (maybe with errors)
    fig.text(0.5, 0.18, 'T_eff  = %.3f(%.3f)' % (logout[0] + errors[0]))
    fig.text(0.5, 0.15, 'log(g) = %.3f(%.3f)' % (logout[1] + errors[1]))
    fig.text(0.5, 0.12, 'v_t    = %.3f(%.3f)' % (logout[2] + errors[2]))
    fig.text(0.5, 0.09, '[Fe/H] = %.3f(%.3f)' % (logout[3] + errors[3]))

    # Save the figure
    plt.savefig(starname + '.eps')


def compute_error(path, filelines, fileout, plot_flag):
    owd = os.getcwd()
    os.chdir(path)
    hdr = '\t'.join(['star', 'teff', 'erteff', 'logg', 'erlogg', 'vtur',
                     'ervtur', 'feh', 'erfeh', 'NFEI', 'NFEII', 'siFEI',
                     'siFEII']) + '\n'
    with open(fileout, 'w') as outfile:
        outfile.write(hdr)
        outfile.write('----\t----\t------\t----\t------\t----\t------\t---\
                       \t-----\t----\t-----\t-----\t------\n')

    line = filelines
    errors = error(line)

    print line
    print 'Temperature: %s +- %s' % (errors[0], errors[1])
    print 'logg: %s +- %s' % (errors[2], errors[3])
    print 'Microturbulence: %s +- %s' % (errors[4], errors[5])
    print 'Metallicity: %s +- %s' % (errors[6], errors[7])
    print '-' * 42

    out = '%s\t%4d\t%4d\t%5.2f\
           \t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%3d\t%3d\t%5.2f\
           \t%5.2f\n' % (line, (errors)[0], (errors)[1], (errors)[2],
                         (errors)[3], (errors)[4], (errors)[5],
                         (errors)[6], (errors)[7], (errors)[8],
                         (errors)[9], (errors)[10], (errors)[11])
    with open(fileout, 'a') as bla:
        bla.write()

    if plot_flag:
        plots(line, True, errors)
    os.chdir(owd)


# Main program:
def main():
    moogfiles = glob('Out*')
    n = len(moogfiles)

    hdr = 'Name   Teff    errTeff logg    errlogg     v   \
           errv    [M/H]   err[M/H]\n'
    with open('finalerrors', 'w') as bla:
        bla.write(hdr)

    for moogfile in moogfiles:
        err = error(moogfile.strip(), fix_logg=True)

        print moogfile
        print 'Temperature: %i +- %i' % (err[0], err[1])
        print 'logg: %.2f +- %.2f' % (err[2], err[3])
        print 'Microturbulence: %.2f +- %.2f' % (err[4], err[5])
        print 'Metallicity: %.2f +- %.2f' % (err[6], err[7])
        print '-' * 42
        with open('finalerrors', 'a') as bla:
            tmp = map(str, err)
            bla.write(str(moogfile)+' '*4+tmp[0]+' '*4 + tmp[1] +
                      ' '*4+tmp[2]+' '*4+tmp[3] +
                      ' '*4+tmp[4]+' '*4+tmp[5] +
                      ' '*4+tmp[6]+' '*4+tmp[7] + '\n')

        with open('file_out.rdb', 'a') as bla:
            bla.write('%s\t%4d\t%4d\t%5.2f\t%5.2f\t%5.2f\
                       \t%5.2f\t%5.2f\t%5.2f\t%3d\t%3d\t\
                       %5.2f\t%5.2f\n' % (moogfile, err[0], err[1],
                                          err[2], err[3],
                                          err[4], err[5],
                                          err[6], err[7],
                                          err[8], err[9],
                                          err[10], err[11]))
        #plots(moogfile, True, err)

    #os.system('cat *.eps > tmp.eps')
    #os.system('ps2pdf tmp.eps plot_all.pdf')
    #os.system('rm *.eps')

if __name__ == "__main__":
    main()
