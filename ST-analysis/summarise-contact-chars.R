#### libraries ####
library(readr)
library(dplyr)
library(stringr)
library(ggplot2)
library(patchwork)
library(Hmisc)

#### data folders ####
DATA_FOLDER <- "~/Library/CloudStorage/OneDrive-Linköpingsuniversitet/projects - in progress/touch comm MNG Kinect/"
CONTACT_DATA_FOLDER <- paste0(DATA_FOLDER, "data_contact-IFF-trial/")
STIM_INFO_FOLDER <- paste0(DATA_FOLDER, "data_stimulus-logs/")

# notes from Shan about the data:
# the csv file contains the contact features as 
# raw data (named as xxRaw), interpolated data (named as xx), smoothed data (named as xxSmooth), 
# 1st derivative (named as xx1D), and 2nd derivative (named as xx2D). 
# The contact data were upsampled and the neural data were downsampled to both 1000Hz.
# the units for first and second derivatives are 
# cm/s2 for velocity1D, cm/s for depth1D, and cm2/s for area1D 
# I  kept the data of the whole trial regardless of having neural data or not. 
# The end of each trial might not be covered by the trial number since the contact sometimes stopped 
# after the LED went off.

#### plot appearance ####
theme_set(theme_bw(base_size = 14))

#### plot a single session ####

ex <- read_csv(paste0(CONTACT_DATA_FOLDER, "2022-06-17/unit5/2022-06-17_18-15-56_controlled-touch-MNG_ST16_5_block1.csv"))

feature_plot <- function(df, feature, y_axis_label, trial) {
  df %>% 
    ggplot(aes(x = t, y = .data[[feature]], colour = as.character(.data[[trial]]))) +
    geom_point(size = 0.2) +
    labs(y = y_axis_label) 
}

plot_raw_session <- function(df) {
  
  theme_no_x <- theme(
    axis.title.x=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank())
  
  area <- feature_plot(df, "areaSmooth", expression("Contact cm"^2), "trial_id") + theme_no_x
  depth <- feature_plot(df, "depthSmooth", "Depth cm", "trial_id") + theme_no_x
  velAbs <- feature_plot(df, "velAbsSmooth", "AbsV cm/s", "trial_id") + theme_no_x
  velLat <- feature_plot(df, "velLatSmooth", "LatV cm/s", "trial_id") + theme_no_x
  velLong <- feature_plot(df, "velLongSmooth", "LongV cm/s", "trial_id") + theme_no_x
  velVert <- feature_plot(df, "velVertSmooth", "VertV cm/s", "trial_id") + theme_no_x
  
  iff <- df %>% 
    mutate(
      spike_label = if_else(spike == 1, "|", ""),
      trial_id = as.character(trial_id)
    ) %>% 
    ggplot(aes(x = t, y = IFF, colour = trial_id)) +
    geom_line(linewidth = 0.2) +
    geom_text(aes(y = -max(IFF)/5, label = spike_label), alpha = 0.5, size = 8) +
    labs(y = "IFF Hz", x = "Seconds") +
    theme(legend.position = "none")
  
  area / depth / velAbs / velLat / velLong / velVert / iff + 
    plot_layout(guides = 'collect') 
}

plot_raw_session(ex)


#### read in semi-controlled data ####

data_files_controlled <- list.files(CONTACT_DATA_FOLDER, "controlled", full.names = TRUE, recursive = TRUE)

stim_files_controlled <- list.files(STIM_INFO_FOLDER, "stimuli", full.names = TRUE, recursive = TRUE)

merge_session_data_w_stiminfo <- function(data_file_list, stim_file_list) {
  
  # read in the stim files
  read_all_stim_files <- function(file_list) {
    stim_file_contents <- tibble()
    for (stimfile in stim_files_controlled) {
      stim_file_contents <- rbind(
        stim_file_contents,
        read_csv(stimfile, show_col_types = FALSE)
      )
    }
    stim_file_contents %>% 
      mutate(kinect_recording = basename(str_replace_all(kinect_recording, "\\\\", "/")) )
  }
  
  stimuli_controlled <- read_all_stim_files(stim_file_list)
  
  # rad in the data files and match with stim files
  data_controlled <- tibble()
  for (f in data_files_controlled) {
    print(f)
    fname <- basename(f)
    
    # match based on date/time stamp to find stim info for this session
    session_datetime <- str_extract(fname, "([0-9]|-|_){19}")
    stim_idx <- which(str_detect(stimuli_controlled$kinect_recording, session_datetime))
    session_stim <- stimuli_controlled[stim_idx,]
    
    # read data
    session_data <- read_csv(f, show_col_types = FALSE) 
    
    # get the trial_ids based on the LED visible on the camera
    trial_ids <- na.omit(unique(session_data$trial_id))
    
    # check if the stim file has the same number of trials
    if (nrow(session_stim) == length(trial_ids)) {
      
      # create the trial variable in the session data file to later merge with the stim info
      session_data <- session_data %>% 
        mutate(trial = NA_integer_) 
      
      # fill the new trial variable with labels from the session stim info
      for (trial_n in seq_along(trial_ids)) {
        session_data$trial[session_data$trial_id == trial_ids[trial_n]] <- session_stim$trial[trial_n]
      }
      # merge session data with stim info
      session_data <- full_join(session_data, session_stim, by = "trial") %>% 
        #  add filename metadata and unique stim description to new variables 
        mutate(
        filename = fname,
        unit = str_extract(fname, "ST[0-9]+_[0-9]+"),
        stim_desc = if_else( is.na(trial_id), NA_character_,
          paste0(
          trial_id, ".",
          " ", type, 
          " speed", speed, 
          " ", str_extract(contact_area, "(finger)|(hand)"),
          " ", force )
      ))
      
    } else {
      warning("number of stimuli does not match")
      print("number of stimuli does not match")
    }
    
    # update to all data 
    data_controlled <- rbind(data_controlled, session_data )
  }
  data_controlled
}

