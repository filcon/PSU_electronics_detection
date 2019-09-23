# PSU Electronics Detection

#### 1. Objective
#### 2. Motivation
#### 3. Procedure
#### 4. Results

## 1. Objective
Detection and identification of electronic components in Power Supply Units (PSUs) for PCs.
The result at a first stage should provide identification of major components as illustrated in the image bellow:

![PSU_components_detection_smaller](https://user-images.githubusercontent.com/47978862/65394548-d9769580-dd8f-11e9-960d-e4d4d84326c9.png)
##### PSU: Corsair SF600 Platinum / Photo source: [jonnyGURU.com](https://www.jonnyguru.com/)

Detection of defects will be addressed later.

## 2. Motivation
My passion for PC hardware and deep learning and the desire to combine both to build a computer vision project.

PSUs were chosen because they are common, their core components are well known and there are a considerable number of reviews that provide a great number of quality photos and information on their electronics. This makes them a good source of information to build a labeled dataset for electronics, to compensate the lack of open source options.

In addition, not much projects/works on object detection for electronics are available, so I hope to contribute a little to the field.

### Side note:
A PSU is a very important component in a PC, besides its main task to convert AC current do DC current, if of good quality it helps in the PC performance, provides current protection and prolongs the life of all other PC components.

## 3. Procedure
The project is still on its first steps and I hope do develop it further with more advanced implementations and detailed descriptions. 
For the moment, a YOLOv3 framework was used for the detection with a bit of OpenCV help, following a simple tutorial, [Snowman by LearnOpenCV](https://www.learnopencv.com/training-yolov3-deep-learning-based-custom-object-detector/).

### 3.1. Image Processing
#### 3.1.1.1. Data Collection
Up to the moment around 300 PSU internal images were collected but more will be collected soon. The objective is to collect around 1000 relevant images.

All images were collected from [jonnyGURU.com](https://www.jonnyguru.com/). It’s a technology website that makes excellent and detailed reviews on PSUs and has very good quality images that perfectly fit the project needs.

I thank Jon Gerow for authorizing the image collection and their usage on this project.

#### 3.1.2. Data Annotation
Data annotation takes a long time, so only around 230 images were annotated at the moment and just for the coils.
This was performed with **LabelImage**. Instructions for download, install and use can be found [here](https://github.com/tzutalin/labelImg).

Labels were saved in YOLO format.

#### 3.1.3. Train-Test Data Split
First images were put in a folder called **images** and the labels in a folder called **labels**.

For train test data split the code was adapted from the tutorial and two arguments are included. -p for the percentage of test data and -f to pass the folder were were the images are stored. For the first test I used 90% Train and 10% Test, but 80-20 and 70-30 are usually more common. Example of script:

```python
python split_train_test.py -f 30 -p /full/path/to/project/images/
```
This means 30% of test and 70% of train. Two files, data_train.txt and data_test.txt, are generated with the list of selected images for each split.


### 3.2 Model
#### 3.2.1. YOLOv3 configuration

To use YOLOv3 I downloaded and built [Darknet](https://github.com/pjreddie/darknet):
```python
cd ~
git clone https://github.com/pjreddie/darknet
cd darknet
make
```
Modifications were made on how to store intermediate weights while training. This is usefull to evaluate how well the model is learning, for early stopping, and in case there is the need to stop and resume training later. 
In the file examples/detector.c, line #138 was changed from:

```
if(i%10000==0 || (i < 1000 && i%100 == 0)){
```
to
```
if(i%1000==0 || (i < 2000 && i%200 == 0)){
```
The original code saves the weights after every 100 iterations until the first 1000 and then after every 10000 iterations. In my case, since for now I'm only training one class much less iterations are required. The new code saves the weights after every 200 iterations until the first 2000 and then after every 1000 iterations.

After the changes, darknet has to be recompiled again by running **make**.

If a GPU with CUDA is available it will be extremely usefull to speed up the training. Make sure the latest drivers and CUDA are installed. To make use of the GPU the **Makefile** of darknet was changed from:
```
GPU = 0 
```
to
```
GPU = 1 
```
Save and recompile again by running **make**. Other options can be used with GPUs but more configurations are required.
In the project a Nidia GTX 1050 Ti was used.

Network configuration files with the models architecture and hyperparameters can be found on the **cfg folder**, inside darknet.
The used **cfg** file **yolov3.cfg**, which is provided in this repository, is an adaptation of the **yolov3-voc.cfg**.

#### 3.2.2. Transfer learning
Due to the low number of images it is almost compulsory to use pre-trained network weights to take advantage of transfer learning. YOLOv3 weights trained on ImageNet were downloaded and saved to the darknet folder:
```python
cd ~/darknet
wget https://pjreddie.com/media/files/darknet53.conv.74 -O ~/darknet/darknet53.conv.74
```
Other configuration files and weights can be found and downloaded from the [YOLO site](https://pjreddie.com/darknet/yolo/).

Several options for weights use on the network can be attempted. Two were tested at the moment:

* **Option A:** Use pre-trained weights as starting point for all layers and train new weights just from the last convolutional layer onward. Before this point all weights remain unchanged.

To accomplish this the following line of code was included on the **cfg** file, before the last layer I wanted to train:
```
stopbackward=1
```
Only the weights of the layers after this line will be updated during backpropagation.

* **Option B:**  Use pre-trained weights for initialization and train the entire network.

No changes are required for **Option B**.

#### 3.2.3. Data files
In the **darknet.data** file it is necessary to provide the number of classes and the full paths to some relevant files and folders:
```
classes = 1
train  = /path/to/project/folder/snowman_train.txt
valid  = /path/to/project/folder/snowman_test.txt
names = /path/to/project/folder/classes.names
backup = /path/to/project/folder/weights/
```
The **classes.names** file also needs to be updated with the classes being detected. In my case only 1 class, **coil**, is being detected:
```
coil
```
More classes will be added soon.

#### 3.2.4. Training
Due to GPU memory limitations, the number of subdivisions on the **cfg** file was increased to 64 to avoid memory errors, while maintaining the batch size of 64. If a more powerfull GPU was available smaller subdivisions could be attempted, e.g. 1, 2, 4, 8, 16 or 32. For more details on selecting batch and sudbdivisoon, and other hyperparameters, check the [tutorial](https://www.learnopencv.com/training-yolov3-deep-learning-based-custom-object-detector/).

To start training and generate a log file the following script was used:
```python
cd darknet
./darknet detector train /path/to/project/folder/darknet.data /path/to/project/folder/yolov3.cfg ./darknet53.conv.74 > /path/to/project/folder/train.log
```
To generate a plot of the loss:
```python
python plotTrainLoss.py /path/to/project/folder/train.log
```
## 4. Results
While training both transfer learning options, **A** and **B**, were tested.

**Option A** was not doing a good job in reducing the loss and after 200 iterations the loss was higher than desired.

Stopbackward could have been placed in a different position, e.g. in the middle of the network, so that more layers could have been updated, but training was stopped and the configuration switched to **Option B**. After 200 iterations the loss was already much lower and after 800 iterations the model was already successful in the detection of coils.

An example can be seen in the test image below.

![DSC_1598_coils](https://user-images.githubusercontent.com/47978862/65394656-e34cc880-dd90-11e9-91e9-303f94a4d3a3.jpg)
##### PSU: Corsair TX750M (2017) / Photo source: [jonnyGURU.com](https://www.jonnyguru.com/)

To test the model two paths need to be updated in the file **object_detection_yolo.py**:
```python
modelConfiguration = "/full/path/to/project/darknet-yolov3.cfg";
modelWeights = "/full/path/to/project/weights/darknet-yolov3_final.weights";
```
Then run the script with the selected image:
```
python object_detection_yolo.py --image=file_name.jpg
```

Further improvement of the model will continue, and the next steps will be the addition of more pictures and classes.

Full results with metrics will be presented.
