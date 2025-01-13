import os
import csv
import java.awt.Color as Color
from ij import WindowManager as WindowManager
from ij import WindowManager, IJ
from ij.plugin.frame import RoiManager as RoiManager
from ij.process import ImageStatistics as ImageStatistics
from ij.measure import Measurements as Measurements
from ij import IJ as IJ
from ij.measure import CurveFitter as CurveFitter
from ij.gui import Plot as Plot
from ij.gui import PlotWindow as PlotWindow
import math


# Get the active image
current_imp = WindowManager.getCurrentImage()
title = current_imp.getTitle()

# Extract the folder address from the filename
folder_address = IJ.getDirectory("image")

# Specify the filename for the CSV file
csv_filename = os.path.join(folder_address, "FRAP_data_all_rois_" + os.path.splitext(title)[0] + ".csv")
 
# Get ROIs
roi_manager = RoiManager.getInstance()
roi_list    = roi_manager.getRoisAsArray()
 
# Specify up to what frame to fit and plot.
n_slices = 610  # Number of frames to consider
nR=6
frames_to_include = 100  # Number of frames to include
frames_before_bleach = 5  # Number of frames before the bleach frame



# Open the CSV file in 'append' mode
with open(csv_filename, "a") as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Loop through each ROI
    for k in range(0, nR-2): 
        # We assume first one is FRAP roi, the 2nd one is normalizing roi.
        roi_FRAP    = roi_list[k];
        roi_norm    = roi_list[nR-2];

        # Create empty lists for X and Y values
        x_values = []
        y_values = []
         
        # Get current image plus and image processor
        current_imp  = WindowManager.getCurrentImage()
        stack        = current_imp.getImageStack()
        calibration  = current_imp.getCalibration()

        # Find minimal intensity value in FRAP and bleach frame
        min_intensity = None
        bleach_frame = None
        for i in range(0, n_slices):
            ip = stack.getProcessor(i+1)
            ip.setRoi(roi_FRAP)
            stats = ImageStatistics.getStatistics(ip, Measurements.MEAN, calibration)
            mean = stats.mean
            if min_intensity is None or mean < min_intensity:
                min_intensity = mean
                bleach_frame = i
        
        # Loop over frames to collect intensity values
        for i in range(bleach_frame - frames_before_bleach, bleach_frame - frames_before_bleach + frames_to_include):
            if i < 0 or i >= n_slices:
                continue  # Skip frames outside the valid range
            
            # Get the current slice 
            ip = stack.getProcessor(i+1)

            # Put the ROI on it
            ip.setRoi(roi_FRAP)

            # Make a measurement in it
            stats = ImageStatistics.getStatistics(ip, Measurements.MEAN, calibration);
            mean  = stats.mean

            # Store the measurement in the list
            x_values.append(i * calibration.frameInterval)
            y_values.append(mean)

        # Write X and Y values to the CSV file for the current ROI
        csvwriter.writerow(["ROI" + str(k+1)] + x_values)
        csvwriter.writerow(["", ""] + y_values)