data_controlled <- merge_session_data_w_stiminfo(data_files_controlled, stim_files_controlled)

#### plot semi-controlled data ####

plot_session <- function(df, title = "") {
  
  theme_no_x <- theme(
    axis.title.x=element_blank(),
    axis.text.x=element_blank(),
    axis.ticks.x=element_blank())
  
  area <- feature_plot(df, "areaSmooth", expression("Contact cm"^2), "stim_desc") + theme_no_x
  depth <- feature_plot(df, "depthSmooth", "Depth cm", "stim_desc") + theme_no_x
  velAbs <- feature_plot(df, "velAbsSmooth", "AbsV cm/s", "stim_desc") + theme_no_x
  velLat <- feature_plot(df, "velLatSmooth", "LatV cm/s", "stim_desc") + theme_no_x
  velLong <- feature_plot(df, "velLongSmooth", "LongV cm/s", "stim_desc") + theme_no_x
  velVert <- feature_plot(df, "velVertSmooth", "VertV cm/s", "stim_desc") + theme_no_x
  
  iff <- df %>% 
    mutate(
      spike_label = if_else(spike == 1, "|", ""),
      trial_id = as.character(trial_id)
    ) %>% 
    ggplot(aes(x = t, y = IFF, colour = trial_id)) +
    geom_line(linewidth = 0.2) +
    geom_text(aes(y = -max(IFF)/5, label = spike_label), alpha = 0.5, size = 8) +
    labs(y = "IFF Hz", x = "Seconds") +
    theme(legend.position = "none")
  
  area / depth / velAbs / velLat / velLong / velVert / iff + 
    plot_layout(guides = 'collect') + 
    #theme(legend.position = "bottom") +
    plot_annotation(title = title)
}

data_controlled %>% 
  filter(filename == data_controlled$filename[1]) %>%
  plot_session(title = data_controlled$filename[1])

# area
area <- data_controlled %>% 
  filter(areaSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = as.factor(speed), y = areaSmooth, colour = force)) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Contact area", 
       x = "Velocity instruction (cm/s)", 
       y = expression("Contact area (cm"^2*")"),
       colour = " Intensity instruction")

data_controlled %>% 
  filter(areaSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = contact_area, y = areaSmooth)) +
  facet_wrap(. ~ type) +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) #+
  labs(title = "Contact area", 
       x = "Velocity instruction (cm/s)", 
       y = expression("Contact area (cm"^2*")"),
       colour = " Intensity instruction")


# depth
depth <- data_controlled %>% 
  filter(depthSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = as.factor(speed), y = depthSmooth, colour = force)) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Intensity", 
       x = "Velocity instruction (cm/s)", 
       y = "Depth (cm)",
       colour = " Intensity instruction")

# velAbs
velAbs <- data_controlled %>% 
  filter(velAbsSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = force, y = velAbsSmooth, colour = as.factor(speed))) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Absolute velocity", 
       colour = "Velocity instruction (cm/s)", 
       y = "Velocity (cm/s)",
       x = " Intensity instruction")

# velLat
velLat <- data_controlled %>% 
  filter(velLatSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = force, y = velLatSmooth, colour = as.factor(speed))) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Lateral velocity", 
       colour = "Velocity instruction (cm/s)", 
       y = "Lateral velocity (cm/s)",
       x = " Intensity instruction")

# velLong
velLong <- data_controlled %>% 
  filter(velLongSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = force, y = velLongSmooth, colour = as.factor(speed))) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Longitudinal velocity", 
       colour = "Velocity instruction (cm/s)", 
       y = "Longitudinal velocity (cm/s)",
       x = " Intensity instruction")

# velVert
velVert <- data_controlled %>% 
  filter(velVertSmooth > 0 & !is.na(trial)) %>% 
  ggplot(aes(x = force, y = velVertSmooth, colour = as.factor(speed))) +
  facet_wrap(type ~ contact_area, scales = "free") +
  geom_boxplot(outlier.shape = 21, outlier.alpha = 0.2, coef = 3) +
  labs(title = "Vertical velocity", 
       colour = "Velocity instruction (cm/s)", 
       y = "Vertical velocity (cm/s)",
       x = " Intensity instruction")

#### read in expressions data ####
data_files_expressions <- list.files(CONTACT_DATA_FOLDER, full.names = TRUE, recursive = TRUE) %>%
  setdiff(data_files_controlled)
