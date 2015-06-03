#!/usr/bin/python
## My first python code

##imports:

import subprocess
import os
import ReadConfig as rc


## Global Variables


## My functions:


def get_install_dir():
  """
  Set the local variables with the instalation path
  """
  local_install_path="/home/sousasag/Programas/GIT_projects/SPECPAR/"
#  return read_config_install('specpar','install_path')
  return local_install_path

import sys
sys.path.insert(0, get_install_dir()+'tmcalc_cython')

import tmcalc_module as tm


def ares_make_mine_opt(path,linelist_ew):
  """
  Read the parameters from the configuration file and 
  build a local 'mine.opt' file to run the ARES code
  """
  file_mineopt = open(path+'mine.opt','w')
  file_mineopt.write('specfits='+rc.read_config_param('ares','specfits')+'\n')  
  file_mineopt.write('readlinedat='+"'"+linelist_ew+"'\n")
  file_mineopt.write('fileout='+rc.read_config_param('ares','fileout')+'\n')
  file_mineopt.write('lambdai='+rc.read_config_param('ares','lambdai')+'\n')
  file_mineopt.write('lambdaf='+rc.read_config_param('ares','lambdaf')+'\n')
  file_mineopt.write('smoothder='+rc.read_config_param('ares','smoothder')+'\n')
  file_mineopt.write('space='+rc.read_config_param('ares','space')+'\n')
  file_mineopt.write('rejt='+rc.read_config_param('ares','rejt')+'\n')
  file_mineopt.write('lineresol='+rc.read_config_param('ares','lineresol')+'\n')
  file_mineopt.write('miniline='+rc.read_config_param('ares','miniline')+'\n')
  file_mineopt.write('plots_flag=0'+'\n')
  file_mineopt.write('rvmask='+rc.read_config_param('ares','rvmask')+'\n')
  file_mineopt.close()


def run_ares(path):
  """
  Runs the ARES code locally and waits until it finishes.
  """
  owd = os.getcwd()
  os.chdir(path)
  process = subprocess.Popen(get_install_dir()+'ARESv4/dist/Debug/GNU-Linux-x86/aresv4', shell=True)
  process.wait()
  print process.returncode
  os.chdir(owd)

def create_model_kurucz(path, teff, logg, feh, vtur):
  
  owd = os.getcwd()
  os.chdir(path)
  command = get_install_dir()+'interpol_models/make_model_gfortran.bash '+str(teff)+' '+str(logg)+' '+str(feh)+' '+str(vtur)
  process = subprocess.Popen(command, shell=True)
  process.wait()
  os.chdir(owd)

def create_model_marcs(path, teff, logg, feh, vtur):
  
  owd = os.getcwd()
  os.chdir(path)
  command = get_install_dir()+'interpol_models_marcs/make_model_marcs.bash '+str(teff)+' '+str(logg)+' '+str(feh)+' '+str(vtur)
  # just to keep the same file name... might be useful
  os.system("mv out_marcs.atm out.atm")
  process = subprocess.Popen(command, shell=True)
  process.wait()
  os.chdir(owd)


def create_abfind_par(path, linelist_ares):
  owd = os.getcwd()
  os.chdir(path)
  os.system("cp "+get_install_dir()+"Amebsa_tunned/abfind.par.base abfind.par")
  os.system("echo \"lines_in      '"+linelist_ares+"'\" >> abfind.par" )
  os.chdir(owd)

def create_ewfind_par(path, linelist_ares):
  owd = os.getcwd()
  os.chdir(path)
  os.system("cp "+get_install_dir()+"Amebsa_tunned/ewfind.par.base ewfind.par")
  os.system("echo \"lines_in      '"+linelist_ares+"'\" >> ewfind.par" )
  os.chdir(owd)


def run_MOOG(path, driver):
  owd = os.getcwd()
  os.chdir(path)
  os.system("echo "+driver+" | "+get_install_dir()+"MOOG2013/./MOOGSILENT > /dev/null 2>&1")
  os.system("rm a")
  os.chdir(owd)

def run_amebsa_prior(path,run_path,filename_lines,teff, logg, feh, vtur, models):
  owd = os.getcwd()
  os.chdir(path)
  os.chdir(run_path)
  os.system('echo "" > star_file')  
  os.system('echo "" >> star_file')
  os.system('echo '+filename_lines+' '+str(teff)+' '+str(logg)+' '+str(vtur)+' '+str(feh)+' >> star_file')
  os.system('cp '+ get_install_dir()+'Amebsa_tunned/abfind.par.base .')
  if models == 'MARCS':
    process = subprocess.Popen(get_install_dir()+'Amebsa_tunned/dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs', shell=True)
  else:
    process = subprocess.Popen(get_install_dir()+'Amebsa_tunned/dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz', shell=True)
  process.wait()
  os.chdir(owd)

def run_amebsa(path,run_path,filename_lines, models):
  """
  models = 'MARCS' -> it will run with MARCS models
  Else it will run with KURUCZ models
  """
  owd = os.getcwd()
  os.chdir(path)
  os.chdir(run_path)
  os.system('echo "" > star_file')  
  os.system('echo "" >> star_file')
  os.system('echo '+filename_lines+' >> star_file')
  os.system('cp '+ get_install_dir()+'Amebsa_tunned/abfind.par.base .')
  if models == 'MARCS':
    process = subprocess.Popen(get_install_dir()+'Amebsa_tunned/dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs', shell=True)
  else:
    process = subprocess.Popen(get_install_dir()+'Amebsa_tunned/dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz', shell=True)
  process.wait()
  os.chdir(owd)
  
def get_tmcalc_teff_feh(filename_ares):
  (teff,erteff,erteff2,erteff3,nout,nindout) = tm.get_temperature_py(get_install_dir()+'tmcalc_cython/ratios_list.dat', filename_ares)
  (fehout, erfehout, nout) = tm.get_feh_py(get_install_dir()+'tmcalc_cython/feh_calib_lines.dat', filename_ares, teff, erteff, erteff2, erteff3)
  return (teff,fehout)


### Main program:
def main():

  print "Nothing to do here"


if __name__ == "__main__":
    main()

