%Function test(net,testdata) for testing
function accuracy=test(net,imdsTest)
    %get network input size
    inputSize = net.Layers(1).InputSize; 
    
    %risize  test data to fit network input size
    augimdstest = augmentedImageDatastore(inputSize(1:2),imdsTest);
    
    %classification
    [YPred,scores] = classify(net, augimdstest );
    YTest = imdsTest.Labels;
    
    %calculate accuracy
    accuracy = mean(YPred == YTest);
end