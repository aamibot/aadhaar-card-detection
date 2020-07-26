import cfg
import sys
import onnx
import numpy as np
import cv2
import onnxruntime

from tool.utils import plot_boxes_cv2,post_processing,load_class_names

class Detector:

    def __init__(self,image_path,filename):

        self.session = onnxruntime.InferenceSession(cfg.MODEL_PATH)
        self.image_path = image_path
        self.filename = filename

    def detect(self):
        """Detect if image is Aadhaar and save image if detected"""

        print("The model expects input shape: ", self.session.get_inputs()[0].shape)

        image_src = cv2.imread(self.image_path)
        IN_IMAGE_H = self.session.get_inputs()[0].shape[2]
        IN_IMAGE_W = self.session.get_inputs()[0].shape[3]

        # Input
        resized = cv2.resize(image_src, (IN_IMAGE_W, IN_IMAGE_H), interpolation=cv2.INTER_LINEAR)
        img_in = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img_in = np.transpose(img_in, (2, 0, 1)).astype(np.float32)
        img_in = np.expand_dims(img_in, axis=0)
        img_in /= 255.0
        print("Shape of the network input after preprocessing: ", img_in.shape)

        # Compute
        input_name = self.session.get_inputs()[0].name

        outputs = self.session.run(None, {input_name: img_in})

        boxes = post_processing(img_in, 0.4, 0.6, outputs)

        if np.array(boxes).size:

            namesfile = 'data/obj.names'
            class_names = load_class_names(namesfile)
            plot_boxes_cv2(image_src, boxes[0], savename=self.filename, class_names=class_names) #Detect image and save image with bounding boxes if Aadhaar card detected
            return 1
            
        else:
            print('Uploaded Image is not Aadhaar')
            return 0