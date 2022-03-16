## Тесты для сервиса AuthAPI

Тесты работают отдельно от основных сервисов. Для тестирования собирается конейнер AuthAPI из корневой директории проекта.

### Требования:
  - python3 >= 3.8.10
  - [docker-compose](https://docs.docker.com/compose/install/) >= 1.29.2


### Запуск:
1) На примере .env_example создать в директории с тестами файл .env и заполнить его необходимыми данными
2) Запустить docker-compose
  ```
  docker-compose up -d --build
  ```
3) Результаты тестов можно посмотреть командой `docker-compose logs auth-api-tests`
