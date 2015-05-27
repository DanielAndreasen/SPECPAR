#!/usr/bin/python
## My first python code
## To create the EW files for GAIA ESO Survey

##imports:
import sys
import re
import numpy as np
from numpy import arange,array,ones,linalg
import matplotlib.pyplot as plt

## My functions:

def read_moog_ele(filenamemoog,linesfe1,linesfe2,ele):
  try:
    filemoog = open (filenamemoog,'r')
  except IOError as e:
    print 'ERROR: File ('+filenamemoog+') not present?'
    sys.exit()
  print 'Reading the file: ' + filenamemoog
  flagfe=0
  slope_ep=0
  slope_rw=0
  diff_feh=0
  feh1=0
  feh2=0
  for line in filemoog:
    line=line.strip()
    m=re.search(r'.*Teff= (\d*)\s*log g= (\d*\.\d*)\s*vt= (\d*\.\d*)\s*\[M/H\]=\s*([-\d]\d*\.\d*).*',  line)
    if m:
      teff= m.group(1)
      logg= m.group(2)
      vt= m.group(3)
      feh= m.group(4)
      print "Parameters:\n----------------------\nTeff logg vtur [Fe/H]\n----------------------"
      print teff, logg, vt, feh
    m=re.search(r'Abundance Results for Species ('+ele+' I\s)\.*',line)
    if m:
#      print m.group(1)
      flagfe=1
    m=re.search(r'Abundance Results for Species ('+ele+' II)\.*',line)
    if m:
