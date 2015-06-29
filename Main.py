#!/usr/bin/python
## My first python code

##imports:

from ConfigParser import SafeConfigParser
import subprocess
import os
import math
import logging
import ReadConfig as rc
import Interfaces_SPECPAR as isp
import Run_Programs as rp
import read_moog_plot as rmoog
import ARES_MOOG_errors2 as moogerr
import numpy as np


## Global Variables

## My functions:

def plot_MOOG_results(path, filemoog):
  linesfe1=[]
  linesfe2=[]
  (slope_ep, slope_rw, diff_feh)=rmoog.read_moog(filemoog,linesfe1,linesfe2)
  rmoog.plot_graphs(linesfe1,linesfe2)
  
  
def find_iron_parameters(path,run_path,save_folder, linesin):

  converged = False
  owd = os.getcwd()
  moog_file = moog_file = 'Out_moog_'+linesin
  logging.info('Starting 1st iteration for %s', linesin)
  rp.run_amebsa(path,run_path,linesin, 'KURUCZ')
  #checking convergency:
  if os.path.isfile(run_path+moog_file):
    logging.info('First iteration converged for %s', linesin)
  else:
    logging.warning('First iteration did not converge for %s', linesin)
    moog_file = 'Out_moog_b.'+linesin

  n_removed_lines = isp.remove_outliers_from_linelist(run_path+linesin,run_path+moog_file,run_path+linesin+'_new',3.)
  logging.info('Removed %d outliers lines for %s', n_removed_lines, linesin)
  if n_removed_lines > 1:
    linesin=linesin+'_new'
    moog_file = moog_file = 'Out_moog_'+linesin
    logging.info('Starting 2nd iteration for %s', linesin)
    rp.run_amebsa(path,run_path,linesin, 'KURUCZ')
    if os.path.isfile(run_path+moog_file):
      logging.info('Second iteration converged for %s', linesin)
      converged = True
    else:
      logging.error('Final iteration did not converge for %s', linesin)
      moog_file = 'Out_moog_b.'+linesin
  else:
    logging.info('No need for 2nd iteration for %s', filename_lines)
  os.system("cp "+run_path+linesin+" "+save_folder)
  os.system("cp "+run_path+moog_file+" "+save_folder)

  if converged == True:
    logging.info('Computing errors for %s', linesin)
  else:
    logging.warning('Computing errors for no convergent result of %s', linesin)

  # Put a try catch here
  moogerr.compute_error(run_path, moog_file, moog_file+'.er', True) 
  logging.info('Errors computed for %s', linesin)
  os.system("cp "+run_path+moog_file+'.er'+" "+save_folder)
  os.system("cp "+run_path+moog_file+'.eps'+" "+save_folder)

  os.chdir(owd)
  os.system("rm -rf "+run_path+"*")
  
def find_iron_parameters_tmcalc_prior(path,run_path,save_folder, linesin, filename_ares):
  converged = False
  owd = os.getcwd()
  #Default Starting Values
  teff=5500
  logg=4.0
  feh=0.0
  vtur=1.0
  (teff,feh) = rp.get_tmcalc_teff_feh(run_path+filename_ares)
  print teff, feh
  if math.isnan(teff) == True:
    teff=5500
  if math.isnan(feh) == True:
    feh=0.0
# Ramirez 2013    
#  vtur = 1.163 + 7.808e-4 * (teff - 5800) - 0.494*(logg - 4.30) - 0.05*feh
# Tsantaki 2013
  vtur = 6.932e-4*teff - 0.348*logg - 1.437
  logging.info('Using the following parameters as initial: %d %5.2f %5.2f %5.2f', teff, logg, feh, vtur)
  moog_file = moog_file = 'Out_moog_'+linesin
  logging.info('Starting 1st iteration for %s', linesin)
  rp.run_amebsa_prior(path,run_path,linesin,teff,logg,feh,vtur, 'KURUCZ')

  #checking convergency:
  if os.path.isfile(run_path+moog_file):
    logging.info('First iteration converged for %s', linesin)
  else:
    logging.warning('First iteration did not converge for %s', linesin)
    moog_file = 'Out_moog_b.'+linesin
  n_removed_lines = isp.remove_outliers_from_linelist(run_path+linesin,run_path+moog_file,run_path+linesin+'_new',3.)
  logging.info('Removed %d outliers lines for %s', n_removed_lines, linesin)
  if n_removed_lines > 1:
    ## NEED TO GET THE LAST VALUES FROM MOOG
    (teff,logg,feh,vtur) = isp.read_parameters_moogfile(run_path+moog_file)
    linesin=linesin+'_new'
    moog_file = moog_file = 'Out_moog_'+linesin
    logging.info('Starting 2nd iteration for %s', linesin)
    logging.info('Using the following parameters as initial: %d %5.2f %5.2f %5.2f', teff, logg, feh, vtur)
    rp.run_amebsa_prior(path,run_path,linesin,teff,logg,feh,vtur, 'KURUCZ')
    if os.path.isfile(run_path+moog_file):
      logging.info('Second iteration converged for %s', linesin)
      converged = True
    else:
      logging.error('Final iteration did not converge for %s', linesin)
      moog_file = 'Out_moog_b.'+linesin
  else:
    logging.info('No need for 2nd iteration for %s', filename_lines)
  os.system("cp "+run_path+linesin+" "+save_folder)
  os.system("cp "+run_path+moog_file+" "+save_folder)

  if converged == True:
    logging.info('Computing errors for %s', linesin)
  else:
    logging.warning('Computing errors for no convergent result of %s', linesin)

  # Put a try catch here
  moogerr.compute_error(run_path, moog_file, moog_file+'.er', True) 
  logging.info('Errors computed for %s', linesin)
  os.system("cp "+run_path+moog_file+'.er'+" "+save_folder)
  os.system("cp "+run_path+moog_file+'.eps'+" "+save_folder)

  os.chdir(owd)
