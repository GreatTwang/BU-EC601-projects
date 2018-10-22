%Load image data
imds = imageDatastore('Datasets\', ...
    'IncludeSubfolders',true,'LabelSource','foldernames');

%dataset=>train, validation, test  7:2:1
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomize');
[imdsValidation,imdsTest]=splitEachLabel(imdsValidation,0.66,'randomize');

% Create image input layer.
inputLayer = imageInputLayer([200 200 3]);

% Create the middle layers.
middleLayers = [
    convolution2dLayer(3,8,'Padding','same')
    batchNormalizationLayer
    reluLayer
    
    averagePooling2dLayer(2,'Stride',2)

    convolution2dLayer(3,16,'Padding','same')
    batchNormalizationLayer
    reluLayer
    
    averagePooling2dLayer(2,'Stride',2)
  
    convolution2dLayer(3,32,'Padding','same')
    batchNormalizationLayer
    reluLayer
    
    convolution2dLayer(3,32,'Padding','same')
    batchNormalizationLayer
    reluLayer
    
    dropoutLayer(0.2)
    ];
% Create the final layers.
finalLayers = [
    % Add the last fully connected layer
    fullyConnectedLayer(2)
    % Add the softmax loss layer and classification layer.
    softmaxLayer
    classificationLayer
    ];

%all the layers
layers = [
    inputLayer
    middleLayers
    finalLayers
    ]

%Risize input data
pixelRange = [-30 30];
imageAugmenter = imageDataAugmenter( ...
    'RandXReflection',true, ...
    'RandXTranslation',pixelRange, ...
    'RandYTranslation',pixelRange);
augimdsTrain = augmentedImageDatastore([200 200],imdsTrain, ...
    'DataAugmentation',imageAugmenter);
augimdsValidation = augmentedImageDatastore([200 200],imdsTrain);

%Specify the training options
options = trainingOptions('adam', ...
    'MiniBatchSize',20, ...
    'MaxEpochs',50, ...
    'InitialLearnRate',1e-4, ...
    'Shuffle','every-epoch', ...
    'ValidationData',augimdsValidation, ...
    'ValidationFrequency',30, ...
    'Verbose',false, ...
    'Plots','training-progress');

%training the transferred network
convnet = trainNetwork(augimdsTrain,layers,options);