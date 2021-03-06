# -*- coding: utf-8 -*-

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from soundscape_IR.soundscape_viewer.utility import pulse_interval
from soundscape_IR.soundscape_viewer import spectrogram_detection
import numpy as np

import copy 

class Sound_visualization:
   
    def sound_visualization(clip,select_f_range=[],plot_t_range=[],plot_f_range=[],pulse_interval_plot=False,pulse_interval_energy_percentile=50,pulse_interval_range=[5, 20],ICI_plot=False,ICI_threshold=12, ICI_min_interval=0.005, ICI_f_count=10,vmin=None,vmax=None,plot_title=[],save_plot=[]):
      ###Normalization
      clip_copy=copy.deepcopy(clip)
      old_sf=clip_copy.sf
    
      if select_f_range:
        f_list0=(clip_copy.f>=min(select_f_range))*(clip_copy.f<=max(select_f_range))
        f_list=np.where(f_list0==True)[0]
        clip_copy.data[:,1:]=clip_copy.data[:,1:]*f_list0
        clip_copy.sf=clip_copy.f[-1]*2
      else:
        f_list=np.arange(len(clip_copy.f))
        clip_copy.sf=clip_copy.f[-1]*2
      clip_copy.f=clip_copy.f[f_list]
      clip_copy.FFT_size=int(clip_copy.FFT_size*clip_copy.sf/old_sf)
      clip_copy.convert_audio(clip_copy.data)
      waveform=clip_copy.xrec/np.max(np.abs(clip_copy.xrec))
      
      ##PSD analysis
    
      mean_input_data=np.power(10,clip_copy.data[:,1:]/10).mean(axis=0)[f_list]
      mean_input_data2=10*np.log10(mean_input_data)
      median_input_data=np.median(np.power(10,clip_copy.data[:,1:]/10),axis=0)[f_list]
      median_input_data2=10*np.log10(median_input_data)
    
      if ICI_plot==True:
        fig = plt.figure(figsize=(14, 9),constrained_layout=True)
        gs = gridspec.GridSpec(3, 2, figure=fig, width_ratios=[0.7, 0.3])
      else:
        fig = plt.figure(figsize=(14, 6),constrained_layout=True)
        gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[0.7, 0.3])
      
      if plot_title:
        fig.suptitle(plot_title,fontsize=16)
    
      ###plot1
      ax1 = fig.add_subplot(gs[0, 0])
      im = ax1.imshow(clip_copy.data[:,1:][:,f_list].T,
                      vmin=vmin, vmax=vmax,
                      origin='lower',  aspect='auto', cmap=cm.jet,
                  extent=[0,len(waveform)/clip_copy.sf, clip_copy.f[0], clip_copy.f[-1]], interpolation='none')
      ax1.set_title('Spectrogram')
      ax1.set_ylabel('Frequency')
      ax1.set_xlabel('Time')
      cbar = fig.colorbar(im, ax=ax1, aspect=80)
      cbar.set_label('PSD')
    
      ###plot2
      ax2 = fig.add_subplot(gs[1, 0])
      ax2.plot(np.arange(1,len(waveform)+1)/(clip_copy.sf), waveform)
      ax2.set_title('Waveform')
      ax2.set_ylabel('Normalized amplitude')
      ax2.set_xlabel('Time')
      ax2.set_xlim(0, len(waveform)/clip_copy.sf)
      ax2.set_ylim(-1,1)
    
      if plot_t_range:
        ax2.axvspan(plot_t_range[0],plot_t_range[1], alpha=0.3, color='lightgray')
    
      ###plot3
      ax3 = fig.add_subplot(gs[0, 1])
      ax3.plot(mean_input_data2,clip_copy.f, linewidth=2,color='blue')
      ax3.plot(median_input_data2,clip_copy.f, linewidth=2,color='red')
      ax3.set_ylim(clip_copy.f[0], clip_copy.f[-1])
      ax3.set_xlim(0, 1.1*np.max(mean_input_data2))
    
      if plot_f_range:
        ax3.axhspan(plot_f_range[0],plot_f_range[1], alpha=0.3, color='lightgray')
        
      ax3.set_title('PSD')
      ax3.set_ylabel('Frequency')
      ax3.set_xlabel('Signal-to-noise ratio')
      ax3.fill_betweenx(clip_copy.f,mean_input_data2,median_input_data2,alpha=1,color= 'lightgray')
      #plot4
      if pulse_interval_plot==True:
        pulse_interva=pulse_interval(clip_copy.data[:,np.append(0,f_list)], energy_percentile=pulse_interval_energy_percentile, interval_range=pulse_interval_range, plot_type='None')
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(pulse_interva.PI, pulse_interva.result)
        ax4.set_title('Pulse interval')
    
        ax4.set_xlabel('Lagged time (ms)')
        ax4.set_ylabel('Correlation score')
      if ICI_plot==True:
        detection = spectrogram_detection(clip.data, clip.f, threshold=ICI_threshold, minimum_interval=ICI_min_interval, frequency_count=ICI_f_count,filename=[])
        detection_time=detection.detection[0:-1,0]-clip.data[0,0]
        ICI=1000*(detection.detection[1:,0]-detection.detection[0:-1,0])
    
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.scatter(x=detection_time, y=ICI)
        ax4.set_yscale("log")
        ax4.set_xlim([0,clip.data[-1,0]-clip.data[0,0]])
        ax4.set_ylim([1,200])
        ax4.set_xlabel('Time (sec)')
        ax4.set_ylabel('Inter-click interval')
        ax4.set_title('Inter-click interval')
    
      if save_plot:
        plt.savefig(save_plot)