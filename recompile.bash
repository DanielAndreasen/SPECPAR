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
  if [[ -f intermod.e && -f transform.e ]]; then
    echo "Interpolation of KURUCZ compiled sucessfully"
  else
    echo "Interpolation of KURUCZ did not compile. Check file: interpol_models/compiling_interpol.log"
    exit
  fi
  cd ..
  echo "Compiling interpolation of MARCS models..." 
  cd interpol_models_marcs
  make &> compiling_interpol.log
  if [[ -f interpol_modeles && -f interpol_marcs ]];
  then
    echo "Interpolation of MARCS compiled sucessfully"
  else
    echo "Interpolation of MARCS did not compile. Check file: interpol_models_marcs/compiling_interpol.log"
    exit
  fi
  cd ..
}

function compile_MOOG(){
  echo "Compiling MOOG2013..." 
  cd MOOG2013
#  echo "Setting the installation MOOG path"
  sed -i "22s@.*@     .  '$(pwd)'@"  Moogsilent.f
  $MOOG_Make &> compiling_MOOG.log
  if [ -f MOOGSILENT ];
  then
    echo "MOOG compiled sucessfully"
  else
    echo "MOOG did not compile. Check file: MOOG2013/compiling_MOOG.log"
    exit
  fi
  cd ..
}

function compile_minimization(){
  echo "Compiling minimization Amoeba+Amebsa..." 
  cat Amebsa_tunned/main.cbase | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make &> compiling_amebsa_kur.log
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz
  if [ -f dist/Debug/GNU-Linux-x86/amebsa_tunned_kurucz ];
  then
    echo "amebsa_tunned_kurucz compiled sucessfully"
  else
    echo "amebsa_tunned_kurucz did not compile. Check file: Amebsa_tunned/compiling_amebsa_kur.log"
    exit
  fi
  cd ..
  cat Amebsa_tunned/main.cbase_marcs | sed s@"FULLMOOGPATHHERE"@"$(pwd)/MOOG2013/./MOOGSILENT"@g | sed s@"INTERPOLPATHHERE"@"$(pwd)/interpol_models_marcs/"@g > Amebsa_tunned/main.c
  cd Amebsa_tunned
  make &> compiling_amebsa_mar.log
  mv dist/Debug/GNU-Linux-x86/amebsa_tunned dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs
  if [ -f dist/Debug/GNU-Linux-x86/amebsa_tunned_marcs ];
  then
    echo "amebsa_tunned_marcs compiled sucessfully"
  else
    echo "amebsa_tunned_marcs did not compile. Check file: Amebsa_tunned/compiling_amebsa_mar.log"
    exit
  fi
  cd ..
}

function compile_tmcalc(){
  echo "Compiling tmcalc module..."
  cd tmcalc_cython
  python setup.py build_ext --inplace &> compiling_tmcalc.log
  if [ -f tmcalc_module.so ];
  then
    echo "tmcalc module compiled sucessfully"
  else
    echo "tmcalc_module did not compile. Check file: tmcalc_cython/compiling_tmcalc.log"
    exit
  fi
  cd ..
}

function clean_ARES(){
  echo "Cleaning ARES..."
  cd ARESv4
  make clean > /dev/null
  rm -rf compiling_ares.log
  cd ..
}

function clean_setup_dirs(){
  echo "Deleting Local directories..."
  rm -rf running_dir
  rm -rf save_folder  
}

function clean_interpolation(){
  echo "Cleaning interpolation of KURUCZ models..." 
  cd interpol_models
  make clean
  rm compiling_interpol.log
  cd ..
  echo "Cleaning interpolation of MARCS models..." 
  cd interpol_models_marcs
  make clean
  rm compiling_interpol.log
  cd ..
}

function clean_MOOG(){
  echo "Cleaning MOOG2013..." 
  cd MOOG2013
  rm *.o MOOGSILENT
  rm compiling_MOOG.log
  cd ..
}

function clean_minimization(){
  echo "Cleaning amebsa+amoeba..." 
  cd Amebsa_tunned
  make clean
  rm  dist/Debug/GNU-Linux-x86/amebsa*
  rm compiling_amebsa_mar.log compiling_amebsa_kur.log
  cd ..
}

function clean_tmcalc(){
  echo "Cleaning tmcalc module..." 
  cd tmcalc_cython
  rm -rf build 
  rm -rf tmcalc_module.so
  rm -rf compiling_tmcalc.log
  cd ..

}


if [ "$1" = "make" ]; then
  setup_dirs
  compile_ARES
  compile_interpol
  compile_minimization
  compile_tmcalc
  echo "SPECPAR compiled sucessfully"
else
  if [ "$1" = "clean" ]; then
    clean_setup_dirs
    clean_ARES
    clean_interpolation
    clean_MOOG
    clean_minimization
    clean_tmcalc
    echo "SPECPAR cleaned sucessfully"
  else
    echo "options are: recompile.bash make/clean"
  fi

fi
