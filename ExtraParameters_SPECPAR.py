#!/usr/bin/python
## My first python code

##imports:

import numpy as np
import Util
import math
import urllib2
import re
import os

## My functions:

def correct_logg_transit_mortier(loggin, teff):
  """
  Correct a logg from ARES+MOOG accordingly with Mortier et al. 2014 using transit data
  Valid for 4500 < teff < 6500
  """
  return -4.57e-4*teff+2.59+loggin

def correct_logg_astero_mortier(loggin, teff):
  """
  Correct a logg from ARES+MOOG accordingly with Mortier et al. 2014 using asteroseismic data
  Valid for 5000 < teff < 6500
  """
  return -3.89e-4*teff+2.10+loggin


def radius_torres2010(teff,logg,feh):
  """
  Get the radius of a star using the Torres calibrations from 2010
  """
  bi=[2.4427,0.6679,0.1771,0.705,-0.21415, 0.02306,0.04173]
#  ebi=[0.038,0.016,0.027,0.13,0.0075,0.0013,0.0082]
  X=math.log(teff,10)-4.1
  logR=bi[0]+bi[1]*X+bi[2]*X**2.+bi[3]*X**3+bi[4]*logg**2+bi[5]*logg**3+bi[6]*feh
  RT=10**logR
  return (RT)
  

def mass_torres2010(teff,logg,feh):
  """
  Get the mass of a star using the Torres calibrations from 2010
  """
  ai=[1.5689,1.3787,0.4243,1.139,-0.1425,0.01969,0.1010]
#  eai=[0.058,0.029,0.029,0.24,0.011,0.0019,0.014]
  X=math.log(teff,10)-4.1
  logM=ai[0]+ai[1]*X+ai[2]*X**2.+ai[3]*X**3+ai[4]*logg**2+ai[5]*logg**3+ai[6]*feh
  MT=10**logM
  Mcor = 0.791*MT**2.-0.575*MT+0.701 # Santos et al 2013 correction
  return (MT,Mcor)
  
def bc_flower(teff):
  """
  Get the bolometric correction using the relations from flower 1996
  """
  lteff=np.log10(teff)
  if (lteff<3.7):
    bcflow=-0.190537291496456e+05+0.155144866764412e+05*lteff-0.421278819301717e+04*(lteff*lteff)+0.381476328422343e+03*(lteff*lteff*lteff)
  if (lteff>=3.7 and lteff<3.9):
    bcflow=-0.370510203809015e+05+0.385672629965804e+05*lteff-0.150651486316025e+05*(lteff*lteff)+0.261724637119416e+04*(lteff*lteff*lteff)-0.170623810323864e+03*(lteff*lteff*lteff*lteff)
  if (lteff>=3.9):
    bcflow=-0.370510203809015e+05+0.385672629965804e+05*lteff-0.150651486316025e+05*(lteff*lteff)+0.261724637119416e+04*(lteff*lteff*lteff)-0.170623810323864e+03*(lteff*lteff*lteff*lteff)
  return bcflow
  
def get_hipparcus_paralaxe(hipnumber):
  """
  Get the paralaxe, its error, and the v mag from the hipparcus catalogues
  """
  print os.path.dirname(__file__)
  hip,par,erpar = np.loadtxt(os.path.dirname(__file__)+'/hipparcus_data/Main_Cat.rdb', skiprows=2, usecols = (0,6,11), unpack=True)
  itemindex = np.where(hip==hipnumber)
  if len(itemindex) == 0:
    print "No Hipparcus data"
    return -1
  paralaxe = par[itemindex][0]
  error_par = erpar[itemindex][0]
  hip,v = np.loadtxt(os.path.dirname(__file__)+'/hipparcus_data/myhip.rdb', skiprows=2, usecols = (1,5), unpack=True)
  itemindex = np.where(hip==hipnumber)
  vmag = v[itemindex][0]
  return (paralaxe, error_par, vmag)
  
def create_Padova_url(star, teff, erteff, feh, erfeh, V, eV, plx, eplx):
  strurl = 'http://stev.oapd.inaf.it/cgi-bin/param_1.3?param_version=1.3&star_name=%s&star_teff=%5d&star_sigteff=%5d&star_feh=%6.2f&star_sigfeh=%6.2f'
  strurl+= '&flag_sismo=0&star_vmag=%6.2f&star_sigvmag=%6.2f&star_parallax=%7.2f&star_sigparallax=%6.2f&isoc_kind=parsec_CAF09_v1.1'
  strurl+= '&imf_file=tab_imf/imf_chabrier_lognormal.dat&sfr_file=tab_sfr/sfr_const_z008.dat&sfr_minage=0.1e9&sfr_maxage=12.0e9'
  strurl+= '&photsys_file=tab_mag/tab_mag_ubvrijhk.dat&.cgifields=isoc_kind&submit_form=Submit'
  strurl = strurl % (star, teff, erteff, feh, erfeh, V, eV, plx, eplx)
  strurl=strurl.replace(" ","")
  return strurl

