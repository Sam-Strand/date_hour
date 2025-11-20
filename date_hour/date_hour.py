from datetime import datetime, timedelta
from typing import Union
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler


class DateHour(str):
    '''Класс для работы с временными метками с границами периодов.'''
    
    _formats = {
        '%Y-%m-%d %H:%M:%S': 'hour',  # секунды
        '%Y-%m-%d %H:%M': 'hour',     # минуты  
        '%Y-%m-%d %H': 'hour',        # Час
        '%Y-%m-%d': 'day',            # День
        '%Y-%m': 'month',             # Месяц
        '%Y': 'year',                 # Год
    }

    def __new__(cls, value: Union[str, datetime]) -> 'DateHour':
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        
        if not isinstance(value, str):
            raise ValueError(f'Ожидалась строка, получен {type(value)}: {value}')
        
        dt, format_type = cls._parse_string(value)
        
        normalized_dt = dt.replace(minute=0, second=0, microsecond=0)
        normalized_str = normalized_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        instance = super().__new__(cls, normalized_str)
        instance._format_type = format_type
        return instance

    @classmethod
    def _parse_string(cls, value: str) -> tuple[datetime, str]:
        '''Парсит строку в datetime и возвращает тип формата.'''
        errors = []
        
        for fmt, format_type in cls._formats.items():
            try:
                dt = datetime.strptime(value, fmt)
                return dt, format_type
            except ValueError as e:
                errors.append(f"{fmt}: {e}")
                continue
        
        # Если ни один формат не подошел
        supported_formats = "\n  - ".join(cls._formats.keys())
        raise ValueError(
            f'Не удалось распарсить дату: "{value}".\n'
            f'Поддерживаемые форматы:\n  - {supported_formats}'
        )

    def _get_datetime(self) -> datetime:
        '''Возвращает datetime объект из строки.'''
        return datetime.strptime(self, '%Y-%m-%d %H:%M:%S')

    def _get_start_datetime(self) -> datetime:
        '''Возвращает начало периода.'''
        dt = self._get_datetime()
        
        if self._format_type == 'year':
            return dt.replace(month=1, day=1, hour=0)
        elif self._format_type == 'month':
            return dt.replace(day=1, hour=0)
        elif self._format_type == 'day':
            return dt.replace(hour=0)
        else:  # hour
            return dt  # Уже нормализовано до начала часа

    def _get_stop_datetime(self) -> datetime:
        '''Возвращает конец периода.'''
        dt = self._get_datetime()
        
        if self._format_type == 'year':
            # Конец года: 31 декабря 23:00:00
            return dt.replace(month=12, day=31, hour=23)
        elif self._format_type == 'month':
            # Конец месяца: последний день 23:00:00
            if dt.month == 12:
                next_month = dt.replace(year=dt.year + 1, month=1, day=1)
            else:
                next_month = dt.replace(month=dt.month + 1, day=1)
            last_day = next_month - timedelta(days=1)
            return last_day.replace(hour=23)
        elif self._format_type == 'day':
            # Конец дня: 23:00:00
            return dt.replace(hour=23)
        else:  # hour
            # Для часа: тот же час
            return dt

    @property
    def start(self) -> str:
        '''Начало периода в формате YYYY-MM-DD HH:MM:SS.'''
        return self._get_start_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def stop(self) -> str:
        '''Конец периода в формате YYYY-MM-DD HH:MM:SS.'''
        return self._get_stop_datetime().strftime('%Y-%m-%d %H:%M:%S')

    def __sub__(self, hours: int) -> 'DateHour':
        '''Вычитает указанное количество часов от начала периода.'''
        start_dt = self._get_start_datetime()
        new_dt = start_dt - timedelta(hours=hours)
        return DateHour(new_dt)

    def __add__(self, hours: int) -> 'DateHour':
        '''Добавляет указанное количество часов к началу периода.'''
        start_dt = self._get_start_datetime()
        new_dt = start_dt + timedelta(hours=hours)
        return DateHour(new_dt)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        source: type, 
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: Union[str, datetime]) -> 'DateHour':
            if isinstance(value, cls):
                return value
            return cls(value)
            
        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )


if __name__ == '__main__':
    print("=== Тестирование DateHour с определением типа при парсинге ===")
    
    # Тест 1: Разные форматы
    test_cases = [
        "2024",              # Год
        "2024-01",           # Месяц
        "2024-01-15",        # День
        "2024-01-15 14",     # Час
        "2024-01-15 14:30",  # Время с минутами
        "2024-01-15 14:30:45", # Полное время
        datetime(2024, 1, 15, 14, 30, 45),  # datetime объект
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            dh = DateHour(case)
            print(f"{i}. {case!r:25} -> {dh!r:25} | тип: {dh._format_type:6} | start: {dh.start:19} | stop: {dh.stop:19}")
        except Exception as e:
            print(f"{i}. {case!r:25} -> ОШИБКА: {e}")

    print("\n=== Арифметические операции ===")
    dh = DateHour("2024-01-15 14:30:00")
    print(f"Исходный: {dh} -> start: {dh.start}")
    print(f"+2 часа:  {(dh + 2)} -> start: {(dh + 2).start}")
    print(f"-3 часа:  {(dh - 3)} -> start: {(dh - 3).start}")

    print("\n=== Проверка границ периодов ===")
    print(f"Год 2024:       {DateHour('2024').start} - {DateHour('2024').stop}")
    print(f"Месяц 2024-01:  {DateHour('2024-01').start} - {DateHour('2024-01').stop}")
    print(f"День 2024-01-15: {DateHour('2024-01-15').start} - {DateHour('2024-01-15').stop}")
    print(f"Час 2024-01-15 14: {DateHour('2024-01-15 14').start} - {DateHour('2024-01-15 14').stop}")