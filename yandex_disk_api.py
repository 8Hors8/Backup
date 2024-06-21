import sys

import requests
import logging
import os

import token_cont


class YandexDiskApi:

    def __init__(self, token_yand: str, name_profile: str):
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
        name_folder = self.name_folder if self.name_folder is not None else self._request_folder_name()
        params = {
            "path": f'{name_folder}/{self.name_profile}'
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
            for name_img in name_files_list:
                params = {
                    "path": f'{self.name_folder}/{self.name_profile}/{name_img}'
                }
                response = requests.get(url, headers=self._common_headers(), params=params, timeout=5)
                url_save = response.json()['href']
                with open(f'photo/{name_img}', 'rb') as image:
                    response = requests.put(url_save, files={'file': image})

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


if __name__ == '__main__':
    t = YandexDiskApi(token_cont.TOKEN_YND, token_cont.id_user)
    # t.creating_folder()
    t.saving_photo_disk()
