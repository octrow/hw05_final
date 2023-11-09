
# hw05_final

### Подписки на авторов

Реализована система подписок/отписок на авторов постов.

Стек:

- Python 3.10.5
- Django 3.2
- pytest


### Настройка и запуск

Клонируем проект:

```bash
git clone git@github.com:themasterid/hw05_final.git
```

Переходим в папку с проектом:

```bash
cd hw05_final
```

Устанавливаем виртуальное окружение:

```bash
python -m venv venv
```

Активируем виртуальное окружение:

```bash
source venv/Scripts/activate
```

Устанавливаем зависимости:

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Применяем миграции:

```bash
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Создаем superuser:

```bash
python yatube/manage.py createsuperuser
```

Собираем статику (опционально):

```bash
python yatube/manage.py collectstatic
```

В папку с проектом, где файл settings.py добавляем файл .env куда прописываем наши параметры:

```bash
SECRET_KEY='Ваш секретный ключ'
ALLOWED_HOSTS='127.0.0.1, localhost'
DEBUG=True
```

Добавить в .gitingore файлы:

```bash
.env
.venv
```

Для запуска тестов выполним:

```bash
pytest
```

Запускаем проект:

```bash
python yatube/manage.py runserver
```

После чего проект будет доступен по адресу http://localhost:8000/

Заходим в http://localhost:8000/admin и создаем группы и записи.
После чего записи и группы появятся на главной странице.

Автор: [Daniil Petrov](https://github.com/octrow) :+1:
