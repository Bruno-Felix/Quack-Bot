import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        
        image.save(save_path)

    except requests.exceptions.RequestException as e:
        print(f'Erro ao baixar a imagem: {e}')
    except IOError as e:
        print(f'Erro ao salvar a imagem: {e}')


def perspectiveImage(image_bg_cv, image_sm_cv, coords):
    points_orig = np.float32([[0, 0], [image_sm_cv.shape[1], 0], [0, image_sm_cv.shape[0]], [image_sm_cv.shape[1], image_sm_cv.shape[0]]])

    points_dest = np.float32(coords)

    matrix = cv2.getPerspectiveTransform(points_orig, points_dest)

    image_sm_transformed = cv2.warpPerspective(image_sm_cv, matrix, (image_bg_cv.shape[1], image_bg_cv.shape[0]))

    result_pil = Image.fromarray(cv2.cvtColor(image_sm_transformed, cv2.COLOR_BGR2RGB))

    return result_pil

def make_image(template, image_attachment):
    image_path = 'image.png'  
    background_path = f'static/template/{template["filename"]}'

    download_image(image_attachment, 'image.png')

    background_image = Image.open(background_path)

    image_bg_cv = cv2.imread(background_path)
    image_sm_cv = cv2.imread(image_path)

    resultado = perspectiveImage(image_bg_cv, image_sm_cv, template['coords'])

    resultado.paste(background_image, (0,0), background_image)

    resultado.save('result.png')

def delete_images():
    delete_image('image.png')
    delete_image('result.png')

def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

