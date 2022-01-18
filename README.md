# QGIS Transformation Processing Algorithms

## Motivation

While [QGIS](https://github.com/qgis/QGIS) features an user-friendly and sophisticated [georeferencer](https://docs.qgis.org/testing/en/docs/user_manual/working_with_raster/georeferencer.html) for raster files with different transformation options, it lacks a similar tool for vector layers. The GDAL/OGR library provides the gcp options to georeference vector layers with polynominal transformations.
But there is still an option missing to reference data with a 4-parameter Helmert transformation with estimated parameters using the least square fitting. This QGIS processing script should fill this gap.

## Installation

1. download the Python scripts
2. open Processing Toolbox in QGIS
3. select "Open Existing Script" in the Processing Toolbox menu
4. algorithms are added in section "Scripts"

![image](https://user-images.githubusercontent.com/980073/149583386-1d92fc6a-0519-4b1a-b638-56257521124c.png)

## How to use the processing script