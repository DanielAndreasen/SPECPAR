#!/bin/bash

MOOG_Make="make -f Makefile.rh64silent"

if [ "$1" = "make" ]; then

  echo "Setting the installation path on code"
  sed -i "21s@.*@  local_install_path=\"$(pwd)/\"@"  Run_Programs.py
  echo "Compiling ARES..." 
  cd ARESv4
  make
  cd ..
  echo "Compiling interpolation of KURUCZ models..." 
  cd interpol_models
  make
  cd ..
  echo "Compiling interpolation of MARCS models..." 
  cd interpol_models_marcs
  make
  cd ..
  echo "Compiling MOOG2013..." 
  cd MOOG2013
  echo "Setting the installation MOOG path"
  sed -i "22s@.*@     .  '$(pwd)'@"  Moogsilent.f
  $MOOG_Make
  cd ..
  echo "Compiling minimization Amoeba+Amebsa..." 
  cat Amebsa_tunned/main.cbase | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz
  cd ..
  cat Amebsa_tunned/main.cbase_marcs | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models_marcs/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs
  cd ..
  cd tmcalc_cython
  python setup.py build_ext --inplace
  cd ..


else

  if [ $1 = "clean" ]; then
    echo "Cleaning ARES..."
    cd ARESv4
    make clean
    cd ..
    echo "Cleaning interpolation of KURUCZ models..." 
    cd interpol_models
    make clean
    cd ..
    echo "Cleaning interpolation of MARCS models..." 
    cd interpol_models_marcs
    make clean
    cd ..
    echo "Cleaning MOOG2013..." 
    cd MOOG2013
    rm *.o MOOGSILENT
    cd ..
    cd Amebsa_tunned
    make clean
    rm  dist/Debug/GNU-Linux-x86/amebsa*
    cd ..
    cd tmcalc_cython
    rm -rf build 
    rm -rf tmcalc_module.so
    cd ..

  else
    echo "options are: recompile.bash make/clean"
  fi

fi
