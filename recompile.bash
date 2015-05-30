#!/bin/bash

MOOG_Make="make -f Makefile.rh64silent"

function setup_dirs(){
  echo "Creating local directories"
  mkdir running_dir
  mkdir save_folder
  echo "Setting the installation path on code"
  sed -i "21s@.*@  local_install_path=\"$(pwd)/\"@"  Run_Programs.py
}

function compile_ARES(){
  echo "Compiling ARES..." 
  cd ARESv4
  make &> compiling_ares.log
  cd ..
  if [ -f ARESv4/dist/Debug/GNU-Linux-x86/aresv4 ];
  then
    echo "ARES compiled sucessfully"
  else
    echo "ARES did not compile. Check file: ARESv4/compiling_ares.log"
    exit
  fi
}

function compile_interpol(){
  echo "Compiling interpolation of KURUCZ models..." 
  cd interpol_models
  make &> compiling_interpol.log
  cd ..
  echo "Compiling interpolation of MARCS models..." 
  cd interpol_models_marcs
  make &> compiling_interpol.log
  cd ..
}

function compile_MOOG(){
  echo "Compiling MOOG2013..." 
  cd MOOG2013
  echo "Setting the installation MOOG path"
  sed -i "22s@.*@     .  '$(pwd)'@"  Moogsilent.f
  $MOOG_Make &> compiling_MOOG.log
  cd ..
}

function compile_minimization(){
  echo "Compiling minimization Amoeba+Amebsa..." 
  cat Amebsa_tunned/main.cbase | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make &> compiling_amebsa_kur.log
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz
  cd ..
  cat Amebsa_tunned/main.cbase_marcs | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models_marcs/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make &> compiling_amebsa_mar.log
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs
  cd ..
}

function clean_ARES(){
    echo "Cleaning ARES..."
    cd ARESv4
    make clean > /dev/null
    rm -rf compiling_ares.log
    cd ..
}


if [ "$1" = "make" ]; then
  setup_dirs
  compile_ARES
  compile_interpol
  compile_MOOG
  compile_minimization
  echo "Compiling tmcalc module"
  cd tmcalc_cython
  python setup.py build_ext --inplace &> compile_tmcalc.log
  cd ..


else

  if [ $1 = "clean" ]; then
    echo "Deleting Local directories"
    rm -rf running_dir
    rm -rf save_folder
    clean_ARES
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
