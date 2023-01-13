#### libraries ####
library(readr)
library(dplyr)
library(stringr)
library(ggplot2)
library(patchwork)

#### data folders ####
DATA_FOLDER <- "~/Library/CloudStorage/OneDrive-Linköpingsuniversitet/projects - in progress/touch comm MNG Kinect/"

#### read in the data ####
ex <- read_csv(paste0(DATA_FOLDER, "data_contact-IFF/2022-06-22/unit1/2022-06-22_15-42-14_controlled-touch-MNG_ST18_1_block4.csv"))

# notes from Shan about the data:
# the csv file contains the contact features as 
# raw data (named as xxRaw), interpolated data (named as xx), smoothed data (named as xxSmooth), 
# 1st derivative (named as xx1D), and 2nd derivative (named as xx2D). 
# The contact data were upsampled and the neural data were downsampled to both 1000Hz.
# the units for first and second derivatives are 
# cm/s2 for velocity1D, cm/s for depth1D, and cm2/s for area1D 

#### plot a single session ####

iff <- ex %>% 
  mutate(spike_label = if_else(spike == 1, "|", "")) %>% 
  ggplot(aes(x = t, y = IFF)) +
  geom_line(colour = "blue") +
  geom_text(aes(y = -15, label = spike_label))

area <- ex %>% 
  ggplot(aes(x = t, y = areaSmooth)) +
  geom_line(colour = "red") 

depth <- ex %>% 
  ggplot(aes(x = t, y = depthSmooth)) +
  geom_line(colour = "red") 

velAbs <- ex %>% 
  ggplot(aes(x = t, y = velAbsSmooth)) +
  geom_line(colour = "red") 

velLat <- ex %>% 
  ggplot(aes(x = t, y = velLatSmooth)) +
  geom_line(colour = "red") 

velLong <- ex %>% 
  ggplot(aes(x = t, y = velLongSmooth)) +
  geom_line(colour = "red") 

velVert <- ex %>% 
  ggplot(aes(x = t, y = velVertSmooth)) +
  geom_line(colour = "red") 

area / depth / velAbs / velLat / velLong / velVert / iff


#### read in all the data ####

data_files_controlled <- list.files(paste0(DATA_FOLDER, "data_contact-IFF"), "controlled", full.names = TRUE, recursive = TRUE)

data_files_expressions <- list.files(paste0(DATA_FOLDER, "data_contact-IFF"), full.names = TRUE, recursive = TRUE) %>% 
  setdiff(data_files_controlled)

stim_files_controlled <- list.files(paste0(DATA_FOLDER, "data_stimulus-logs"), "stimuli", full.names = TRUE, recursive = TRUE)

stimuli_controlled <- tibble()
for (stimfile in stim_files_controlled) {
  stimuli_controlled <- rbind(
    stimuli_controlled,
    read_csv(stimfile)
  )
}

stimlog_files_controlled <- list.files(paste0(DATA_FOLDER, "data_stimulus-logs"), "controlled.*log", full.names = TRUE, recursive = TRUE)

stimlogs_controlled <- tibble()
for (stimlogfile in stimlog_files_controlled) {
  str_extract(read_lines(stimlogfile, skip = 1), ",\\.+")
  log_contents <- tibble(
    time = str_extract(read_lines(stimlogfile, skip = 1), "[0-9]+\\.[0-9]+") %>% as.numeric()
  )
  
  stimlogs_controlled <- rbind(
    stimuli_controlled,
    #read_csv(stimlogfile)
  )
}

data_controlled <- tibble()
for (f in data_files_controlled) {
  
  fname <- basename(f)
  #session_date <- str_extract(fname, "[0-9]{4}-[0-9]{2}-[0-9]{2}")
  session_datetime <- str_extract(fname, "([0-9]|-|_){19}")
  stim_idx <- which(str_detect(stimuli_controlled$kinect_recording, session_datetime))
  stimuli_controlled[stim_idx,]
  
  data_controlled <- rbind(
    data_controlled,
    read_csv(f) %>% mutate(
      filename = fname
      )
    )
}
