# Aadhaar Card Detection
This is an application to detect aadhaar card in an image.

### Breif Overview
Approximately 10 different aadhaar card images were augmented to ~100 different images to train a cutom object detection model using YOLOv4(Darknet).Then the model was converted to onnx and inference was made with onnxruntime.The application is served using the flask web framework.

### Try it out
Go to : https://detect-aadhaar.herokuapp.com/ or  
        https://detect-aadhaar-2.herokuapp.com/
  

### References
* https://github.com/Tianxiaomo/pytorch-YOLOv4
* https://github.com/DataActivator/ObjectDetection_FlaskDeployment
