import os
import cv2
import imagehash
from PIL import Image
import numpy as np
from imagehash import ImageHash


def get_image_hash(image_path: str) -> ImageHash:
    """Obtiene el hash de una imagen usando pHash (hash perceptual)"""
    image = Image.open(image_path)
    return imagehash.phash(image)


def get_image_histogram(image_path: str) -> np.ndarray:
    """Calcula el histograma de la imagen en escala de grises"""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = hist / hist.sum()  # Normalizar el histograma
    return hist


def compare_histograms(hist1: np.ndarray, hist2: np.ndarray) -> float:
    """Compara dos histogramas utilizando correlación"""
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)


def find_duplicates(directory: str, use_histogram_comparison: bool=False) -> list:
    """Encuentra duplicados en un directorio usando hash o histograma"""
    hashes = {}  # Diccionario para almacenar hashes o histogramas
    duplicates = []  # Lista de duplicados encontrados

    # Recorrer todas las imágenes en el directorio
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Usar hash o histograma según la opción
            if use_histogram_comparison:
                hist = get_image_histogram(file_path)
                found_duplicate = False

                for existing_hist in hashes.values():
                    # Comparar histogramas con las imágenes ya procesadas
                    if compare_histograms(hist, existing_hist) > 0.9:  # Umbral de similitud (ajustable)
                        found_duplicate = True
                        break

                if found_duplicate:
                    duplicates.append(file_path)
                else:
                    hashes[file_path] = hist
            else:
                # Usar hash perceptual para comparación
                image_hash = get_image_hash(file_path)
                if image_hash in hashes:
                    duplicates.append((hashes[image_hash], file_path))
                else:
                    hashes[image_hash] = file_path

    return duplicates


def confirm_and_remove_duplicates(duplicates: list) -> None:
    """Mostrar los duplicados y pedir confirmación para eliminarlos"""
    if not duplicates:
        print("No se encontraron imágenes duplicadas.")
        return

    # Mostrar las imágenes duplicadas encontradas
    print("Posibles duplicadas encontradas:")
    for i, duplicate in enumerate(duplicates):
        if isinstance(duplicate, tuple):
            print(f"\n[{i + 1}] Imagen 1: {duplicate[0]}\n    Imagen 2: {duplicate[1]}")
        else:
            print(f"[{i + 1}] Imagen: {duplicate}")

    # Pedir al usuario confirmación para eliminar
    to_remove = input("\n¿Deseas eliminar las imágenes duplicadas? (y/n): ").strip().lower()

    if to_remove == 'y':
        for duplicate in duplicates:
            if isinstance(duplicate, tuple):
                confirm = input(f"\n¿Eliminar {duplicate[1]}? (y/n): ").strip().lower()
                if confirm == 'y':
                    os.remove(duplicate[1])
                    print(f"{duplicate[1]} ha sido eliminada.")
                else:
                    print(f"{duplicate[1]} no se ha eliminado.")
            else:
                confirm = input(f"\n¿Eliminar {duplicate}? (y/n): ").strip().lower()
                if confirm == 'y':
                    os.remove(duplicate)
                    print(f"{duplicate} ha sido eliminada.")
                else:
                    print(f"{duplicate} no se ha eliminado.")
    else:
        print("No se eliminaron imágenes.")


# Ruta del directorio a verificar
p = "/media/alexperezortuno/Workspace/Documents"

# Buscar duplicados
# Elegir si comparar por hash o por histograma (True para histograma)
d = find_duplicates(p, True)
if not d:
    d = find_duplicates(p, False)

# Confirmar y eliminar duplicados
confirm_and_remove_duplicates(d)
