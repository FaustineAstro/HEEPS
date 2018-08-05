#!/usr/bin/env python3
from heeps import pupil, wavefront_abberations, detector, apodization, vortex,lyotstop # loads all HEEPS scripts required for simuation
from copy import deepcopy
import numpy as np
from astropy.io import fits 
from multiprocessing import Pool
from functools import partial

def coronagraphs(wfo, mode, conf):
    if mode == 'APP': 
        RAVC = False    
        lyotstop(wfo, conf, RAVC)
    conf['PHASE_APODIZER_FILE'] = 0
    if mode == 'RAVC':    
        RAVC = True
        apodization(wfo, conf, RAVC=True)
        vortex(wfo, conf)
        lyotstop(wfo, conf, RAVC)
    elif mode == 'VC':
        RAVC = False
        vortex(wfo, conf)
        lyotstop(wfo, conf, RAVC)
    elif mode == 'OFFAXIS':
        print('No Coronagraph')    
        RAVC = False
        lyotstop(wfo, conf, RAVC)
    elif mode == 'MASK':
        print('Ring apodizer and LS present')    
        RAVC = True
        apodization(wfo, conf, RAVC=True)
        lyotstop(wfo, conf, RAVC)
    else:
        print('ELT PSF')    
    return wfo

def check_dim(input):
    r = 0
    try:
        r = input.ndim
    except: AttributeError
    return r

def propagation_test(a,b):
    if check_dim(a)==3 or check_dim(b)==2:
        out = 'mutli'
    else:
        out = 'single'
    return out


def multi_cube(atm_screen,TILT,conf,mode,wfo1,iter):
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
    wavefront_abberations(wfo, conf, atm_screen_iter, TILT_iter)
    coronagraphs(wfo, mode, conf)
    psf = detector(wfo, conf)	
    return psf

        
def metis_hci(mode,conf, atm_screen, TILT):     
    if (propagation_test(atm_screen,TILT)=='single'):
        wfo = pupil(conf) 
        wavefront_abberations(wfo, conf, atm_screen, TILT)
        coronagraphs(wfo, mode, conf)
        psf = detector(wfo, conf)	
        fits.writeto(conf['OUT_DIR'] + conf['PREFIX'] + '_PSF_'+ conf['MODE'] +'.fits', psf, overwrite=True)        
    else:
        if (atm_screen.ndim == 3):
            length_cube = atm_screen.shape[0]
        if (TILT.ndim == 2):
            length_cube = TILT.shape[0]
        wfo1 = pupil(conf)
        p = Pool(2)
        func = partial(multi_cube,atm_screen,TILT,conf,mode,wfo1)
        psf_cube = np.array(p.map(func, range(length_cube)))     
        fits.writeto(conf['OUT_DIR'] + conf['PREFIX'] + '_PSF_cube_'+ conf['MODE'] +'.fits', psf_cube, overwrite=True)
        psf = psf_cube[0]
    return psf


