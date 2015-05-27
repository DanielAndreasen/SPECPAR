#!/usr/bin/python2.7
## S. Sousa
# Code to determine the errors on the stellar parameters, determined by MOOG.
# Plots can be generated as well.
# Based on python script from Annelies, which was 
# Based on an idea in Santos et al. 2000 AND Gonzalez & Vanture
# Partly translated from the sm-code from Nuno
# 
#
# Use: it reads the file "moog_files" in which each line is an "Out_moog_file"
#      moog_errors
#
# Warning!! Change the MOOG-directory down here.
##imports:

import re
import math
import os
import matplotlib.pyplot as plt
import glob
import Run_Programs as rp


## My functions:

#moogcommand = '/home/sousasag/doutoramento/programas/moogbatch2002_nuno/moog2002_minebatch/./MOOG'

def run_moog(teff,logg,metal,vtur):
  run_moog_kurucz(teff,logg,metal,vtur)
#  run_moog_marcs(teff,logg,metal,vtur)

def run_moog_kurucz(teff,logg,metal,vtur):
  rp.create_model_kurucz('./',teff,logg,metal,vtur)
  rp.run_MOOG('./', 'abfind.par')
  
#def run_moog_marcs(teff,logg,metal,vtur):
  #os.system(' interpol_marcs '+str(teff)+' '+str(logg)+' '+str(metal)+' '+str(vtur))
  #os.system('echo abfind.par | ' + moogcommand)


def readmoog(filename):
  """
  # Function that reads the file output by the MOOG and results in the variables.
  """
  with open(filename) as f:
    lines = f.readlines()

  expr1 = re.compile('Teff')
  expr2 = re.compile('#lines')
  expr3 = re.compile('correlation')
  expr4 = re.compile('OH NO')
  Felines = ''
  Correlation = ''
  extraline = 'no'
  atmparam = ''
  for line in lines:
    match1 = expr1.search(line)
    if match1 != None:
      atmparam = match1.string
    match2 = expr2.search(line)
    if match2 != None:
      Felines += match2.string
    match3 = expr3.search(line)
    if match3 != None:
      Correlation += match3.string
    match4 = expr4.search(line)
    if match4 != None:
      extraline = 'yes'

  atmparam = atmparam.split()
  teff = float(atmparam[1])
  logg = float(atmparam[4])
  vt = float(atmparam[6])
  metal = float((atmparam[-1].split('='))[-1])
  
#  if len(atmparam) == 9:
#    metal = float(atmparam[8])
#  if len(atmparam) == 8:
#    print atmparam[7]
#    metal = float((atmparam[7])[4:])
  Felines = Felines.split()

  nfe1 = float(Felines[10])
  nfe2 = float(Felines[21])
  fe1 = float(Felines[3])
  sigfe1 = float(Felines[7])
  fe2 = float(Felines[14])
  sigfe2 = float(Felines[18])
  Correlation = Correlation.split()
  slopeEP = float(Correlation[4])
  #This will catch when you don't have RW statistics in the output, 
  #later bellow it will derive our own slope in this case
  try:
    slopeRW = float(Correlation[16])
  except IndexError:
    slopeRW = 9999.
  # read the actual lines of FeI and FeII

  if extraline == 'yes':
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
    offset1.append(float(line[6].replace('\n','')))
    lam1.append(float(line[0]))

  if extraline == 'yes':
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
    offset2.append(float(line[6].replace('\n','')))
    lam2.append(float(line[0]))
    EP2.append(float(line[1]))
    
  if slopeRW > 9500:
    a,b,sig_a,sig_b=lsq(logRW1,abund1)
    print a,b
    slopeRW = a 
  return teff,logg,vt,metal,nfe1,fe1,sigfe1,nfe2,fe2,sigfe2,slopeEP,slopeRW,abund1,abund2,offset1,offset2,lam1,lam2,EP1,logRW1,EP2



