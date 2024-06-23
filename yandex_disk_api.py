"""
Скрипт для работы с API Яндекс.Диска для загрузки фотографий.

Этот скрипт использует API Яндекс.Диска для создания папки на диске,
 загрузки фотографий из локальной папки 'photo' на Яндекс.Диск,
а также удаления загруженных файлов из локальной папки после успешной
загрузки на Яндекс.Диск.

Для работы скрипта необходимо передать токен OAuth Яндекс.Диска
 в качестве аргумента при создании объекта класса YandexDiskApi.

Пример использования:
    api = YandexDiskApi(token_yand='Ваш_токен')
    api.creating_folder()
    api.saving_photo_disk()

Где <token_yand> - токен OAuth для доступа к API Яндекс.Диска.

"""

import sys

import logging
import os
from tqdm import tqdm
import requests


class YandexDiskApi:
    """
    Класс для работы с API Яндекс.Диска для загрузки фотографий.
    Attributes:
        token (str): Токен OAuth для доступа к API Яндекс.Диска.
        name_folder (str or None): Название папки на Яндекс.Диске,
         куда будут загружаться фотографии.
    """

    def __init__(self, token_yand: str):
        """
        Инициализация объекта класса YandexDiskApi.

        Args:
            token_yand (str): Токен OAuth для доступа к API Яндекс.Диска.
        """
        self.token = token_yand
        self.name_folder = None

    def _common_headers(self):
        """
        Формирует общие заголовки для запросов к API Яндекс.Диска.

        Returns:
            dict: Словарь с заголовками HTTP запроса.
        """

        headers = {
            "Authorization": f'OAuth {self.token}'
        }
        return headers

    def _request_folder_name(self):
        """
        Запрашивает у пользователя название папки для создания на Яндекс.Диске.

        Returns:
            str: Название папки, введенное пользователем или значение по умолчанию "image".
        """
        reply = input('Ведите название папки ---> ')
        self.name_folder = reply if reply else "image"
        return self.name_folder

    def creating_folder(self):
        """
        Создает папку на Яндекс.Диске с указанным именем или использует имя по умолчанию.

        Raises:
            ValueError: Если возникает ошибка создания папки.

        Notes:
            Использует API endpoint для создания ресурсов на Яндекс.Диске.
        """
        print("Введите имя папки, которую вы хотите создать, "
              "или нажмите Enter для использования имени по умолчанию 'image'.")

        url = "https://cloud-api.yandex.net/v1/disk/resources"
        name_folder = self.name_folder if self.name_folder is not None \
            else self._request_folder_name()
        params = {
            "path": f'{name_folder}'
        }
        response = requests.put(url, headers=self._common_headers(), params=params, timeout=5)

        if response.status_code == 201:
            logging.info(f"Папка '{self.name_folder}' успешно создана.")
        elif response.status_code == 409:
            logging.warning(f"Папка '{self.name_folder}' уже существует.")
        else:
            logging.warning(f"Неожиданный код состояния: {response.status_code}")

    def saving_photo_disk(self):
        """
        Загружает фотографии из локальной папки 'photo' на Яндекс.Диск в указанную папку.
        Raises:
            OSError: Если возникает ошибка доступа к локальной папке 'photo'.
            requests.exceptions.RequestException: Если возникает ошибка HTTP запроса
             к API Яндекс.Диска.

        Notes:
            Использует API endpoint для загрузки файлов на Яндекс.Диск.
        """

        name_files_list = self._list_files_in_directory()
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.name_folder if self.name_folder is not None else self.creating_folder()

        if name_files_list:
            for name_img in tqdm(name_files_list, desc="Загрузка фотографий", unit="фото"):
                params = {
                    "path": f'{self.name_folder}/{name_img}'
                }
                response = requests.get(url, headers=self._common_headers(),
                                        params=params, timeout=2)

                url_save = response.json()['href']

                with open(f'photo/{name_img}', 'rb') as image:
                    response_save = None
                    while response_save is None or response_save.status_code != 201:
                        response_save = requests.put(url_save, files={'file': image})

                        if response_save.status_code == 201:
                            print(f"Фото '{name_img}' успешно загружено на Яндекс.Диск.")
                            image.close()
                            self._delete_uploaded_photos(name_img)
                        else:
                            print(f"Ошибка при загрузке фото '{name_img}': {response_save.text}")

        else:
            print("Папка 'photo' пуста")
            sys.exit()

    def _list_files_in_directory(self):
        """
        Сканирует локальную папку 'photo' на наличие файлов.

        Returns:
            list: Список имен файлов в папке 'photo'.

        Raises:
            ValueError: Если папка 'photo' не существует или не является директорией.
        """

        current_dir = os.path.dirname(__file__)
        photo_dir = os.path.join(current_dir, 'photo')
        try:
            if not os.path.isdir(photo_dir):
                raise ValueError(f"Папка '{photo_dir}' не существует или не является директорией.")
            files = os.listdir(photo_dir)
            name_files = [f for f in files if os.path.isfile(os.path.join(photo_dir, f))]
            return name_files
        except OSError as e:
            print(f"Ошибка при сканировании папки '{photo_dir}': {e}")
            return []

    def _delete_uploaded_photos(self, name_img: str):
        """
        Удаляет из локальной папки 'photo' файлы, которые были успешно загружены на Яндекс.Диск.

        Args:
            name_img (str): Имя файла для удаления из папки 'photo'.

        Raises:
            ValueError: Если папка 'photo' не существует или не является директорией.
            OSError: Если возникает ошибка доступа к локальной папке 'photo'.
        """
        current_dir = os.path.dirname(__file__)
        photo_dir = os.path.join(current_dir, 'photo')
        try:
            if not os.path.isdir(photo_dir):
                raise ValueError(f"Папка '{photo_dir}' не существует или не является директорией.")

            file_path = os.path.join(photo_dir, name_img)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Файл '{name_img}' удалён из папки 'photo'.")

        except OSError as e:
            print(f"Ошибка при удалении файлов из папки '{photo_dir}': {e}")


if __name__ == '__main__':
    pass