def get_url(strurl):
  filepadova = urllib2.urlopen(strurl)
  lines = filepadova.readlines()
  for line in lines:
    #print line
    if re.search("Results for" , line):
      line=line.replace(".<p>Results for","").replace("&plusmn;",",").replace(":   Age=",",").replace("Gyr , Mass=",",").replace("<i>M</i>&#9737 , log<i>g</i>=",",").replace("(cgs) , <i>R</i>=",",").replace("<i>R</i>&#9737 ,",",").replace(", (<i>B-V</i>)<sub>0</sub>=",",").replace("mag","")
      line = line.strip().split(",")
      #print line
      age = float(line[1])
      erage = float(line[2])
      mass = float(line[3])
      ermass = float(line[4])
      logg = float(line[5])
      erlogg = float(line[6])
      radius = float(line[7])
      erradius = float(line[8])
      bv = float(line[9])
      erbv = float(line[10])
      return (age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv)
  return -1


def get_padova_data(star, teff, erteff, feh, erfeh, V, eV, plx, eplx):
  """
  Get the padova parameters from the web interface http://stev.oapd.inaf.it/cgi-bin/param_1.3
  using the paralaxe as a input - For some reason does not work in some systems...
  """

  strurl = create_Padova_url(star, teff, erteff, feh, erfeh, V, eV, plx, eplx)
  return get_url(strurl)

def get_padova_data_old(star, teff, erteff, feh, erfeh, V, eV, plx, eplx):
  """
  Get the padova parameters from the web interface http://stev.oapd.inaf.it/cgi-bin/param_1.3
  using the paralaxe as a input - For some reason does not work in some systems...
  """
  strurl = 'http://stev.oapd.inaf.it/cgi-bin/param_1.3?param_version=1.3&star_name=%s&star_teff=%5d&star_sigteff=%5d&star_feh=%6.2f&star_sigfeh=%6.2f'
  strurl+= '&flag_sismo=0&star_vmag=%6.2f&star_sigvmag=%6.2f&star_parallax=%7.2f&star_sigparallax=%6.2f&isoc_kind=parsec_CAF09_v1.1'
  strurl+= '&imf_file=tab_imf/imf_chabrier_lognormal.dat&sfr_file=tab_sfr/sfr_const_z008.dat&sfr_minage=0.1e9&sfr_maxage=12.0e9'
  strurl+= '&photsys_file=tab_mag/tab_mag_ubvrijhk.dat&.cgifields=isoc_kind&submit_form=Submit'
  strurl = strurl % (star, teff, erteff, feh, erfeh, V, eV, plx, eplx)
  strurl=strurl.replace(" ","")
  print strurl
  print 'INFO: Getting data from padova interface ... Enjoy the view outside the window for a few seconds'
  filepadova = urllib2.urlopen(strurl)
  lines = filepadova.readlines(filepadova)
  for line in lines:
    if re.search("Results for" , line):
      print line
      line=line.replace(".<p>Results for","").replace("&plusmn;",",").replace(":   Age=",",").replace("Gyr , Mass=",",").replace("<i>M</i>&#9737 , log<i>g</i>=",",").replace("(cgs) , <i>R</i>=",",").replace("<i>R</i>&#9737 ,",",").replace(", (<i>B-V</i>)<sub>0</sub>=",",").replace("mag","")
      line = line.strip().split(",")
      print line
      age = float(line[1])
      erage = float(line[2])
      mass = float(line[3])
      ermass = float(line[4])
      logg = float(line[5])
      erlogg = float(line[6])
      radius = float(line[7])
      erradius = float(line[8])
      bv = float(line[9])
      erbv = float(line[10])
      return (age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv)
  return -1

def get_mass_padova_iter(star, teff, erteff, logg, erlogg, feh, erfeh, mass_ini, mv, bcflow):
  """
  Get the padova parameters from the web interface http://stev.oapd.inaf.it/cgi-bin/param_1.3
  without the knowledge of the paralaxe which is then determined iteratively together with the mass and using the logg from spectroscopy
  """
  diff_mass = 1
  massi = mass_ini
  iteration = 1
  ermv = 0.05
  erpar=1
  while (diff_mass > 0.005):
    parit= 10.0**((logg - 4.44 - np.log10(massi) - 4.0*np.log10(teff) + 4.0*np.log10(5777) - 0.4*(mv + bcflow) - 0.11)*0.5)*1000.
    print "Iteration: %d   Estimated mass: %f   Estimated paralaxe:  %f " %  (iteration, massi, parit)
    (age,erage,masso,ermasso,loggo,erloggo,radius,erradius,bv,erbv) = get_padova_data(star, teff, erteff, feh, erfeh, mv, ermv, parit, erpar)
    diff_mass = abs(masso-massi)
    iteration+=1
    massi=masso
  return (age,erage,masso,ermasso,loggo,erloggo,radius,erradius,bv,erbv, parit)
    

