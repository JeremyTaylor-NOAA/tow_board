#####################################################################
#####################################################################
##  File:   Dockerfile
##
##  Spec:   Dockerfile is used to create the ros-humble
##          docker image. This file gets the base image,
##          downloaded dependencies, and copys files into the 
##          image. This file also sets the entrypoint
##          and runs the startup.sh script at start up.
##
##  i/o:    None.
##
##  notes:  
##
##  Author: Aksel Sloan | aksel.sloan@noaa.gov
##
##
#####################################################################
#####################################################################

#FROM --platform=linux/arm64 osrf/ros:humble-desktop
FROM arm64v8/ros:humble-ros-base-jammy

# Set the ROS distribution
ARG ROS_DISTRO=humble

# Update and install packages
RUN echo "hello world"
RUN apt-get update

RUN apt-get update && \
    apt-get install -y \
    vim \
    python3-pip \
    usbutils \
    python3-smbus \
    libgl1-mesa-glx \ 
    python3-opencv \
    libopencv-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    
