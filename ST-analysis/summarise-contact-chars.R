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

#read in the data 
ex <- read_csv(paste0(CONTACT_DATA_FOLDER, "2022-06-17/unit5/2022-06-17_18-15-56_controlled-touch-MNG_ST16_5_block1.csv"))

plot_session <- function(df) {
  
  feature_plot <- function(df, feature, y_axis_label) {
    df %>% 
      mutate(trial_id = as.character(trial_id)) %>%   
      ggplot(aes(x = t, y = .data[[feature]], colour = trial_id)) +
      geom_point(size = 0.2) +
      labs(y = y_axis_label) +
      theme(axis.title.x=element_blank(),
            axis.text.x=element_blank(),
            axis.ticks.x=element_blank())
  }
  
  area <- feature_plot(df, "areaSmooth", expression("Contact cm"^2))
  depth <- feature_plot(df, "depthSmooth", "Depth cm")
  velAbs <- feature_plot(df, "velAbsSmooth", "AbsV cm/s")
  velLat <- feature_plot(df, "velLatSmooth", "LatV cm/s")
  velLong <- feature_plot(df, "velLongSmooth", "LongV cm/s")
  velVert <- feature_plot(df, "velVertSmooth", "VertV cm/s")
 
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

plot_session(ex)


#### read in all the data ####

data_files_controlled <- list.files(CONTACT_DATA_FOLDER, "controlled", full.names = TRUE, recursive = TRUE)

data_files_expressions <- list.files(CONTACT_DATA_FOLDER, full.names = TRUE, recursive = TRUE) %>% 
  setdiff(data_files_controlled)

stim_files_controlled <- list.files(STIM_INFO_FOLDER, "stimuli", full.names = TRUE, recursive = TRUE)

stimuli_controlled <- tibble()
for (stimfile in stim_files_controlled) {
  stimuli_controlled <- rbind(
    stimuli_controlled,
    read_csv(stimfile)
  )
}

data_controlled <- tibble()
for (f in data_files_controlled) {
  
  fname <- basename(f)
  session_datetime <- str_extract(fname, "([0-9]|-|_){19}")
  stim_idx <- which(str_detect(stimuli_controlled$kinect_recording, session_datetime))
  session_stim <- stimuli_controlled[stim_idx,]
  session_data <- read_csv(f)
  trial_ids <- na.omit(unique(session_data$trial_id))
  
  if (nrow(session_stim) == length(trial_ids)) {
    session_data <- session_data %>% 
      mutate(trial = NA_integer_) 
    for (trial_n in seq_along(trial_ids)) {
      session_data$trial[session_data$trial_id == trial_ids[trial_n]] <- session_stim$trial[trial_n]
    }
    session_data <- full_join(session_data, session_stim)
  } else {
    warning("number of stimuli does not match")
  }
  
  data_controlled <- rbind(
    data_controlled,
    session_data %>% mutate(
      filename = fname,
      kinect_recording = basename(str_replace_all(kinect_recording, "\\\\", "/")),
      unit = str_extract(fname, "ST[0-9]+_[0-9]+")
      )
    )
}

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

