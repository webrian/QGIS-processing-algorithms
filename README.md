# QGIS Processing Algorithms

A collection of [QGIS](https://github.com/qgis/QGIS) processing algorithms.

## Unzip Processing Algorithm

### Motivation

There is a handy processing algorithm to [download files](https://docs.qgis.org/testing/en/docs/user_manual/processing_algs/qgis/filetools.html#download-file) from an arbitrary URL. But as it seems geodata are often in compressed ZIP archives. In case of ZIP archives it is necessary to extract downloaded data to a destination folder for further processing.

### Installation

1. download the Python script
2. open Processing Toolbox in QGIS
3. select "Open Existing Script" in the Processing Toolbox menu
4. select the script UnzipArchiveProcessing.py
5. algorithm is added in section "Scripts"

![Screenshot from 2022-12-19 22-37-09](https://user-images.githubusercontent.com/980073/208528878-895b6463-af99-427a-b969-97c5de25d89e.png)

### Use in a Model

This algorithm is useful for use in a model after downloading data.

![model](https://user-images.githubusercontent.com/980073/208529120-9adf9aa2-0d84-4a47-a612-41a0d2bff8a0.png)

## FTP Upload Processing Algorithm

### Motivation

QGIS features already a [Download File](https://docs.qgis.org/testing/en/docs/user_manual/processing_algs/qgis/filetools.html#download-file) processing tool to download (geo-)data from a server. But there is a missing tool to upload files to a server.

### Installation

1. download the Python script
2. open Processing Toolbox in QGIS
3. select "Open Existing Script" in the Processing Toolbox menu
4. select the script FtpUploadProcessing.py
5. algorithm is added in section "Scripts"

![image](https://user-images.githubusercontent.com/980073/211674361-f41e64f4-4cba-4dc2-9d53-7554b6234b53.png)

### Use in a Model

![image](https://user-images.githubusercontent.com/980073/211674637-cb2f6c66-8b7b-461a-972a-10b56bac7b29.png)

## Transformation Processing Algorithms

### Motivation

~~While [QGIS](https://github.com/qgis/QGIS) features an user-friendly and sophisticated [georeferencer](https://docs.qgis.org/testing/en/docs/user_manual/working_with_raster/georeferencer.html) for raster files with different transformation options, it lacks a similar tool for vector layers.~~ QGIS features a native vector georeferencer since version 3.26. The GDAL/OGR library provides the gcp options to georeference vector layers with polynominal transformations.
But there is still an option missing to reference data with a 4-parameter Helmert transformation with estimated parameters using the least square fitting. This QGIS processing script should fill this gap.

### Installation

1. download the Python script
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
