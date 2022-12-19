# QGIS Processing Algorithms

A collection of [QGIS](https://github.com/qgis/QGIS) processing algorithms.

## Unzip Processing Algorithm

## Transformation Processing Algorithms

### Motivation

While [QGIS](https://github.com/qgis/QGIS) features an user-friendly and sophisticated [georeferencer](https://docs.qgis.org/testing/en/docs/user_manual/working_with_raster/georeferencer.html) for raster files with different transformation options, it lacks a similar tool for vector layers. The GDAL/OGR library provides the gcp options to georeference vector layers with polynominal transformations.
But there is still an option missing to reference data with a 4-parameter Helmert transformation with estimated parameters using the least square fitting. This QGIS processing script should fill this gap.

### Installation

1. download the Python scripts
2. open Processing Toolbox in QGIS
3. select "Open Existing Script" in the Processing Toolbox menu
4. select the scripts HelmertTransformationProcessing.py and/or PolynominalTransformationProcessing.py
5. algorithms are added in section "Scripts"

<img src="https://user-images.githubusercontent.com/980073/149583386-1d92fc6a-0519-4b1a-b638-56257521124c.png">

### How to use the processing script

1. load the unreferenced vector layer

<img src="https://user-images.githubusercontent.com/980073/158578743-8cf1b89f-7a79-4d59-ba00-49386393adc4.png" width="450">

2. create a new linestring layer (temporary scratch layer is sufficient)
3. determine control points and add one linestring (with start and end point) for each control point from the unreferenced layer to the georeferenced layer

![Screenshot from 2022-03-16 12-24-04](https://user-images.githubusercontent.com/980073/158579553-2e25ff48-9985-4b63-bc06-c5ba18161831.png)
![Screenshot from 2022-03-16 12-24-31](https://user-images.githubusercontent.com/980073/158579562-97a4673d-7730-43b8-bac7-598dc922e7d6.png)

4. run the processing algorithm

<img src="https://user-images.githubusercontent.com/980073/158580617-9343a9f0-bf4e-48f5-87d1-e178e627f0b0.png" width="600">

5. check the transformation

![Screenshot from 2022-03-16 12-32-04](https://user-images.githubusercontent.com/980073/158580843-f9059bff-9949-477e-9e40-cd4fb150fb81.png)
