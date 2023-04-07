#!/usr/bin/python3
import base64
import json
import os
from io import BytesIO

import cv2
import joblib
import numpy as np
import requests
from tqdm import tqdm

VERSION = __version__ = '0.2.0 '

API_KEY = 'YczU5z-IRZ3VirBslEv5lYSVvfJnER8z'
API_SECRET = 'qomqCnxR1Y_pkohBttQLiS3lPDWTHmx8'
RETURN_ATTRIBUTES = 'gender,beauty,age,smiling,headpose,ethnicity,skinstatus'
RETURN_LANDMARK = 1

assert API_KEY != 'api_key', \
    'You need to get your api-key firstly. Please, follow the url:\n' \
                                 'https://www.faceplusplus.com/v2/pricing-details/'
assert API_SECRET != 'api_secret', \
    'You need to get your api-secret firstly. Please, follow the url:\n' \
                                 'https://www.faceplusplus.com/v2/pricing-details/'

def photo_check(ref):

    parameters = {'api_key': API_KEY, 'api_secret': API_SECRET, 'image_base64': ref,
                  'return_attributes': RETURN_ATTRIBUTES, 'return_landmark': RETURN_LANDMARK}
    response = requests.post('https://api-us.faceplusplus.com/facepp/v3/detect',
                             data=parameters)
    json_dict = json.loads(response.text)
    angles = json_dict['faces'][0]['attributes']['headpose']['roll_angle']
    return angles, json_dict


def rotate_image(image, angle, center=None):

    if center is not None:
        image_center = center
    else:
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def photo_check2(ref):

    parameters = {'api_key': API_KEY, 'api_secret': API_SECRET, 'image_base64': ref,
                  'return_landmark': 'face,nose,left_eyebrow,right_eyebrow'}
    response = requests.post('https://api-us.faceplusplus.com/facepp/v1/face/thousandlandmark',
                             data=parameters)
    json_dict = json.loads(response.text)
    return json_dict


def l2distance(point1, point2):

    return ((point1['x'] - point2['x']) * (point1['x'] - point2['x']) + \
            (point1['y'] - point2['y']) * (point1['y'] - point2['y'])) ** .5


def get_angle(point1, point2, point3, point4):

    vector1 = np.array([point2['x'] - point1['x'], point2['y'] - point1['y']])
    vector2 = np.array([point4['x'] - point3['x'], point4['y'] - point3['y']])
    cos = vector1.dot(vector2) / (np.sqrt(vector1.dot(vector1)) * np.sqrt(vector2.dot(vector2)))
    return np.degrees(np.arccos(cos))


