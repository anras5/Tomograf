import datetime
import os.path

import numpy as np
import csv
from matplotlib.image import imread
from PIL import Image
from skimage import color


from flaskr.src.bresenham import bresenham_algorithm
from flaskr.src.dicom import Patient, save_dicom, read_dicom
from flaskr.src.filters import filter_h


def calculate_sinogram(input_path: str, output_dir: str,
                       interval: int, detectors_number: int, extent: int,
                       gradual: bool,
                       dicom: bool = False,
                       filtered: bool = False,
                       patient: Patient = None,
                       dicom_name: str = ''
                       ):
    """Calculates sinogram from input file and saves a sinogram visualization in `sinogram_path`.
    Then from this sinogram, calculates an output file and saves it in `result_path`.
    Function uses the cone method.

    Parameters
    ----------
    input_path: str
        Path of the input file
    output_dir: str
        Path to the directory of the output files. Will contain sinogram (gradual sinograms)
        and output file (gradual output files)
    interval: int
        The angle by which the emitter is to be moved
    detectors_number: int
        How many detectors will be used
    extent: int
        The angular span of the detectors
    gradual: bool
        if True every step will be saved in a separate file
    dicom: bool, optional
        if True, a .dcm file will be created with data provided in
    filtered: bool, optional
        if True, there will be used a filter on sinogram
    patient: Patient, optional
        data about patient, should not be empty if `dicom` is set to True
    dicom_name: str
        dicom filename

    Returns
    -------
    gradual_number: int
        Number of files saved if `gradual` is True.
        If gradual is False, `gradual_number` is 0.
    """

    # przygotowujemy odpowiednie ścieżki do plików
    sinogram_path = os.path.join(output_dir, 'sinogram.png')
    result_path = os.path.join(output_dir, 'output.png')
    if gradual:
        os.makedirs(os.path.join(output_dir, 'gradual_sinogram'))
        os.makedirs(os.path.join(output_dir, 'gradual_result'))

    # zmieniamy parametry przekazane w funkcji ze stopni na radiany
    interval = interval * np.pi / 180 # Co jaki kąt przesuwany jest emitter po okręgu
    extent = extent * np.pi / 180  # jaka jest rozpiętość kątowa detectors

    # inicjalizacja zmiennych używanych później
    gradual_number = 0
    sinogram = np.zeros((int(2 * np.pi / interval), detectors_number))

    # jeżeli plik to DICOM, wczytujemy z niego dane
    if input_path[-4:] == '.dcm':
        input_jpg_path = os.path.join(output_dir, 'input.jpg')
        image, _ = read_dicom(input_path)
        image_scaled = (255.0 / np.amax(image)) * image
        image_scaled = image_scaled.astype(np.uint8)
        image_image = Image.fromarray(image_scaled, mode='L')
        image_image.save(input_jpg_path)
    else:
        image = imread(input_path)
        try:
            image = color.rgb2gray(image)
        except ValueError:
            pass

    X = image.shape[0] / 2  # współrzędna X środka obrazka
    Y = image.shape[1] / 2  # współrzędna Y środka obrazka
    R = np.sqrt(X ** 2 + Y ** 2)  # długość promienia okręgu, po którym będzie "poruszać się" emitter

    # ---------------------------------------------------------------------------------------------------------------- #
    # OBLICZANIE SINOGRAMU
    # ---------------------------------------------------------------------------------------------------------------- #
    # W zewnętrznej pętli wyznaczamy kolejne pozycje emitera, będą one o 0 do 2pi z odstępem co interval
    for emitter_idx, emitter_angle in zip(range(int(2 * np.pi / interval)), np.arange(0, 2 * np.pi, interval)):
        # wyznaczamy współrzędne (x, y) emittera na podstawie wartości X, Y oraz R i kąta (emitter_angle) z danej
        # interacji
        emitter_coordinates = [int(X + R * np.cos(emitter_angle)), int(Y + R * np.sin(emitter_angle))]

        # W wewnętrznej pętli wyznaczamy pozycje detectorów
        detector_start = emitter_angle + np.pi - extent / 2
        detector_end = emitter_angle + np.pi + extent / 2
        for detector_idx, detector_angle in zip(range(detectors_number),
                                                np.arange(detector_start, detector_end, extent / detectors_number)):
            # wyznaczamy współrzędne (x, y) detectora
            detector_coordinates = [int(X + R * np.cos(detector_angle)), int(Y + R * np.sin(detector_angle))]

            # korzystając z algorytmu bresenham_algorithm wyliczamy punkty leżące na linii pomiędzy emitter i detector
            line_points = list(bresenham_algorithm(emitter_coordinates[0], emitter_coordinates[1],
                                                   detector_coordinates[0], detector_coordinates[1]))

            points_on_line = 0  # licznik punktów które znajdują się na obrazku
            values_sum = 0
            # iterujemy po punktach wyznaczonych przed chwilą przy pomocy algorytmu bresenhama
            for point in line_points:
                if 0 <= point[0] < image.shape[0] and 0 <= point[1] < image.shape[1]:
                    # jeżeli punkt należy do obrazka dodajemy 1 do licznika punktów i zwiększamy wartość sumy
                    # o wartość z punktu na obrazku wejściowym
                    points_on_line += 1
                    values_sum += image[point[0]][point[1]]
            if points_on_line > 0:
                # do sinogramu w odpowiednią komórkę wstawiamy wartość sumy uzyskaną w pętli powyżej podzieloną
                # przez liczbę punktów
                sinogram[emitter_idx][detector_idx] = values_sum / points_on_line
            else:
                sinogram[emitter_idx][detector_idx] = 0

        if gradual:
            # zwiększamy licznik plików
            gradual_number += 1
            # zapisujemy tymczasowy sinogram do pliku
            sinogram_gradual_path = os.path.join(output_dir, 'gradual_sinogram', f'sinogram{emitter_idx}.png')
            sinogram_gradual_scaled = (255.0 / np.amax(sinogram)) * sinogram
            sinogram_gradual_scaled = sinogram_gradual_scaled.astype(np.uint8)
            sinogram_gradual_image = Image.fromarray(sinogram_gradual_scaled.T, mode='L')
            sinogram_gradual_resized = sinogram_gradual_image.resize(image.shape, resample=Image.NEAREST)
            sinogram_gradual_resized.save(sinogram_gradual_path)

    # zapisujemy sinogram do pliku - najpierw normalizujemy, później zapisujemy
    sinogram_scaled = (255.0 / np.amax(sinogram)) * sinogram
    sinogram_scaled = sinogram_scaled.astype(np.uint8)
    sinogram_image = Image.fromarray(sinogram_scaled.T, mode='L')
    sinogram_resized = sinogram_image.resize(image.shape, resample=Image.NEAREST)
    sinogram_resized.save(sinogram_path)

    # ---------------------------------------------------------------------------------------------------------------- #
    # OBLICZANIE OBRAZU WYJŚCIOWEGO
    # ---------------------------------------------------------------------------------------------------------------- #
    mse = [ ['Iteration', 'RMSE'] ]

    if filtered:
        sinogram_f = filter_h(sinogram)
    else:
        sinogram_f = sinogram
    result = np.zeros(image.shape)
    normalization_matrix = np.zeros(image.shape)
    # Wyznaczamy obraz końcowy na podstawie powstałego sinogramu
    for i in range(sinogram_f.shape[0]):
        emitter_coordinates = [int(X + R * np.cos(interval * i)), int(Y + R * np.sin(interval * i))]
        for j in range(sinogram_f.shape[1]):
            detector_angle = interval * i + np.pi - extent / 2 + j * extent / sinogram_f.shape[1]
            detector_coordinates = [int(X + R * np.cos(detector_angle)), int(Y + R * np.sin(detector_angle))]

            line_points = list(bresenham_algorithm(emitter_coordinates[0], emitter_coordinates[1],
                                                   detector_coordinates[0], detector_coordinates[1]))

            for point in line_points:
                if 0 <= point[0] < image.shape[0] and 0 <= point[1] < image.shape[1]:
                    result[point[0]][point[1]] += sinogram_f[i][j]
                    normalization_matrix[point[0]][point[1]] += 1

        if gradual:
            norm_max = np.amax(result)
            result_gradual = result.copy()
            for x in range(result_gradual.shape[0]):
                for y in range(result_gradual.shape[1]):
                    if normalization_matrix[x][y] != 0:
                        result_gradual[x][y] = result_gradual[x][y] / normalization_matrix[x][y]
                        # result_gradual[x][y] = result_gradual[x][y] / norm_max
                    else:
                        result_gradual[x][y] = 0

            result_gradual_path = os.path.join(output_dir, 'gradual_result', f'output{i}.png')
            result_gradual_scaled = (255.0 / np.amax(result_gradual)) * result_gradual
            result_gradual_scaled = result_gradual_scaled.astype(np.uint8)
            result_gradual_image = Image.fromarray(result_gradual_scaled, mode='L')
            result_gradual_image.save(result_gradual_path)

            # Liczymy błąd średniokwadratowy dla danej iteracji
            mse_sum = 0
            for x in range(len(image)):
                for y in range(len(image[x])):
                    mse_sum += (result_gradual[x][y] - image[x][y]) ** 2
            mse.append([i, (mse_sum / image.size) ** (1/2)])



    norm_max = max([max(o) for o in result])
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            if normalization_matrix[x][y] != 0:
                result[x][y] = result[x][y] / normalization_matrix[x][y]
                # result[x][y] = result[x][y] / norm_max
            else:
                result[x][y] = 0

    if not gradual:
        # Liczymy błąd średniokwadratowy dla końcowego obrazu
        mse_sum = 0
        for x in range(len(image)):
            for y in range(len(image[x])):
                mse_sum += (result[x][y] - image[x][y]) ** 2
        mse.append([1, (mse_sum / image.size) ** (1 / 2)])

    result_scaled = (255.0 / np.amax(result)) * result
    result_scaled = result_scaled.astype(np.uint8)
    result_image = Image.fromarray(result_scaled, mode='L')
    result_image.save(result_path)

    # zapisujemy plik wyjściowy w formacie dicom
    if dicom:
        dicom_path = os.path.join(output_dir, dicom_name)
        save_dicom(result_scaled, dicom_path,
                   patient.name, patient.id, patient.sex, patient.birth_date, patient.study_date,
                   patient.comments)

    # zapisujemy plik .csv
    rmse_path = os.path.join(output_dir, 'rmse.csv')
    with open(rmse_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(mse)

    return gradual_number, mse[-1][1]