def lsq(x,y):
  """
  # Function to do a least squares fit to a set of vectors
  # Fit line y2=$a*x2+$b to x & y
  # and calculate rms residual
  """
  n = len(x)
  sx = sum(x)
  sy = sum(y)

  x2 = sx / n
  y2 = sy / n

  xy = [(i-x2)*(j-y2) for i,j in zip(x,y)]
  sxy = sum(xy)

  xx = [(i-x2)*(i-x2) for i in x]
  sxx = sum(xx)

  a = sxy / sxx
  b = y2 - a * x2

  axby = [j - a*i - b for i,j in zip(x,y)]
  axby2 = [i*i for i in axby]

  chi2 = sum(axby2)

  sig_a = math.sqrt( chi2 /((n-2)*sxx) ) 
  sig_b = sig_a * math.sqrt(sxx/n + sx*sx / (n*n) )

  return a,b,sig_a,sig_b

def error(filename):
  """
  # Computes the errors
  """

  # Read the file

  logout = readmoog(filename)

  # First determine the set of variables that will be needed to determine the errors.

  teff = logout[0]
  logg = logout[1]
  vt = logout[2]
  metal = logout[3]
  abundfe = (logout[5] + logout[8])/2.
  sigmafe1 = logout[6]/math.sqrt(logout[4])
  sigmafe2 = logout[9]/math.sqrt(logout[7])

  # Do least squaresfits for FeI vs EW and EP

  a1,b1,siga1,sigb1 = lsq(logout[19],logout[12])
  a2,b2,siga2,sigb2 = lsq(logout[18],logout[12])

  # Build new abfind.par file

  linesfile = filename.replace('Out_moog_','')
  linesfile = linesfile.replace('b.','')
  rp.create_abfind_par('./', linesfile)

  # Now for the calculation of the errors

  ##############################
  # VT: Run MOOG with +0.1 dex #
  ##############################

  # Make intermod and transform file

  vtplus = vt + 0.10
  run_moog(teff,logg,metal,vtplus)

  # Read the results

  logoutvt = readmoog('abund_plan_tspec.test')

  # Error on microturbulence

  if logoutvt[11] == 0:
    errormicro = math.fabs(siga1/0.001) * 0.10
  else:
    errormicro = math.fabs(siga1/logoutvt[11]) * 0.10

  # Determine the variation of FeI

  deltafe1micro = math.fabs( (errormicro/0.10) * (logoutvt[5]-abundfe) )


  #########
  # TEFF: #
  #########

  # With these values, calculate the error on the slope of FeI with excitation potential

  addslope = (errormicro/0.10) * logoutvt[10]

  # Add this quadratically to the error on the original FeI-EP slope

  errorslopeEP = math.sqrt(addslope*addslope + siga2*siga2)
               
  # Run MOOG with teff 100K extra

  teffplus = teff +100.
  run_moog(teffplus,logg,metal,vt)

  # Read the results

  logoutteff = readmoog('abund_plan_tspec.test')

  # Error on temperature (suppose the variation on the slope is linear with the error)

  errorteff = math.fabs(errorslopeEP/logoutteff[10]) * 100.

  # Determine the variation of FeI

  deltafe1teff = math.fabs( (errorteff/100.) * (logoutteff[5]-abundfe) )


  #########
  # logg: #
  #########

  # Calculate the variation that the error in Teff caused in the abundances of FeII

  addfe2error = math.fabs( (errorteff/100.) * (logoutteff[8]-abundfe) )

  # Quadratically add it to the original abundance error 

  sigmatotalfe2 = math.sqrt( sigmafe2*sigmafe2 + addfe2error*addfe2error )

  # Run MOOG with logg minus 0.20

  loggminus = logg - 0.20
  run_moog(teff,loggminus,metal,vt)
  # Read the results

  logoutlogg = readmoog('abund_plan_tspec.test')

  # Error on logg

  errorlogg = math.fabs( sigmatotalfe2 / (logoutlogg[8]-abundfe) * 0.2)

  ###########
  # [Fe/H]: #
  ###########
   
  # Take into account the dispersion errors on FeI by teff and vt errors
  # Add them quadratically

  errormetal = math.sqrt(sigmafe1*sigmafe1 + deltafe1teff*deltafe1teff + deltafe1micro*deltafe1micro)


  return teff, errorteff, logg, errorlogg, vt, errormicro, metal, errormetal,logout[4],logout[7],logout[6],logout[9]


