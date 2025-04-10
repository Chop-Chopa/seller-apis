# Скрипты для обновления остатков и цен на Ozon и Яндекс.Марке
Этот репозиторий содержит два скрипта, которые предназначены для автоматического обновления информации о товарах на платформе Ozon и Яндекс.Маркет. Эти скрипты позволяют синхронизировать данные о наличии товаров и их стоимости, минимизируя ручной труд и возможные ошибки.

## Скрипт для Ozon - `seller.py`
Этот скрипт помогает поддерживать в магазине на Ozon актуальную информацию о наличии и стоимости товаров CASIO.

### Как работает скрипт?
1. Получение данных о товарах. Скрипт скачивает файл с остатками товаров CASIO с официального источника. Этот файл содержит актуальные данные о количестве товаров и их ценах.
2. Проверка загруженных товаров. Скрипт проверяет, какие товары уже присутствуют в магазине на Ozon, и добавляет новые или удаляет те, которых нет в наличии.
3. Обновление остатков и цен. После синхронизации, скрипт обновляет остатки (сколько единиц товара в наличии) и цены в вашем магазине на Ozon, используя данные из файла CASIO.
4. Автоматическая обработка больших объемов данных. Все операции выполняются автоматически, данные отправляются порциями, чтобы избежать перегрузки.

### Что нужно для работы?
Для корректной работы скрипта нужно указать два параметра: ID клиента Ozon, токен продавца Ozon.

Эти параметры можно получить в вашем личном кабинете на Ozon
