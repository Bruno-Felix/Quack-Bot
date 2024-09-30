import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os
from urllib.parse import urlparse

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


def perspective_image(image_bg_cv, image_sm_cv, coords):
    points_orig = np.float32([[0, 0], [image_sm_cv.shape[1], 0], [0, image_sm_cv.shape[0]], [image_sm_cv.shape[1], image_sm_cv.shape[0]]])

    points_dest = np.float32(coords)

    matrix = cv2.getPerspectiveTransform(points_orig, points_dest)

    image_sm_transformed = cv2.warpPerspective(image_sm_cv, matrix, (image_bg_cv.shape[1], image_bg_cv.shape[0]))

    result_pil = Image.fromarray(cv2.cvtColor(image_sm_transformed, cv2.COLOR_BGR2RGB))

    return result_pil

def make_image(template, image_attachment, time_request):
    image_path = f'image-{time_request}.png'  
    background_path = f'static/template/{template["filename"]}'

    download_image(image_attachment, image_path)

    background_image = Image.open(background_path)

    image_bg_cv = cv2.imread(background_path)
    image_sm_cv = cv2.imread(image_path)

    resultado = perspective_image(image_bg_cv, image_sm_cv, template['coords'])

    resultado.paste(background_image, (0,0), background_image)

    resultado.save(f'result-{time_request}.png')

def delete_images(time_request):
    delete_image(f'image-{time_request}.png')
    delete_image(f'result-{time_request}.png')

def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

def is_image(url, accept_gif = True):
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.jfif']
    if(accept_gif):
        image_extensions.append('.gif')
    
    file_extension = os.path.splitext(path)[1].lower()
    
    if file_extension in image_extensions:
        return True
    else:
        return False
