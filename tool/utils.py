import cfg
import os
import math
import numpy as np
import cv2
import logging

# Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/utils.log")
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def nms_cpu(boxes, confs, nms_thresh=0.5, min_mode=False):

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = confs.argsort()[::-1]

    keep = []
    while order.size > 0:
        idx_self = order[0]
        idx_other = order[1:]

        keep.append(idx_self)

        xx1 = np.maximum(x1[idx_self], x1[idx_other])
        yy1 = np.maximum(y1[idx_self], y1[idx_other])
        xx2 = np.minimum(x2[idx_self], x2[idx_other])
        yy2 = np.minimum(y2[idx_self], y2[idx_other])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h

        if min_mode:
            over = inter / np.minimum(areas[order[0]], areas[order[1:]])
        else:
            over = inter / (areas[order[0]] + areas[order[1:]] - inter)

        inds = np.where(over <= nms_thresh)[0]
        order = order[inds + 1]

    return np.array(keep)


def get_color(c, x, max_val, colors):
    ratio = float(x) / max_val * 5
    i = int(math.floor(ratio))
    j = int(math.ceil(ratio))
    ratio = ratio - i
    r = (1 - ratio) * colors[i][c] + ratio * colors[j][c]
    return int(r * 255)


def plot_boxes_cv2(img, boxes, savename=None, class_names=None, color=None):
    img = np.copy(img)
    colors = np.array(
        [[1, 0, 1], [0, 0, 1], [0, 1, 1], [0, 1, 0], [1, 1, 0], [1, 0, 0]],
        dtype=np.float32,
    )
    confidence = 0
    width = img.shape[1]
    height = img.shape[0]
    for i in range(len(boxes)):
        box = boxes[i]

        if (box[5] * 100) < 98.0:
            logger.info("Detection confidence less than 98%, image is not Aadhaar")
            return 0
        else:
            confidence = 1
            x1 = int(box[0] * width)
            y1 = int(box[1] * height)
            x2 = int(box[2] * width)
            y2 = int(box[3] * height)

            if color:
                rgb = color
            else:
                rgb = (255, 0, 0)
            if len(box) >= 7 and class_names:
                cls_conf = box[5]
                cls_id = box[6]
                logger.info(f"{class_names[cls_id]}, {cls_conf}")
                classes = len(class_names)
                offset = cls_id * 123457 % classes
                red = get_color(2, offset, classes, colors)
                green = get_color(1, offset, classes, colors)
                blue = get_color(0, offset, classes, colors)
                if color is None:
                    rgb = (red, green, blue)
                img = cv2.putText(
                    img,
                    class_names[cls_id],
                    (x1, y1),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    rgb,
                    1,
                )
            img = cv2.rectangle(img, (x1, y1), (x2, y2), rgb, 1)

    if savename and confidence:
        cv2.imwrite(os.path.join(cfg.DETECTION_FOLDER, savename), img)
        logger.info(
            f"Plot results saved to : {os.path.join(cfg.DETECTION_FOLDER,savename)}"
        )
        return 1


def load_class_names(namesfile):
    class_names = []
    with open(namesfile, "r") as fp:
        lines = fp.readlines()
    for line in lines:
        line = line.rstrip()
        class_names.append(line)
    return class_names


def post_processing(img, conf_thresh, nms_thresh, output):

    # anchors = [12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401]
    # num_anchors = 9
    # anchor_masks = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    # strides = [8, 16, 32]
    # anchor_step = len(anchors) // num_anchors

    # [batch, num, 1, 4]
    box_array = output[0]
    # [batch, num, num_classes]
    confs = output[1]

    if type(box_array).__name__ != "ndarray":
        box_array = box_array.cpu().detach().numpy()
        confs = confs.cpu().detach().numpy()

    # [batch, num, 4]
    box_array = box_array[:, :, 0]

    # [batch, num, num_classes] --> [batch, num]
    max_conf = np.max(confs, axis=2)
    max_id = np.argmax(confs, axis=2)

    bboxes_batch = []
    for i in range(box_array.shape[0]):

        argwhere = max_conf[i] > conf_thresh
        l_box_array = box_array[i, argwhere, :]
        l_max_conf = max_conf[i, argwhere]
        l_max_id = max_id[i, argwhere]

        keep = nms_cpu(l_box_array, l_max_conf, nms_thresh)

        bboxes = []
        if keep.size > 0:
            l_box_array = l_box_array[keep, :]
            l_max_conf = l_max_conf[keep]
            l_max_id = l_max_id[keep]

            for j in range(l_box_array.shape[0]):
                bboxes.append(
                    [
                        l_box_array[j, 0],
                        l_box_array[j, 1],
                        l_box_array[j, 2],
                        l_box_array[j, 3],
                        l_max_conf[j],
                        l_max_conf[j],
                        l_max_id[j],
                    ]
                )

        bboxes_batch.append(bboxes)

    return bboxes_batch