#      print m.group(1)
      flagfe=2

    m=re.search(r'[a-z]',line)
    if m == None:
      m=re.search(r'[\d]',line)
      if m:
        if flagfe == 1:
          linesfe1.append(line)
        if flagfe == 2:
          linesfe2.append(line)

    m=re.search(r'E.P. correlation',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        slope_ep=lines[4]
    m=re.search(r'R.W. correlation',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        slope_rw=lines[4]

    m=re.search(r'average abundance',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        feh1=float(lines[3])
      if flagfe == 2:
        lines=line.split()
        feh2=float(lines[3])

#  print len(linesfe1), len(linesfe2)
  diff_feh=feh1-feh2
  return (slope_ep, slope_rw, diff_feh)
 

def get_mean_sigma_outlier(vec,sigma):
  meanvec = np.mean(vec)
  sigmavec = np.std(vec)
  diffvec = vec - meanvec
  mask = np.where(abs(diffvec) < sigma*sigmavec)
  mean2vec = np.mean(vec[mask])
  std2vec = np.std(vec[mask])
  npoints = len(vec[mask])
  return (mean2vec, std2vec, npoints)
  
  
def read_moog_ele_sigma(filenamemoog,ele,sigma):
  ele1 = -999.
  ele1_sig = -1.
  ele2 = -999.
  ele2_sig = -1.
  nele2 = 0
  linesele1=[]
  linesele2=[]
  data = read_moog_ele(filenamemoog,linesele1,linesele2,ele)
  nele1 = len(linesele1)
  nele2 = len(linesele2)
  if nele1 > 0:
    ab=np.array([float(line.split()[5]) for line in linesele1])
    (ele1, ele1_sig, nele1) = get_mean_sigma_outlier(ab,sigma)
  if nele2 > 0:
    ab2=np.array([float(line.split()[5]) for line in linesele2])
    (ele2, ele2_sig, nele2) = get_mean_sigma_outlier(ab2,sigma)
  return (ele1, ele1_sig, nele1, ele2, ele2_sig, nele2)




def read_moog(filenamemoog,linesfe1,linesfe2):
  try:
    filemoog = open (filenamemoog,'r')
  except IOError as e:
    print 'ERROR: File ('+filenamemoog+') not present?'
    sys.exit()
  print 'Reading the file: ' + filenamemoog
  flagfe=0
  slope_ep=0
  slope_rw=0
  diff_feh=0
  feh1=0
  feh2=0
  for line in filemoog:
    line=line.strip()
    m=re.search(r'.*Teff= (\d*)\s*log g= (\d*\.\d*)\s*vt= (\d*\.\d*)\s*\[M/H\]=\s*([-\d]\d*\.\d*).*',  line)
    if m:
      teff= m.group(1)
      logg= m.group(2)
      vt= m.group(3)
      feh= m.group(4)
      print "Parameters:\n----------------------\nTeff logg vtur [Fe/H]\n----------------------"
      print teff, logg, vt, feh
    m=re.search(r'Abundance Results for Species (Fe I\s)\.*',line)
    if m:
#      print m.group(1)
      flagfe=1
    m=re.search(r'Abundance Results for Species (Fe II)\.*',line)
    if m:
#      print m.group(1)
      flagfe=2

    m=re.search(r'[a-z]',line)
    if m == None:
      m=re.search(r'[\d]',line)
      if m:
        if flagfe == 1:
          linesfe1.append(line)
        if flagfe == 2:
          linesfe2.append(line)

    m=re.search(r'E.P. correlation',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        slope_ep=lines[4]
    m=re.search(r'R.W. correlation',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        slope_rw=lines[4]

    m=re.search(r'average abundance',line)
    if m:
      if flagfe == 1:
        lines=line.split()
        feh1=float(lines[3])
      if flagfe == 2:
        lines=line.split()
        feh2=float(lines[3])

#  print len(linesfe1), len(linesfe2)
  diff_feh=feh1-feh2
  return (slope_ep, slope_rw, diff_feh)
    
        
#  fileparam = open ('test_20','r')
#  names=[]
#  for line in fileparam:
#    if not re.match('#', line):
#      line = line.strip()
#      sline = line.split()
#      names.append((sline[3],sline[4],sline[0],sline[5]))
#  return names

def linear_fit(x,y):
  A=array([x,ones(len(x))])
  w = linalg.lstsq(A.T,y)[0] # obtaining the parameOut_moog_lines.test.cmineters
  xline=arange(min(x),max(x),(max(x)-min(x))/100)
  line = w[0]*xline+w[1] # regression line
  return (w,xline,line)
  

def plot_graphs(linesfe1,linesfe2):
  ep=[float(line.split()[1]) for line in linesfe1]
  rw=[float(line.split()[4]) for line in linesfe1]
  ab=[float(line.split()[5]) for line in linesfe1]
  ab2=[float(line.split()[5]) for line in linesfe2]
  fig = plt.figure()
  ax1= fig.add_subplot(2,1,1)
  ax2= fig.add_subplot(2,1,2)
  difffeh=np.mean(ab)-np.mean(ab2)
  stringin='FeI - FeII: %.3f' % difffeh
  ax1.plot(ep[0], ab[0], marker="o",color='b',label=stringin)
  for i in range (1, len(ep)):
    ax1.plot(ep[i], ab[i], marker="o",color='b')
  ax1.set_ylim([7,8])
  ax1.set_xlim(0,max(ep))
  ax1.set_xlabel("E.P.")
  ax1.set_ylabel("Ab FeI")
  # plotting the line
  (w,xline,line) = linear_fit(ep,ab)
#  print w
  stringin='Slope: %.3f' % w[0]
  p1=ax1.plot(xline,line,linestyle='--',color='r', label=stringin)
  for i in range (0, len(rw)):
    ax2.plot(rw[i], ab[i], marker="o",color='b')
  
  ax2.set_ylim([7,8])
  ax2.set_xlim(min(rw),max(rw))
  ax2.set_xlabel("R.W.")
  ax2.set_ylabel("Ab FeI")
  # plotting the line
  (w,xline,line) = linear_fit(rw,ab)
#  print w
  stringin='Slope: %.3f' % w[0]
  p2=ax2.plot(xline,line,linestyle='--',color='r',label=stringin)
  ax1.legend()
  ax2.legend()
  plt.show()

### Main program:
def main():
#  print 'Number of arguments:', len(sys.argv), 'arguments.'
#  print 'Argument List:', str(sys.argv)
  if len(sys.argv) != 3:
    print 'Only 2 argument is needed'
    print 'The argument should be the name of the outputted MOOG file then 0 for no plot, 1 for plot.'
    print 'Example to show plot: ./read_moog_plot.py moog_output.file 1'
    print 'Example without plot: ./read_moog_plot.py moog_output.file 0'
    exit()
  filenamemoog=sys.argv[1]
  flagplot=float(sys.argv[2])
  linesfe1=[]
  linesfe2=[]
  (slope_ep, slope_rw, diff_feh)=read_moog(filenamemoog,linesfe1,linesfe2)
#  print slope_ep, slope_rw, diff_feh
#  print len(linesfe1), len(linesfe2)
  if flagplot > 0.5: 
    plot_graphs(linesfe1,linesfe2)
  else:
    print '-----------------------------'
    print '|  Slope  E.P. :'+slope_ep
    print '|  Slope  R.W. :'+slope_rw
    print '|  Fe I - Fe II:'+str(diff_feh)
    print '-----------------------------'

  

if __name__ == "__main__":
    main()

