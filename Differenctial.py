#!/usr/bin/python
## My first python code

##imports:

import numpy as np
import Run_Programs as rp




## My functions:

def read_linelist_file_ew(path,filelinelist):
  """
  Read the linelist file into a numpy array  
  with the respective names in the columns
  This skips header with 2 lines
  """
  data = np.loadtxt(path+filelinelist, dtype={'names': ('lambda_rest', 'EP', 'loggf', \
    'ele', 'atom', 'ew' ),'formats': ('f4', 'f4', 'f4', 'a4','f4', 'f4')},skiprows=2)
  return data

def create_lines_ew_moog(filename_out,lines_data):
  """
  The lines data should be read by read_linelist_file_ew
  """
  fileout = open(filename_out,'w')
  fileout.write(' '+filename_out+'\n')
  for datai in lines_data:
    fileout.write('{: 9.2f}{: 8.1f}{: 12.2f}{: 11.3f}{: 28.1f}\n'.format(float(datai['lambda_rest']),float(datai['atom']),float(datai['EP']),float(datai['loggf']),float(datai['ew'])))
  fileout.close()

def get_ew(path, line_data):
  create_lines_ew_moog(path+'lines_ew.in', [line_data])
  rp.create_ewfind_par(path,'lines_ew.in')
  rp.run_MOOG(path,'ewfind.par')
  ew_calc = np.loadtxt(path+'abund_plan_tspec.test', skiprows = 5, usecols = (6,), unpack= True)
  return ew_calc

def calib_loggf(path, line_data):
  ew_sun = line_data['ew']
  ew_calc = -1
  loggf = line_data['loggf']
  a1 = -8.
  b1 = -0.1
  i = 0
  while abs(ew_sun - ew_calc) > 0.05:
    i += 1
    c1 = ( b1 - a1 ) / 2. + a1
#    print i, ew_sun, ew_calc, c1
    line_data['loggf'] = c1
    ew_calc = get_ew(path, line_data)
    if ew_calc - ew_sun < 0:
      a1=c1
    else:
      b1=c1
#  print ew_calc, ew_sun
  return c1


  


### Main program:
def main():
  path = 'running_dir/'
  rp.create_model_marcs(path, 5777, 4.40, 0.0, 1.0)
#  rp.create_model_kurucz(path, 5777, 4.40, 0.0, 1.0)
  lines_data = read_linelist_file_ew(path,'../linelistDir/full_linelist.dat')
  for line in lines_data[:10]:
    print line['lambda_rest'], line['loggf']
    new_logf = calib_loggf(path, line)
    print new_logf


#  create_lines_ew_moog(path+'lines_ew.in', lines_data)
#  rp.ares_make_mine_opt(path,'../linelistDir/full_linelist.dat')
#  rp.run_ares(path)

#  rp.create_ewfind_par(path, linelist)
  
  
  


if __name__ == "__main__":
    main()

