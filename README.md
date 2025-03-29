## Реализованы следующе методы для объявлений:
 - Создание: `POST /advertisement`
 - Обновление: `PATCH /advertisement/{advertisement_id}`
 - Удаление: `DELETE /advertisement/{advertisement_id}`
 - Получение по id: `GET  /advertisement/{advertisement_id}`
 - Поиск по полям: `GET /advertisement?{query_string}`

## Добавлены роуты для управления пользователями:
 - POST /login, который возвращает токен для авторизации. Срок действия токена - 48 часов
 - Создание: `POST /user`
 - Обновление: `PATCH /user/{user_id}`
 - Удаление: `DELETE /user/{user_id}`
 - Получение по id: `GET  /user/{user_id}`

## Пользователи принадлежат одной из следующих групп: user, admin

### Права неавторизованного пользователя (клиент может токен не передавать):
- Создание пользователя `POST /user`
- Получение пользователя по id `GET /user/{user_id}`
- Получение объявления по id  `GET /advertisement/{advertisement_id}`
- Поиск объявления по полям `GET /advertisement?{query_string}`

### Права авторизованного пользователя с группой user:
- все права неавторизованного пользователя
- обновление своих данных `PATCH /user/{user_id}`
- удаление себя `DELETE /user/{user_id}`
- создание объявления  `POST /advertisement`
- обновление своего объявления `PATCH /advertisement/{advertisement_id}`
- удаление своего объявления `DELETE /advertisement/{advertisement_id}`

### Права авторизованного пользователя с группой admin:
- любые действия с любыми сущностям

Если у пользователя недостаточно прав для выполнения операции, то возвращается ошибка 403
   
## Запуск приложения
docker-compose up --build
