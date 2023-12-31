import random

from api import PetFriends
from config import valid_email, no_valid_email, valid_password, images
import os

pf = PetFriends()


# 1 GET /api/create_pet_simple Add information about new pet without photo
def test_successful_add_self_pet_without_photo(name='Бобр - без фото', animal_type='Собакен', age=2):
    """Проверяем возможность добавления питомца без фото"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца его имя, тип и возраст
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name


# 2 GET /api/key Get API key
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result  # - есть key отлично, иначе ошибка


# 3 GET /api/pets Get list of pets
def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    print('\n len', len(result['pets']))
    assert len(result['pets']) > 0


# 4 POST /api/pets Add information about new pet
def test_add_new_pet_with_valid_data(name='Бобр', animal_type='Собакен', age='5',
                                     pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что можно добавить питомца с валидными данными"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    print("#1.3 status", status)
    print("#1.4 result", result)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name


# 5 POST /api/pets/set_photo{pet_id} Add photo of pet
def test_successful_add_pet_photo(pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что можно добавить фото к существующему питомцу с валидными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, "Рекс", "Кот", 2)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка, получаем код изменяемой картинки и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][0]['id']
    value_image1 = my_pets['pets'][0]['pet_photo']

    print("\nvalue_image1", type(value_image1), value_image1)

    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    # Проверяем что статус ответа = 200 и у питомца появилось (изменилось) фото и отправленное фото
    # равно загруженному на сервер

    assert status == 200
    print('Ответ сервера о фото', result['pet_photo'])
    assert result['pet_photo'] != value_image1


# 6 DELETE /api/pets{pet_id} Delete pet from database
def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Шарик", "собака", "1", "images/104.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа = 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


# 7 PUT /api/pets{pet_id} Update information about pet
def test_successful_update_self_pet_info(name='Лорд', animal_type='Собака', age=7):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


########################################################################################################################
#  Кроме этого еще + 10 тестов

# 1 Проверим, что пользователь с невалидным email не сможет получить auth_key
def test_get_api_key_for_no_valid_user(email=no_valid_email, password=valid_password):
    """ Проверяем что запрос API ключа с невалидным email возвращает статус 403 и
    в результате не содержится слово key """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


# 2 Проверим, что пользователь с невалидным password не сможет получить auth_key
def test_get_api_key_for_no_valid_password(email=valid_email, password=no_valid_email):
    """ Проверяем что запрос API ключа с невалидным email возвращает статус 403 и
    в результате не содержится слово key """

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


# 3 Проверим, что неавторизованный пользователь не может удалить питомца
# В swagger если подставить валидный ID питомца и не валидный auth_key питомец будет удален.
def test_successful_delete_self_pet_no_auth_key():
    """Проверяем возможность удаления питомца не авторизованным пользователем"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Мухтар", "собака", "2", "images/108.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id_1 = my_pets['pets'][0]['id']

    # в запросе на удаление подставляем несуществующий key и снова запрашиваем список питомцев
    status, _ = pf.delete_pet({'key': '75'}, pet_id_1)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id_2 = my_pets['pets'][0]['id']

    # Проверяем что статус ответа равен 403 и питомец не удален
    # В swagger питомец удаляется здесь, возвращается ошибка и это верно.
    assert status == 403
    print('\n #2', type(my_pets.values()), my_pets.values())
    assert pet_id_1 == pet_id_2


# 4 Проверим работу фильтра мои питомцы убедимся в том, что список выдает питомцев
def test_get_my_pets_with_valid_key(filter='my_pets'):
    """ Проверяем что запрос с фильтром мои питомцы возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список питомцев применив filter - 'my_pets' и проверяем что список не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    if len(result['pets']) > 0:

        assert status == 200
        print('len', len(result['pets']), result)
        assert len(['pets']) > 0

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# 5 Проверка, что фото поменялось "PASSED"
def test_successful_changes_pet_photo(pet_photo=f'images/{random.choice(images)}'):
    """Тестируем: Изменение фото питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Лорд", "собака", "4", "images/109.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']  # id питомца (первый в списке)
    image = my_pets['pets'][0]['pet_photo']  # получаем код image изменяемой картинки питомца

    # Добавляем питомца с фото
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    # Если значению кода изменяемой картинки не равно полученному значению кода картинки в ответе - PASSED:
    assert image != result.get('pet_photo')  # - есть ответ от сервера и можно сравнить результаты


# 6 Проверка, что фото имеет недопустимый формат "PASSED"
def test_unsuccessful_changes_pet_photo(pet_photo="images/101.pdf"):
    """Тестируем: Изменение фото питомца, формат файла отличен от JPG, JPEG или PNG."""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Мухтар", "собака", "2", "images/108.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']  # id питомца (первый в списке)
    image = my_pets['pets'][0]['pet_photo']  # получаем код image изменяемой картинки питомца

    # Добавляем питомца с фото
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 500
    # Проверяем что фото не изменилось
    assert image == my_pets['pets'][0]['pet_photo']


# 7 Проверяем, что нет возможности добавить фото к существующему питомцу с невалидным "key"
def test_unsuccessful_add_pet_photo(pet_photo=f'images/{random.choice(images)}'):
    """Проверяем, что нет возможности добавить фото к существующему питомцу с невалидным "key"."""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Кузя", "Кот", "7", pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и получаем код image изменяемой картинки
    pet_id = my_pets['pets'][0]['id']
    image = my_pets['pets'][0]['pet_photo']

    # Отправляем запрос на изменение фото питомца с невалидным "key"
    status, result = pf.add_pet_photo({'key': '75'}, pet_id, pet_photo)

    # Проверяем что статус ответа равен 403 и у питомца не изменилось фото
    assert status == 403
    assert image == my_pets['pets'][0]['pet_photo']


# 8 Проверяем что в поле возраст можно ввести только целые цифры, иначе ошибка
# В swagger присутствует проверка на ввод
def test_add_new_pet_with_no_valid_data(name='Бобр', animal_type='Собакен', age='пять',
                                        pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что в поле возраст можно ввести только цифры"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert isinstance(int(result['age']), int)


# 9 Проверяем что незаполненные обязательные поля не дают возможности добавить питомца
# В swagger присутствует проверка на ввод
def test_add_new_pet_with_no_data(name='', animal_type='', age='',
                                  pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что незаполненные обязательные поля не дают возможности добавить питомца"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    print(result)
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert len(['name']) > 3


# 10 Проверяем что поле ввода имени питомца ограничено 32 символами (видимо нет ограничений!)
def test_add_new_pet_no_data(name=f'Test'*1024, animal_type='Собака', age='1',
                             pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что поле ввода имени питомца ограничено 32 символами"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    print("\n len name", len(result['name']))
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert len(result['name']) < 33
