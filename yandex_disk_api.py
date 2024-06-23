import sys


import logging
import os
from tqdm import tqdm
import requests




class YandexDiskApi:

    def __init__(self, token_yand: str):
        self.token = token_yand
        self.name_folder = None
        self.name_profile = name_profile

    def _common_headers(self):
        headers = {
            "Authorization": f'OAuth {self.token}'
        }
        return headers

    def _request_folder_name(self):
        reply = input('Ведите название папки ---> ')
        self.name_folder = reply if reply else "image"
        return self.name_folder

    def creating_folder(self):
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
            logging.warning(f"Папка '{self.name_folder}/{self.name_profile}' уже существует.")
        else:
            logging.warning(f"Неожиданный код состояния: {response.status_code}")

    def saving_photo_disk(self):
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
        Сканирует папку 'photo' на наличие файлов.
        :return: Возращает список из имени файлов
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
        Удаляет из папки 'photo' те файлы, которые были успешно загружены на Яндекс.Диск.
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