def extract_features(file, resize=False):
    
    try:
        # read photo from the provided image path
        photo = cv2.imread(file)
        # resize photo if necessary, that implies the resulting photo will be also downscaled
        if resize:
            photo = cv2.resize(photo, (256, 256))
        # convert numpy ndarray to base64-encoded string
        _, buffer = cv2.imencode('.jpg', photo)
        b_io = BytesIO(buffer)
        b_io.seek(0)
        b64string = base64.b64encode(b_io.read())

        # make first api request to face++
        angles, json_dict = photo_check(b64string)

        # finding the center of the face
        center = json_dict['faces'][0]['face_rectangle']
        bounding_box = center['left'], center['top'], center['width'], center['height']
        center = center['left'] + center['width'] // 2, center['top'] + center['height'] // 2

        # rotate image among calculated center
        rotated = rotate_image(photo, angles, center)

        # convert rotated numpy ndarray to base64-encoded string
        _, buffer = cv2.imencode('.jpg', rotated)
        b_io = BytesIO(buffer)
        b_io.seek(0)
        b64string = base64.b64encode(b_io.read())

        # make second api request to face++, get 1000 keypoints
        json_dict2 = photo_check2(b64string)

        # divide keypoints into three group for convenience
        points = json_dict2['face']['landmark']['face']
        nose = json_dict2['face']['landmark']['nose']
        eyebrows = json_dict2['face']['landmark']['left_eyebrow'], \
                   json_dict2['face']['landmark']['right_eyebrow']

        # calculate euclidean distances between defined points
        distance = {}
        for keypoint1, keypoint2, tag in \
                         [('face_contour_left_16', 'face_contour_right_16', 'chin'),
                          ('face_contour_left_30', 'face_contour_right_30', 'jawline'),
                          ('face_contour_left_62', 'face_contour_right_62', 'cheekbones'),
                          ('face_hairline_16', 'face_hairline_128', 'browline'),
                          ('face_hairline_31', 'face_hairline_113', 'forehead1'),
                          ('face_hairline_47', 'face_hairline_97', 'forehead2'),
                          ('face_hairline_63', 'face_hairline_82', 'forehead3'),
                          ('face_hairline_72', 'face_contour_right_0', 'facelength'),
                          ('face_hairline_63', 'face_contour_right_16', 'facelength_l1'),
                          ('face_hairline_82', 'face_contour_left_16', 'facelength_r1'),
                          ('face_hairline_47', 'face_contour_right_30', 'facelength_r2'),
                          ('face_hairline_97', 'face_contour_left_30', 'facelength_l2')]:
            point1, point2 = json_dict2['face']['landmark']['face'][keypoint1], \
                             json_dict2['face']['landmark']['face'][keypoint2]
            distance[tag] = l2distance(point1, point2)

        # get other measurements by approximation and interpolation
        distance['w_center'] = (distance['browline'] + distance['cheekbones']) / 2
        distance['w_lower'] = distance['jawline']
        distance['w_upper'] = distance['forehead1'] * 0.8 + distance['forehead2'] * 0.2
        distance['l_center'] = distance['facelength']
        distance['l_med'] = (distance['facelength_l1'] + distance['facelength_r1']) / 4 + \
                            (distance['facelength_l2'] + distance['facelength_r2']) / 4

        # calculate angles between necessary points
        angle = {}
        angle['chin'] = get_angle(points['face_contour_right_0'],
                                  points['face_hairline_72'],
                                  points['face_contour_right_16'],
                                  points['face_contour_right_30']) / 2 + \
                        get_angle(points['face_contour_right_0'],
                                  points['face_hairline_72'],
                                  points['face_contour_left_16'],
                                  points['face_contour_left_30']) / 2
        angle['cheeks'] = get_angle(points['face_contour_right_0'],
                                    points['face_hairline_72'],
                                    points['face_contour_right_30'],
                                    points['face_contour_right_62']) / 2 + \
                          get_angle(points['face_contour_right_0'],
                                    points['face_hairline_72'],
                                    points['face_contour_left_30'],
                                    points['face_contour_left_62']) / 2
        angle['forehead'] = get_angle(points['face_hairline_72'],
                                      points['face_contour_right_0'],
                                      points['face_hairline_47'],
                                      points['face_hairline_16']) / 2 + \
                            get_angle(points['face_hairline_72'],
                                      points['face_contour_right_0'],
                                      points['face_hairline_97'],
                                      points['face_hairline_128']) / 2
        return angles, distance, angle, points, nose, eyebrows, bounding_box, json_dict
    except KeyError as key_exception:
        # only 1000 images daily can be extracted due to free plan limit
        print(key_exception, file, json_dict)
        return None

if __name__ == '__main__':
    # generated2 is a directory with 5000 images from https://www.thispersondoesnotexist.com/
    files = [os.path.join(r'generated2', f) for f in os.listdir(r'generated2')]
    # output file for extracted features
    OUTFILE = 'gen2_features'
    if os.path.exists(OUTFILE):
        results = joblib.load(OUTFILE)
    else:
        results = []
    # iterate over all images, and downscaling them
    for f in tqdm(files[len(results):]):
        results.append(extract_features(f, True))
        if len(results) % 200 == 0:
            joblib.dump(results, OUTFILE, 3, 4)
    joblib.dump(results, OUTFILE, 3, 4)
