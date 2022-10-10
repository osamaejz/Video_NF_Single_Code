
from DAQ_for_baseline_recording import data_acq
from pylsl import StreamInlet, resolve_stream
import numpy as np
import pandas as pd
from scipy import signal
import time
import vlc
import sys

complete_nf_mean_frequencies = []
complete_samples = []

current_data_sample = []
print("Baseline recording started")

baseline_raw = data_acq("abcd",4)# give filename and time for baseline recording in seconds

print("Baseline recording ended and data processing started")

baseline_raw_array = np.array(baseline_raw)
baseline_raw_array =  np.transpose(baseline_raw_array)

Fs = 500
wL = 4 * Fs
nf_channel = 2

pwelch = signal.welch(baseline_raw_array[nf_channel], fs=Fs, window='hanning', nperseg=wL, noverlap=wL/2, nfft=wL)
baseline_frequency = pwelch[1]

baseline_mean_frequency = np.mean(baseline_frequency)

print("Baseline data processing ended")

media = vlc.MediaPlayer("National Anthem NED.mp4")

check = True
#in_data_check = True # condition for initial 4 seconds data check
try:
        
    # first resolve an EEG stream on the lab network
    print("Starting Realtime NFB")
    print("looking for an EEG stream...")
    
    streams = resolve_stream('type', 'EEG')
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    t1 = time.time()
    t3 = time.time()
    realtime_mean_frequency = 0
    first_play = 1
    
    while check:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
        t2 = time.time()
        sample, timestamp = inlet.pull_sample()
        #time_stamp.append(timestamp)
        complete_samples.append(sample) # this have entire data for csv file 
        
        if (t2-t3<=0.4):#time for computation of 400 ms data
            current_data_sample.append(sample[0])#index value should be change in you want different EEG channel
            #print("cs")
                    
        else:
            t3 = time.time() 
            #print ("time up")
            realtime_data_in_array = np.array(current_data_sample)
            #realtime_frequency = signal.sosfilt(sos1, realtime_data_in_array)

            real_pwelch = signal.welch(realtime_data_in_array, fs=50, window='hanning', nperseg=50*2, noverlap=(50*2)/2, nfft=50*2)
            
            realtime_mean_frequency = np.mean(real_pwelch[1]) # having final data
            
            complete_nf_mean_frequencies.append(realtime_mean_frequency)
            #a = current_data_sample
            current_data_sample = []
            
        if(first_play == 1):
            first_play = 2
            media.play()    
       
        print (t2-t1)
        if realtime_mean_frequency  > baseline_mean_frequency:
            media.play()
            print("Excelent! You are doing great")
                        
        else:
            
             print("You are going wrong.. ")
             media.pause()
        #print(np.shape(complete_samples)[0])
        #if (np.shape(complete_samples)[0] >= nf_time*500):
        if (t2-t1 >= 20):# total time for nf session
        
            print (t2-t3)
            media.pause()
            check = False
            

except KeyboardInterrupt as e:
        print("Ending program")
        raise e



