#!/usr/bin/env python3

# =============================================================================
#       Example file for creating a multi-cube PSF
# =============================================================================

# Required libraries
import proper # library for propagation of wavefront
import matplotlib.pyplot as plt # for plotting simulated PSFs
import numpy as np
from astropy.io import fits    # to read and write fits files

from simulation_config import *	# Loads default configuration for simulation (later will be changed to dictinary)
from heeps import * # loads all HEEPS scripts required for simuation
from copy import deepcopy

#  default simulation cofiguration defined in "simulation_config" can be overridden here
wavelength = 3.80*10**-6
charge = 2 # charge is modified here
TILT = np.random.randn(10,2)

# =============================================================================
#                         ELT Pupil Plane
# =============================================================================

(npupil, wfo1) = pupil(diam, gridsize, spiders_width, spiders_angle, pixelsize,  r_obstr, wavelength,
          pupil_file=pupil_file, missing_segments_number=0, Debug=Debug, Debug_print=Debug_print, prefix=prefix) 
  

# =============================================================================
#                     Multi-cube phase screens / abberations
# =============================================================================

if (atm_screen.ndim == 3) or (TILT.ndim == 2) or (LS_misalignment.ndim == 2) or (apodizer_misalignment.ndim == 2) or (Island_Piston.ndim == 2) or (NCPA.ndim == 3):
   
    if (atm_screen.ndim == 3):
        length_cube = atm_screen.shape[0]
    if (TILT.ndim == 2):
        length_cube = TILT.shape[0]
    if (LS_misalignment.ndim == 2):
        length_cube = LS_misalignment.shape[0]
    if (apodizer_misalignment.ndim == 2):
        length_cube = apodizer_misalignment.shape[0]
    if (Island_Piston.ndim == 2):
        length_cube = Island_Piston.shape[0]
    if (NCPA.ndim == 3):
        length_cube = NCPA.shape[0]
    
    psf_Coro = np.zeros((length_cube,nd,nd))
  
    for iter in range(0, length_cube):
        wfo = deepcopy(wfo1)

        if ((isinstance(atm_screen, (list, tuple, np.ndarray)) == True)):
            if (atm_screen.ndim == 3):
                atm_screen_iter = atm_screen[iter,:,:]
            else:
                atm_screen_iter = atm_screen
        if (TILT.ndim == 2):
            TILT_iter = TILT[iter,:]
        else:
            TILT_iter = TILT
        if (LS_misalignment.ndim == 2):
            LS_misalignment_iter =  LS_misalignment[iter,:]
        else:
            LS_misalignment_iter =  LS_misalignment
        if (apodizer_misalignment.ndim == 2):
            apodizer_misalignment_iter = apodizer_misalignment[iter,:]
        else:
            apodizer_misalignment_iter = apodizer_misalignment
        if (Island_Piston.ndim == 2):
            Island_Piston_iter = Island_Piston[iter,:]
        else:
            Island_Piston_iter = Island_Piston          
        if (isinstance(NCPA, (list, tuple, np.ndarray)) == True):
            if (NCPA.ndim == 3):
                NCPA_iter = NCPA[iter,:,:]
            else:
                NCPA_iter = NCPA
                
#       Wavefront abberations
        wavefront_abberations(wfo, npupil, atm_screen_iter, NCPA,Island_Piston,TILT=TILT_iter, Debug='False',Debug_print='False', prefix='test')  
 
#       Coronagraph selection -- Classical Vortex / RAVC / APP --
        coronagraphs(wfo, r_obstr,npupil, phase_apodizer_file,amplitude_apodizer_file,apodizer_misalignment,charge,
              f_lens,diam,LS_amplitude_apodizer_file,LS_misalignment,LS,LS_parameters,spiders_angle, LS_phase_apodizer_file, Debug_print,pixelsize, Debug, coronagraph_type= coronagraph_type)

#       Detector plane      
        psf = detector(wfo,f_lens,nd)	
        psf_Coro[iter,:,:] = psf       
    fits.writeto(out_dir + prefix + '_PSF_cube_'+coronagraph_type+'.fits', psf_Coro, overwrite=True)


        
plt.figure()
plt.imshow(np.sqrt(psf_Coro[1]))
plt.colorbar()

plt.show()

