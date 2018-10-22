clear
clc
%load data
imds = imageDatastore('Datasets\', ...
    'IncludeSubfolders',true,'LabelSource','foldernames');

% dataset=>Train, Validation, Test
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomize');
[imdsValidation,imdsTest]=splitEachLabel(imdsValidation,0.66,'randomize');

%training example: training using transfer learning with pretrained Alexnet
%transferlearning_alexnet       %you can remove % if you want to train models

%training example: training a simple CNN designed by myself
%simplecnn                 %you can remove % if you want to train models

%Function test(net,testdata) for testing
%testing example : transfer learning with Alexnet
load('alexnet_transfer.mat','nettransfer');    % model saved in alexnet_transfer.mat
accuracy_alex=test(nettransfer,imdsTest);
accuracy_alex

%testing example : simple CNN designed by myself
load('simplecnn.mat','convnet');    % model saved in simplecnn.mat
accuracy_simplecnn=test(convnet,imdsTest);
accuracy_simplecnn





