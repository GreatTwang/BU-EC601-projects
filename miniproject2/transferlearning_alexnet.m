%Load image data
imds = imageDatastore('Datasets\', ...
    'IncludeSubfolders',true,'LabelSource','foldernames');

%dataset=>train, validation, test  7:2:1
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomize');
[imdsValidation,imdsTest]=splitEachLabel(imdsValidation,0.66,'randomize');

%Load Pretrained Network
net = alexnet         %need Matlab related addons
%Get inputSize of Pretrained Network
inputSize = net.Layers(1).InputSize

%To retrain AlexNet to classify new dataset, replace the last three layers of the network.
layersTransfer = net.Layers(1:end-3);
numClasses = numel(categories(imdsTrain.Labels));
layers = [
    layersTransfer
    fullyConnectedLayer(numClasses,'WeightLearnRateFactor',10,'BiasLearnRateFactor',10)
    softmaxLayer
    classificationLayer];

%Risize input data
pixelRange = [-30 30];
imageAugmenter = imageDataAugmenter( ...
    'RandXReflection',true, ...
    'RandXTranslation',pixelRange, ...
    'RandYTranslation',pixelRange);
augimdsTrain = augmentedImageDatastore(inputSize(1:2),imdsTrain, ...
    'DataAugmentation',imageAugmenter);
augimdsValidation = augmentedImageDatastore(inputSize(1:2),imdsTrain);

%Specify the training options
options = trainingOptions('sgdm', ...
    'MiniBatchSize',10, ...
    'MaxEpochs',6, ...
    'InitialLearnRate',1e-4, ...
    'Shuffle','every-epoch', ...
    'ValidationData',augimdsValidation, ...
    'ValidationFrequency',30, ...
    'Verbose',false, ...
    'Plots','training-progress');

%training the transferred network
nettransfer = trainNetwork(augimdsTrain,layers,options);