#  os.system("rm -rf "+run_path+"*")
  
  
def run_chain_parameters():
  os.system("rm -rf SPECPAR.log")
  logging.basicConfig(filename='SPECPAR.log', format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
  logging.info('Started')
  path='./'
  run_path='running_dir/'
  save_path='save_folder/'
  ## CREATE folders

  # # Running ARES
  linelist_ew = rp.get_install_dir()+rc.read_config_param('linelists','iron_parameters').replace("'","")
  rp.ares_make_mine_opt(run_path,linelist_ew)
  logging.info('ARES Started')
  rp.run_ares(run_path)
  logging.info('ARES Finished')
  
  # # Creating moog linelist
  filename_lines = rp.get_install_dir()+rc.read_config_param('linelists','iron_parameters').replace("'","")
  filename_ares = rc.read_config_param('ares','fileout').replace("'","")
  filename_out = 'lines.' + filename_ares
  isp.ares_to_lines(run_path+filename_ares,filename_lines,run_path+filename_out, 4000,9999,5,150)
  logging.info('Starting AMEBSA for %s', filename_out)
#  find_iron_parameters(path,run_path,save_path,filename_out)
  find_iron_parameters_tmcalc_prior(path,run_path,save_path,filename_out,filename_ares)
  logging.info('Finished') 
 
def run_chain_tmcalc():
  
  os.system("rm -rf SPECPAR.log")
  logging.basicConfig(filename='SPECPAR.log', format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
  logging.info('Started')
  path='./'
  run_path='running_dir/'
  save_path='save_folder/'
  ## CREATE folders

  # # Running   ARES
  linelist_ew = rp.get_install_dir()+rc.read_config_param('linelists','tmcalc_linelist').replace("'","")
  rp.ares_make_mine_opt(run_path,linelist_ew)
  logging.info('ARES Started')
  rp.run_ares(run_path)
  logging.info('ARES Finished')
  filename_ares = rc.read_config_param('ares','fileout').replace("'","")
  logging.info('Getting TMCALC results')
  print filename_ares
  (teff,feh) = rp.get_tmcalc_teff_feh(run_path+filename_ares)
  print 'Teff:', teff
  print 'Feh:', feh

def run_chain_get_element_abund(moogfile, element):
  run_path='running_dir/'
  save_path='save_folder/'
  (teff,logg,feh,vtur) = isp.read_parameters_moogfile(moogfile)
  linelist_element=rp.get_install_dir()+rc.read_config_param('linelists',element+'_abund').replace("'","")
  rp.ares_make_mine_opt(run_path,linelist_element)
  rp.run_ares(run_path)
  filename_ares = rc.read_config_param('ares','fileout').replace("'","")
  filename_out = 'lines.' + filename_ares
  isp.ares_to_lines(run_path+filename_ares,linelist_element,run_path+filename_out, 4000,9999,5,150)
  rp.create_abfind_par(run_path,filename_out)
  rp.create_model_kurucz(run_path,teff,logg,feh,vtur)
  rp.run_MOOG(run_path, 'abfind.par')
  (ele1, ele1_sig, nele1, ele2, ele2_sig, nele2) = rmoog.read_moog_ele_sigma(run_path+'abund_plan_tspec.test',element,2.)
  return (ele1, ele1_sig, nele1, ele2, ele2_sig, nele2)

### Main program:
def main():

  print "Testing eclipse push"
#  run_chain_parameters()


#  run_chain_tmcalc()
#  print run_chain_get_element_abund('save_folder/Out_moog_lines.sun.ares_new','Ti')
   
#  # # Genarating atmospheric model
#  rp.create_model_kurucz(path,5777,4.44,0.0,1.0)
#  # # Creating abfind.par
#  rp.create_abfind_par(path,'lines.test.cmine')
#  # # Running MOOG
#  rp.run_MOOG(path, 'abfind.par')
#  # # Plotting MOOG Result
#  plot_MOOG_results(path,'abund_plan_tspec.test')





if __name__ == "__main__":
    main()

