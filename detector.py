import cfg
import sys
import onnx
import numpy as np
import cv2
import onnxruntime
import logging
from tool.utils import plot_boxes_cv2,post_processing,load_class_names

#Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/detector.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

model = onnxruntime.InferenceSession(cfg.MODEL_PATH)
logger.info(f'Model loaded')

class Detector:

    def __init__(self,image_path,filename):

        self.image_path = image_path
        self.filename = filename

    def detect(self):
        """Detect if image is Aadhaar and save image if detected"""

        logger.info(f'The model expects input shape: {model.get_inputs()[0].shape}')

        image_src = cv2.imread(self.image_path)
        IN_IMAGE_H = model.get_inputs()[0].shape[2]
        IN_IMAGE_W = model.get_inputs()[0].shape[3]

        # Input
        resized = cv2.resize(image_src, (IN_IMAGE_W, IN_IMAGE_H), interpolation=cv2.INTER_LINEAR)
        img_in = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img_in = np.transpose(img_in, (2, 0, 1)).astype(np.float32)
        img_in = np.expand_dims(img_in, axis=0)
        img_in /= 255.0
        logger.info(f'Shape of the network input after preprocessing: {img_in.shape}')

        # Compute
        input_name = model.get_inputs()[0].name
        
        outputs = model.run(None, {input_name: img_in})
           
        boxes = post_processing(img_in, 0.4, 0.6, outputs)
        logger.info(f'Post Processing output : {boxes}')

        if np.array(boxes).size:

            namesfile = cfg.NAMESFILE
            class_names = load_class_names(namesfile)
            if plot_boxes_cv2(image_src, boxes[0], savename=self.filename, class_names=class_names): #Detect image and save image with bounding boxes if Aadhaar card detected
                return 1
            else:
                return 0
            
        else:
            logger.info('Uploaded Image is not Aadhaar')
            return 0
