#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:07:02 2020

@author: arsi

Plot and save similairity matrix
"""


from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from datetime import datetime
from setup import setup_np
from plot_decorator import plot_decorator
import pytest


plt.rcParams.update({'figure.max_open_warning': 0})

@plot_decorator
def Plot_similarity(sim,
                    nov,
                    title="Similarity and novelty",
                    savepath = False, 
                    savename = False,
                    ylim = (0,0.05),
                    threshold = 0,
                    axis = False,
                    kernel = False,
                    ):
    """
    Plot the similarity matrix. Optionally save the figure, plot the kernel, 
    and plot the similarity score.
    
    Parameters
    ----------
    sim : Numpy ndarray
        m x m array containing similarity values
    nov : Numpy ndarray
        m x 1 array containing  novelty scores
        
    title : str, optional
            Similarity plot title. The default is "Similarity and novelty".
    
    savepath : Path object, optional
            Path for figure saving. The default is False.
    
    savename : str object, optional
            Savename for the figure. The default is False.
    
    ylim : tuple, optional
            (float,float) ylimits for the plot. The default is (0,0.05).
    
    threshold : float, optional
            Similarity score threshold for showing in the plot. The default is 0.
    
    axis : pandas.core.indexes.base.Index, optional
            Date range used in the novelty score plot. The default is False.
    
    kernel : Numpy ndarray, optional
            m x m convolution kernel used for novelty score calculation. The default is False.

    Raises
    ------
    Exception
        - Requested save folder does not exist
        - Savename and/or savename are not given

    Returns
    -------
    None.

    """
     
    assert isinstance(sim,np.ndarray), "Similarity matrix type is not np.ndarray."
    assert isinstance(nov,np.ndarray), "Novelty score array type is not np.ndarray."

    sim[sim < threshold] = 0
    # plot it
    fig, ax = plt.subplots(4,4,figsize=(8.3,9.5),sharex=True)  
    gridsize = (4,4)
    ax1 = plt.subplot2grid(gridsize, (0,0), colspan=3,rowspan=3)
    ax2 = plt.subplot2grid(gridsize, (1,3), colspan=1,rowspan=1)
    ax3 = plt.subplot2grid(gridsize, (3,0), colspan=4,rowspan=1)
    
    ax1.imshow(sim,cmap="Blues", origin='lower')
    ax1.set_title("Similarity matrix (cosine distance)", fontsize=22)
    ax1.set_xlabel('$m = {}$'.format(sim.shape[0]),fontsize=16)
    ax1.set_ylabel('$n = {}$'.format(sim.shape[1]),fontsize=16)
    #ax1.text(-0.1, 1.05, "A", fontsize=26, fontweight='bold', transform=ax1.transAxes,va='top', ha='right')
    
    
    if type(kernel) != bool:
        ax2.imshow(kernel,cmap='Blues')
        ax2.set_title('Kernel',fontsize=22)
        #ax[1,3].text(-0.1, 1.05, "B", fontsize=26, fontweight='bold', transform=ax1.transAxes,va='top', ha='right')
    
    #ax1 = plt.subplot(gs[1])
 
    ax3.plot(axis,nov,label="Novelty")
    ax3.set_title("Novelty score", fontsize=22)
    ax3.set_xlabel('Time (date)',fontsize=16)
    ax3.set_ylabel('Novelty',fontsize=16)
    ax3.set_xticks(np.arange(len(axis))[::7])
    ax3.set_xticklabels(axis[::7])
    #ax2.axvspan(datetime(2020,7,1),datetime(2020,7,15),facecolor="red",alpha=0.15,label="Days of interest")
    ax3.axvspan(29,43,facecolor="red",alpha=0.15,label="Days of interest")
    ax3.legend(fontsize=16)
    ax3.set_ylim(ylim)
    #ax[3,0].set_text(-0.1, 1.05, "C", fontsize=26, fontweight='bold', transform=ax1.transAxes,va='top', ha='right')

        
    #ax[3,0].set_text(-0.1, 1.05, "C", fontsize=26, fontweight='bold', transform=ax1.transAxes,va='top', ha='right')
    ax[0,3].set_axis_off()
    ax[2,3].set_axis_off()
    
    plt.suptitle(title + " Daily Patterns",fontsize=26,y=1.03)
    plt.grid(True)
    plt.tight_layout(pad=0)
    
    
     
def test_Plot_similarity():
    from setup import setup_pd, setup_np
    #test_fig = Summary_statistics(setup_ps(), savepath = False, savename = False, test = True)
    #assert test_fig is not None
    
    # Store information about raised ValueError in exc_info
    with pytest.raises(AssertionError) as exc_info:
        Plot_similarity(setup_pd(),setup_np())
    expected_error_msg = "Similarity matrix type is not np.ndarray."
    # Check if the raised ValueError contains the correct message
    assert exc_info.match(expected_error_msg)