def get_paralax_torres(star, teff, logg, feh, mv):
  """
  Get paralax using the mass from torres calibration and the bolometric correction from flower
  """
  (massi,massicor)=mass_torres2010(teff,logg,feh)
  bcflow = bc_flower(teff)
  par= 10.0**((logg - 4.44 - np.log10(massi) - 4.0*np.log10(teff) + 4.0*np.log10(5777) - 0.4*(mv + bcflow) - 0.11)*0.5)*1000.
  parcor= 10.0**((logg - 4.44 - np.log10(massicor) - 4.0*np.log10(teff) + 4.0*np.log10(5777) - 0.4*(mv + bcflow) - 0.11)*0.5)*1000.
  return (par,parcor)

def get_padova_stars(filenamein,filenameout):
  """
  filein needs the following format:

  star  teff  erteff  logg  erlogg  feh erfeh V eV  Plx e_Plx
  ----  ----  ------  ----  ------  --- ----- - --  --- -----
  HD121370  6080  44  3.78  0.15  0.33  0.04  2.68  0.05  87.75 1.24
  Kepler-410A 6375  44  4.25  0.15  0.09  0.04  9.50  0.05  -1  -1

  fileout will be like:

  star  age erage mass  ermass  logg  erlogg  radius  erradius  bv  erbv  par par_ref
  ----  --- ----- ----  ------  ----  ------  ------  --------  --  ----  --- -------
  HD121370  2.037 0.111 1.648 0.022 3.787 0.019 2.628 0.065 0.630 0.012 87.750  hip
  Kepler-410A 1.415 0.913 1.290 0.042 4.247 0.081 1.371 0.146 0.558 0.010 6.451 ite
  """

  fileout = open(filenameout,'w')
  fileout.write("star\tage\terage\tmass\termass\tlogg\terlogg\tradius\terradius\tbv\terbv\tpar\tpar_ref\n")
  fileout.write("----\t---\t-----\t----\t------\t----\t------\t------\t--------\t--\t----\t---\t-------\n")
  teff, erteff, loggs, erloggs, feh, erfeh, V, eV, Plx, e_Plx = np.loadtxt(filenamein, skiprows=2,usecols = (1,2,3,4,5,6,7,8,9,10), unpack=True)
  star = np.loadtxt(filenamein, skiprows=2,usecols = (0,),dtype='str')

  nstars = len(star)

 #name  age erage mass  ermass  loggm erloggm rad errad bvm erbvm

  for i in range(nstars):
    print star[i], i+1, ' out of ', nstars
    if Plx[i] > 0:
      print "Getting Padova with paralaxe defined"
      (age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv) = get_padova_data(star[i], teff[i], erteff[i], feh[i], erfeh[i], V[i], eV[i], Plx[i], e_Plx[i]) 
      strout = "%s\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\thip\n" % (star[i],age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv,Plx[i])
    else:
      print "Getting Padova iterative paralaxe/mass process"
      (MTin,MTcor)=mass_torres2010(teff[i],loggs[i],feh[i])
      bcflowin = bc_flower(teff[i])
      (age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv,parit) = get_mass_padova_iter(star[i], teff[i], erteff[i], loggs[i], erloggs[i], feh[i], erfeh[i], MTin, V[i], bcflowin)
      strout = "%s\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\t%5.3f\tite\n" % (star[i],age,erage,mass,ermass,logg,erlogg,radius,erradius,bv,erbv,parit)
    print strout
    fileout.write(strout)
  fileout.close()



### Main program:
def main():
#  path = '/home/sousasag/Programas/SPECPAR/'
  path = './'
  
  teffin=5777
  loggin=4.44
  fehin=0.00
  (MT,MTcor)=mass_torres2010(teffin,loggin,fehin)
  print "Mass Torres:", MT
  print "Mass Torres Corrected:", MTcor
  print bc_flower(5777)
  
  #print get_hipparcus_paralaxe(1234)

  #print get_padova_data('HD 179949', 6237, 	30, 	0.17, 	0.03, 	6.25, 	0.05, 	36.30, 	0.70)
  
  starin="HD102200"
  teffin = 6185
  erteffin = 65
  loggin = 4.59
  erloggin = 0.04
  fehin = -1.10
  erfehin = 0.05
  (MTin,MTcor)=mass_torres2010(teffin,loggin,fehin)
  mvin = 8.75
  bcflowin = bc_flower(teffin)
  print MTin, bcflowin
  print get_mass_padova_iter(starin,teffin,	erteffin,	loggin,	erloggin,	fehin,erfehin,	MTin,	mvin,	bcflowin)
  print get_paralax_torres(starin, teffin, loggin, fehin, mvin)
  
  


if __name__ == "__main__":
    main()