def plots(filename,err,par):
  """
  # Program to make plots. If err = 1, errors are also in there, defined in par
  # If err != 1, then the parameters (defined in par) are just shown without errors
  # par is een empty string
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

  fig = plt.figure(figsize=(9,12),frameon=False)

  # Make the plot FeI vs EP

  ax = plt.axes([.1, .7, .8, .2])
  plt.scatter(ep1,abund1,s=25, c='k', marker='o')
  plt.xlabel('EP (ev)')
  plt.ylabel('log FeI')
  a,b,sig_a,sig_b = lsq(ep1,abund1)
  xfit = [min(ep1) - 0.1, max(ep1) + 0.1]
  fit = [a * i + b for i in xfit]
  plt.plot(xfit,fit,c='k')
  plt.text(0.05, 0.05, 'slope = ' + str(round(a,3)), transform = ax.transAxes)

  # Make the plot FeI vs log (RW)

  ax = plt.axes([.1, .4, .8, .2])
  plt.scatter(logrw1,abund1,s=25, c='k', marker='o')
  plt.xlabel('log RW')
  plt.ylabel('log FeI')
  a,b,sig_a,sig_b = lsq(logrw1,abund1)
  xfit = [min(logrw1) - 0.1, max(logrw1) + 0.1]
  fit = [a * i + b for i in xfit]
  plt.plot(xfit,fit,c='k')
  plt.text(0.05, 0.05, 'slope = ' + str(round(a,3)), transform = ax.transAxes)

  # Make the plot FeII vs EP

  ax = plt.axes([.1, .1, .3, .2])
  plt.scatter(ep2,abund2,s=25, c='k', marker='o')
  plt.xlabel('EP (ev)')
  plt.ylabel('log FeII')

  # Put the title on

  starname =filename
#  starname = filename.replace('Out_moog_','')
#  starname = starname.replace('b.','')
#  starname = starname.replace('lines.','')
#  starname = starname.replace('.ares','')
  fig.text(0.5, 0.92, starname, horizontalalignment='center', fontsize=16)

  # Put the abundances with its errors

  fig.text(0.5, 0.29, 'FeI = '+ str(round(logout[5],3)) + u"\u00B1 " + str(round(logout[6],3)))
  fig.text(0.5, 0.26, 'FeII = '+ str(round(logout[8],3)) + u"\u00B1 " + str(round(logout[9],3)))
  fig.text(0.5, 0.23, 'FeI - FeII = '+ str(round(logout[5] - logout[8],3)))

  # Define the errors of the parameters, if available

  errors = [1,1,1,1]
  if err == '1':
    errors[0] = u"\u00B1 " + str(round(par[1],3))
    errors[1] = u"\u00B1 " + str(round(par[3],3))
    errors[2] = u"\u00B1 " + str(round(par[5],3))
    errors[3] = u"\u00B1 " + str(round(par[7],3))

  else:
    errors[0] = par
    errors[1] = par
    errors[2] = par
    errors[3] = par

  # Put the parameters on (maybe with errors)

  fig.text(0.5, 0.18, 'T_eff  = '+ str(round(logout[0],3)) + errors[0])
  fig.text(0.5, 0.15, 'log(g) = '+ str(round(logout[1],3)) + errors[1])
  fig.text(0.5, 0.12, 'v_t    = '+ str(round(logout[2],3)) + errors[2])
  fig.text(0.5, 0.09, '[Fe/H] = '+ str(round(logout[3],3)) + errors[3])

  # Save the figure

  plt.savefig(starname + '.eps')
  
  
def compute_error(path, filelines, fileout, plot_flag):
  owd = os.getcwd()
  os.chdir(path)
  with open(fileout,'w') as bla:
    bla.write('star\tteff\terteff\tlogg\terlogg\tvtur\tervtur\tfeh\terfeh\tNFEI\tNFEII\tsiFEI\tsiFEII\n')
    bla.write('----\t----\t------\t----\t------\t----\t------\t---\t-----\t----\t-----\t-----\t------\n')

  errors = []
  line = filelines
  errors.append(error(line))
  i=0

  print line
  print 'Temperature: ',(errors[i])[0],' +- ',(errors)[i][1]
  print 'logg: ',(errors)[i][2],' +- ',(errors)[i][3]
  print 'Microturbulence: ',(errors)[i][4],' +- ',(errors)[i][5]
  print 'Metallicity: ',(errors)[i][6],' +- ',(errors)[i][7]
  print '-----------------------------------------'
    
  with open(fileout,'a') as bla:
    bla.write('%s\t%4d\t%4d\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%3d\t%3d\t%5.2f\t%5.2f\n' % (line, (errors[i])[0], (errors[i])[1], (errors[i])[2], (errors[i])[3], (errors[i])[4], (errors[i])[5], (errors[i])[6], (errors[i])[7], (errors[i])[8], (errors[i])[9], (errors[i])[10], (errors[i])[11]))
#          bla.write(str(line)+str(' '*4)+str((errors[i])[0])+str(' '*4)+str((errors)[i][1])+str(' '*4)+str((errors)[i][2])+str(' '*4)+str((errors)[i][3])+str(' '*4)+str((errors)[i][4])+str(' '*4)+str((errors)[i][5])+str(' '*4)+str((errors)[i][6])+str(' '*4)+str((errors)[i][7])+'\n')        

  if plot_flag == True:
    plots(line,'1',errors[i])
  os.chdir(owd)  
  
#  os.system('cat *.eps > tmp.eps')
#  os.system('ps2pdf tmp.eps plot_all.pdf')
#  os.system('rm *.eps')


### Main program:
def main():
#  with open('moog_files') as f:
#    moogfiles = f.readlines()
  moogfiles = glob.glob('Out*')
  n = len(moogfiles)
  print n

  with open('finalerrors','w') as bla:
    bla.write(str('Name   Teff    errTeff logg    errlogg     v   errv    [M/H]   err[M/H]')+'\n')          

  with open('file_out.rdb','w') as bla:
    bla.write('star\tteff\terteff\tlogg\terlogg\tvtur\tervtur\tfeh\terfeh\tNFEI\tNFEII\tsiFEI\tsiFEII\n')
    bla.write('----\t----\t------\t----\t------\t----\t------\t---\t-----\t----\t-----\t-----\t------\n')

  for line in moogfiles:
    errors = []
    line = line.replace('\n','')
    errors.append(error(line))
    i=0
    print 'OIOIOI:',len(errors[0])

    print line
    print 'Temperature: ',(errors[i])[0],' +- ',(errors)[i][1]
    print 'logg: ',(errors)[i][2],' +- ',(errors)[i][3]
    print 'Microturbulence: ',(errors)[i][4],' +- ',(errors)[i][5]
    print 'Metallicity: ',(errors)[i][6],' +- ',(errors)[i][7]
    print '-----------------------------------------'
    with open('finalerrors','a') as bla:
      bla.write(str(line)+str(' '*4)+str((errors[i])[0])+str(' '*4)+str((errors[i])[1])+str(' '*4)+str((errors[i])[2])+str(' '*4)+str((errors[i])[3])+str(' '*4)+str((errors[i])[4])+str(' '*4)+str((errors[i])[5])+str(' '*4)+str((errors[i])[6])+str(' '*4)+str((errors[i])[7])+'\n')  
    
    with open('file_out.rdb','a') as bla:
      bla.write('%s\t%4d\t%4d\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%5.2f\t%3d\t%3d\t%5.2f\t%5.2f\n' % (line, (errors[i])[0], (errors[i])[1], (errors[i])[2], (errors[i])[3], (errors[i])[4], (errors[i])[5], (errors[i])[6], (errors[i])[7], (errors[i])[8], (errors[i])[9], (errors[i])[10], (errors[i])[11]))
#          bla.write(str(line)+str(' '*4)+str((errors[i])[0])+str(' '*4)+str((errors)[i][1])+str(' '*4)+str((errors)[i][2])+str(' '*4)+str((errors)[i][3])+str(' '*4)+str((errors)[i][4])+str(' '*4)+str((errors)[i][5])+str(' '*4)+str((errors)[i][6])+str(' '*4)+str((errors)[i][7])+'\n')        
    plots(line,'1',errors[i])


  os.system('cat *.eps > tmp.eps')
  os.system('ps2pdf tmp.eps plot_all.pdf')
  os.system('rm *.eps')
      
if __name__ == "__main__":
  main()

