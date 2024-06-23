"""
Скрипт для создания резервной копии фотографий из альбомов пользователей VK в Яндекс.Диск.

Этот скрипт использует API VK и API Яндекс.Диска для получения информации о пользователях VK,
их альбомах, загрузки фотографий на Яндекс.Диск и создания резервной копии фотографий.

Пример использования:
    backup = Backup(name_profiles, token_yand='ваш токен от Yandex.Disk',
     token_vk='ваш токен от VK')
    backup.users_info()
    backup.getting_list_albums()
    backup.upload_photo()
    backup.creating_folder()
    backup.saving_photo_disk()

"""

from vk_api import VkApi
from yandex_disk_api import YandexDiskApi


class Backup(VkApi, YandexDiskApi):
    """
    Класс Backup для создания резервной копии фотографий из альбомов пользователей VK в Яндекс.Диск.

    Attributes:
        name_profile (str): Имя профиля VK, для которого создается резервная копия.
        token_yand (str): Токен OAuth для доступа к API Яндекс.Диска.
        token_vk (str, optional): Токен доступа к API VK. Если не указан,
        требуются права на доступ к фотографиям и альбомам.
    """

    def __init__(self, name_profile: str, token_yand, token_vk: str = None):

        VkApi.__init__(self, name_profile, token_vk)
        YandexDiskApi.__init__(self, token_yand)


if __name__ == '__main__':
    t = Backup(name_profiles, token_yand='token_yand', token_vk='token_vk')
    t.users_info()
    t.getting_list_albums()
    t.upload_photo()
    t.creating_folder()
    t.saving_photo_disk()
