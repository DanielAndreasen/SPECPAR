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
  loggf_out, ew_calc = np.loadtxt(path+'abund_plan_tspec.test', skiprows = 5, usecols = (2, 6), unpack= True)
  return loggf_out, ew_calc

def calib_loggf(path, line_data, loggf_i, loggf_f):
  print line_data
  ew_sun = line_data['ew']
  ew_calc = -1
  loggf = line_data['loggf']
  a1 = loggf_i
  b1 = loggf_f
  i = 0
  while abs(ew_sun - ew_calc) > 0.05 and i < 40:
    i += 1
    c1 = ( b1 - a1 ) / 2. + a1
    print i, ew_sun, ew_calc, c1
    line_data['loggf'] = c1
    loggf_out, ew_calc = get_ew(path, line_data)
    if ew_calc - ew_sun < 0:
      a1=c1
    else:
      b1=c1
#  print ew_calc, ew_sun
#  It is important to be carefull with the use of the loggf vs gf in MOOG"
  if i < 40:
    return loggf_out
  else:
    line_data['loggf']=loggf
    return 10000+loggf



def recalibrate_loggf(path, filein, fileout):
  lines_data = read_linelist_file_ew(path,filein)
  for i,line in enumerate(lines_data):
    print "--->", i, len(lines_data)
    new_loggf = calib_loggf(path, line, -8., -0.1)
    if new_loggf > 1000:
      print "Trying positive numbers"
      new_loggf = calib_loggf(path, line, -0.1, 8.0)
    line['loggf'] = new_loggf
  fileout = open(fileout,'w')
  fileout.write('WL          E.P.     loggf    ele      num    EWsun\n')
  fileout.write('------      -----    -----   ----      ----   -----\n')
  for datai in lines_data:
    fileout.write('%7.2f %8.2f  %9.3f %5s %8.1f %8.1f \n' % (float(datai['lambda_rest']),float(datai['EP']),float(datai['loggf']),datai['ele'],float(datai['atom']),float(datai['ew'])))
  fileout.close()


def recalibrate_loggf_marcs(path, filein, fileout):
  rp.create_model_marcs(path, 5777, 4.44, 0.0, 1.0)
  recalibrate_loggf(path, filein, fileout)

def recalibrate_loggf_kurucz(path, filein, fileout):
  rp.create_model_kurucz(path, 5777, 4.44, 0.0, 1.0)
  recalibrate_loggf(path, filein, fileout)


  


### Main program:
def main():
  path = 'running_dir/'
  recalibrate_loggf_kurucz(path,'../linelistDir/list_iron_complete.dat',path+'list_iron_complete_calibrated_kur.dat')
  recalibrate_loggf_marcs(path,'../linelistDir/list_iron_complete.dat',path+'list_iron_complete_calibrated_mar.dat')

#  rp.create_model_marcs(path, 5777, 4.40, 0.0, 1.0)
#  rp.create_model_kurucz(path, 5777, 4.40, 0.0, 1.0)
#  lines_data = read_linelist_file_ew(path,'../linelistDir/full_linelist.dat')
#  for line in lines_data[:10]:
#    print line['lambda_rest'], line['loggf']
#    new_logf = calib_loggf(path, line)
#    print new_logf


#  create_lines_ew_moog(path+'lines_ew.in', lines_data)
#  rp.ares_make_mine_opt(path,'../linelistDir/full_linelist.dat')
#  rp.run_ares(path)

#  rp.create_ewfind_par(path, linelist)
  
  
  


if __name__ == "__main__":
    main()

