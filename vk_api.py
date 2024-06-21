"""
Модуль VkApi для работы с API социальной сети ВКонтакте.

Класс VkApi предоставляет методы для авторизации пользователя, получения информации о профиле,
работы с фотоальбомами и загрузки фотографий.

Пример использования:
    api = VkApi('Имя_пользователя', token='Ваш_токен')
    api.users_info()
    api.getting_list_albums()
    api.upload_photo()
"""
import os
import sys
import re
from time import sleep
import requests

from tqdm import tqdm


class VkApi:
    """
    Класс VkApi предоставляет интерфейс для работы с API ВКонтакте.

    Attributes:
        url (str): Базовый URL для запросов к API ВКонтакте.
        id (str): Имя пользователя или ID профиля.
        access_token (str): Access token для доступа к API ВКонтакте.
        users_id (int): ID пользователя ВКонтакте.
        id_albums_size (dict): Словарь с размерами альбомов пользователя.
        version (str): Версия API ВКонтакте.

    Methods:
        __init__(name_profile: str, token=None, version='5.199'):
            Инициализирует объект VkApi.

        _request_id_application():
            Запрашивает ID приложения для получения access token.

        _receiving_access_token(client_id: str):
            Получает access token по URL-адресу.

        _request_api(method: str = None, params: dict = None, url_photo: str = None):
            Выполняет HTTP-запрос к API ВКонтакте.

        _common_params():
            Возвращает общие параметры для запросов к API ВКонтакте.

        _error_api(response):
            Обрабатывает ошибки ответа от API ВКонтакте.

        users_info():
            Получает информацию о пользователе.

        getting_list_albums():
            Получает список альбомов пользователя.

        upload_photo():
            Загружает фотографии из альбомов пользователя.

        _number_photos(id_albums: list):
            Обрабатывает ввод количества фотографий для скачивания.

        _url_photos(number_photos: dict):
            Создает словарь с URL фотографий для скачивания.

        _loading(url_photos: dict):
            Загружает фотографии по URL в папку 'photo'.
    """
    url = 'https://api.vk.com/method/'

    def __init__(self, name_profile: str, token_vk: str = None, version='5.199'):
        """

        Инициализирует объект VkApi.

        Args:
            name_profile (str): Имя пользователя или ID профиля.
            token_vk (str, optional): Access token для доступа к API ВКонтакте.
             Если не указан, запрашивается автоматически.
            version (str, optional): Версия API ВКонтакте. По умолчанию '5.199'.
        """

        self.id = name_profile
        self.access_token = token_vk if token_vk is not None else self._request_id_application()
        self.users_id = None
        self.id_albums_size = {}

        self.version = version

    def _request_id_application(self):
        """
        Запрашивает ID приложения для получения access token.

        Returns:str: Access token для доступа к API ВКонтакте.
        """

        answer = input('Укажите ID приложения ---> ')

        token = self._receiving_access_token(answer)

        return token

    def _receiving_access_token(self, client_id: str):
        """
        Получает access token по URL-адресу.

        Args: client_id (str): ID приложения ВКонтакте.
        Returns: str: Access token для доступа к API ВКонтакте.
        """

        url = (f'https://oauth.vk.com/authorize?client_id={client_id}'
               f'&display=page&redirect_uri=https://example.com/callback&scope=offline,photos&'
               f'response_type=token&v=5.131&state=123456')

        print(f'Передайте по ссылке\n{url}')
        token_url = input('Вставьте URL страницы на которую вас перебросило \n---> ')

        pattern = r"access_token=([a-zA-Z0-9._-]+)"
        match = re.search(pattern, token_url)
        if match:
            access_token = match.group(1)
            print(f'Ваш токен: {access_token}')
        else:
            print("Токен доступа не найден")
            access_token = None

        return access_token

    def _request_api(self, method: str = None, params: dict = None, url_photo: str = None):
        """
        Выполняет HTTP-запрос к API.

        :param method: Метод API для обычного запроса.
        :param params: Параметры запроса.
        :param url_photo: URL для загрузки фотографии (если указан, используется GET запрос).
        :return: Объект Response или None в случае ошибки.
        """
        try:
            if url_photo is None:
                response = requests.get(self.url + method,
                                        params={**self._common_params(), **params}, timeout=0.5)
            else:
                response = requests.get(url_photo, timeout=0.5)

            response.raise_for_status()  # Проверка на ошибки HTTP

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

        return response

    def _common_params(self):
        """
        Возвращает общие параметры для запросов к API ВКонтакте.

        Returns:dict: Параметры запроса (access_token и version).
        """
        params = {'access_token': self.access_token,
                  'v': self.version
                  }

        return params

    def _error_api(self, response):
        """
        Обрабатывает ошибки ответа API
        :param response: ответ от сервера
        :return: str кодом ошибки
        """
        if list(response.json().keys())[0] != 'response':
            if response.json()['error']['error_code'] == 5:
                output_ = "Ошибка авторизации ваш токен не действителен"
                print(output_)
                sys.exit()
            else:
                output_ = f"Произошла ошибка  код ошибки " \
                          f"{response.json()['error']['error_code']}." \
                          f"\nСмотрите в домунтациик VK API\nhttps://dev.vk.com/ru/reference/errors"
                print(output_)
        else:
            output_ = f'Пользователя с ником {self.id} не найден'
            print(output_)
            sys.exit()

    def users_info(self):
        """
        Получает информацию о пользователе.

        Returns:str: Сообщение о найденном пользователе.
        """
        params = {'user_ids': self.id}

        response = requests.get(self.url + 'users.get',
                                params={**self._common_params(), **params}, timeout=0.5)

        if 'error' not in response.json().keys() and response.json()['response'] != []:
            self.users_id = response.json()['response'][0]['id']
            output_ = f"По указанному ID был найден пользователь " \
                      f"{response.json()['response'][0]['first_name']} " \
                      f"{response.json()['response'][0]['last_name']}"
            return output_
        self._error_api(response)
        return None

    def getting_list_albums(self):
        """
        Получает список альбомов пользователя и их размеры.

        Returns:str: Сообщение о количестве и названиях альбомов.
        """
        params = {'owner_id': self.users_id,
                  'need_system': '1'
                  }
        response = requests.get(self.url + 'photos.getAlbums',
                                params={**self._common_params(), **params}, timeout=0.5)

        if 'error' not in response.json().keys():
            output_ = f"Количество альбомов у профиля: {response.json()['response']['count']}"
            items = response.json()['response']['items']
            for album in items:
                id_albums = album['id']
                size = album['size']
                title = album['title']
                if size > 0:
                    output_ += f'\nID:{id_albums}, количество фотографий {size}, название: {title}'
                    self.id_albums_size[str(id_albums)] = int(size)
            return output_
        self._error_api(response)
        return None

    def upload_photo(self):
        """
        Загружает фотографии из альбомов пользователя в папку 'photo'.

        """
        print('\nДля скачивания фото через запятую укажите ID альбомов.\n'
              'Если ничего не указывать то поиск фотографий будет '
              '\nпроходить в альбоме  в "фотографии со страницы пользователя" ')

        id_albums = []

        answer_id = input('Укажите ID альбома(мов) ---> ')
        if not answer_id:
            id_albums.append('-6')
        else:
            id_albums = list(album for album in answer_id.split(','))

        number_photos = self._number_photos(id_albums)
        url_photos = self._url_photos(number_photos)
        self._loading(url_photos)

    def _number_photos(self, id_albums: list):
        """
        Обрабатывает ввод количества фотографий, требуемых для скачивания
        :param id_albums:
        :return: dict
        """
        number_photos = {}

        for id_album in id_albums:
            while True:
                amount_photo = self.id_albums_size[id_album]
                try:
                    quantity = int(input(f'Укажите сколько фотографий '
                                         f'скачать для альбома с ID: {id_album} ---> '))
                    if not 0 < quantity <= amount_photo:
                        print("Вы указали неверное количество.",
                              f'Количество фото в '
                              f'альбоме: {amount_photo}' if quantity > amount_photo else '')
                        continue
                    break
                except ValueError:
                    print("Вы указали неверное количество. Пожалуйста, введите число.")

            number_photos[id_album] = quantity
        return number_photos

    def _url_photos(self, number_photos: dict):
        """
        Создает словарь, содержащий ID и URL фотографий, выбранных ранее из альбомов
        :param number_photos: словарь из ID альбома и требуемое количества фото для загрузки
        :return: Словарь из ID фото и URL для скачивания
        """
        id_url_photos = {}
        for id_album, quantity in number_photos.items():

            params = {'owner_id': self.users_id,
                      'album_id': id_album,
                      }
            response = self._request_api(method='photos.get', params=params)
            if 'error' not in response.json().keys():
                photo_dict = response.json()['response']['items'][:quantity]
                for el in photo_dict:
                    id_photo = el['id']
                    url = el['sizes'][-1]['url']
                    id_url_photos[str(id_photo)] = url
            else:
                self._error_api(response)
        return id_url_photos

    def _loading(self, url_photos: dict):
        """
        Загружает фотографии по словарю с парами id и url в папку 'photo' текущей директории.

        :param url_photos: Словарь с парами id и url фотографий.
        """
        folder_name = 'photo'
        folder_path = os.path.join(os.getcwd(), folder_name)  # Получаем полный путь к папке

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for id_photo, url in tqdm(url_photos.items(), desc='Загрузка фотографий', unit='фото'):
            response = self._request_api(url_photo=url)
            if response:

                filename = os.path.join(folder_path, f'photo_{id_photo}.jpg')

                with open(filename, 'wb') as f:
                    f.write(response.content)
                tqdm.write(f"Фотография с ID {id_photo} успешно загружена.")
            else:
                tqdm.write(f"Произошла ошибка при загрузке фотографии с ID {id_photo}.")
                sleep(5)


if __name__ == '__main__':
    pass
