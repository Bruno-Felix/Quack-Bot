import requests
import cv2
import numpy as np
from PIL import Image
from io import BytesIO


def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        
        image.save(save_path)

        print(f'Imagem baixada e salva como {save_path}')

    except requests.exceptions.RequestException as e:
        print(f'Erro ao baixar a imagem: {e}')
    except IOError as e:
        print(f'Erro ao salvar a imagem: {e}')


def perspectiveImage(image_bg_cv, image_sm_cv):
    points_orig = np.float32([[0, 0], [image_sm_cv.shape[1], 0], [0, image_sm_cv.shape[0]], [image_sm_cv.shape[1], image_sm_cv.shape[0]]])

    #points_dest = np.float32([[18, 138], [254, 118], [58, 360], [270, 272]]) # jyp
    points_dest = np.float32([[87, 96], [300, 99], [81, 406], [294, 411]])
    
    matrix = cv2.getPerspectiveTransform(points_orig, points_dest)

    image_sm_transformed = cv2.warpPerspective(image_sm_cv, matrix, (image_bg_cv.shape[1], image_bg_cv.shape[0]))

    result_pil = Image.fromarray(cv2.cvtColor(image_sm_transformed, cv2.COLOR_BGR2RGB))

    return result_pil

def make_image():
    caminho_cabeca = "teste.png"  
    caminho_monitor = "tohr_carteira.png" 

    imagem_monitor = Image.open(caminho_monitor)

    image_bg_cv = cv2.imread(caminho_monitor)
    image_sm_cv = cv2.imread(caminho_cabeca)

    resultado = perspectiveImage(image_bg_cv, image_sm_cv)

    resultado.paste(imagem_monitor, (0,0), imagem_monitor)

    resultado.save('nseinsei.png')
