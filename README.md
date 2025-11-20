# DateHour

Python библиотека для работы с унифицированной датой и временем фиксированного шага (час).

## Особенности
- **Интеграция с Pydantic** - Полная поддержка валидации в Pydantic моделях
- **Простота использования** - Интуитивно понятный API

## Установка
### Способ 1: Установка из репозитория (требуется Git)
```bash
pip install git+https://github.com/Sam-Strand/date_hour.git
```

### Способ 2: Установка готового пакета (без Git)
```bash
pip install https://github.com/Sam-Strand/date_hour/releases/download/v1.0.0/date_hour-1.0.0-py3-none-any.whl
```

## Быстрый старт
```python
from date_hour import DateHour
from date_hour import TimeRange
from datetime import datetime

date = DateHour("2024")

year = TimeRange(date)
print(f"   Год: {year}")

month = TimeRange("2024-01") 
print(f"   Месяц: {month}")

day = TimeRange("2024-01-15")
print(f"   День: {day}")

hour = TimeRange("2024-01-15 14")
print(f"   Час: {hour}")
print("\n2. Произвольные диапазоны:")
custom = TimeRange("2024-01-01", "2024-01-15 14:30:00")
print(f"   Диапазон: {custom}")
print("\n3. Арифметические операции:")
current = TimeRange("2024-01-15 10:00:00", "2024-01-15 14:00:00")
print(f"   Исходный: {current}")
print(f"   Начало -2ч: {current.start - 2}")
print(f"   Конец +3ч: {current.stop + 3}")
```
