import re
from datetime import datetime, timedelta
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

class DateHour(str):
    '''Класс для работы с временными метками с границами периодов.'''
    
    patterns = [
        (re.compile(r'^\d{4}$'), '%Y'),                          # 2024
        (re.compile(r'^\d{4}-\d{2}$'), '%Y-%m'),                # 2024-01
        (re.compile(r'^\d{4}-\d{2}-\d{2}$'), '%Y-%m-%d'),       # 2024-01-15
        (re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}$'), '%Y-%m-%d %H'),  # 2024-01-15 14
        (re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'), '%Y-%m-%d %H:%M:%S'),  # 2024-01-15 14:59:59
    ]

    def __new__(cls, value: str | datetime) -> 'DateHour':
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        if not isinstance(value, str):
            raise ValueError(f'Ожидалась строка, получен {type(value)}: {value}')
        
        matched_format = None
        for pattern, date_format in cls.patterns:
            if pattern.fullmatch(value):
                matched_format = date_format
                break
        
        if not matched_format:
            raise ValueError(
                f'Некорректный формат даты: "{value}". '
                f'Поддерживаемые форматы: "YYYY", "YYYY-MM", "YYYY-MM-DD", "YYYY-MM-DD HH", "YYYY-MM-DD HH:MM:SS"'
            )
        
        try:
            value = datetime.strptime(value, matched_format).replace(minute=0, second=0, microsecond=0)
        except ValueError as e:
            raise ValueError(f'Неверная дата/время: {e}')
            
        return super().__new__(cls, value)

    def _get_start_datetime(self) -> datetime:
        '''Возвращает начало периода'''
        for pattern, date_format in self.patterns:
            if pattern.fullmatch(self):
                dt = datetime.strptime(self, date_format)
                format_type = self._get_format_type()
                
                if format_type == 'year':
                    return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                elif format_type == 'month':
                    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                elif format_type == 'day':
                    return dt.replace(hour=0, minute=0, second=0, microsecond=0)
                elif format_type == 'hour':
                    return dt.replace(minute=0, second=0, microsecond=0)
                elif format_type == 'full':
                    return dt.replace(minute=0, second=0, microsecond=0)
        raise ValueError(f'Не удалось распарсить дату: {self}')

    def _get_stop_datetime(self) -> datetime:
        '''Возвращает конец периода'''
        for pattern, date_format in self.patterns:
            if pattern.fullmatch(self):
                dt = datetime.strptime(self, date_format)
                format_type = self._get_format_type()
                
                if format_type == 'year':
                    # Конец года: 31 декабря 23:00:00
                    return dt.replace(month=12, day=31, hour=23, minute=0, second=0, microsecond=0)
                elif format_type == 'month':
                    # Конец месяца: последний день 23:00:00
                    if dt.month == 12:
                        next_month = dt.replace(year=dt.year + 1, month=1, day=1)
                    else:
                        next_month = dt.replace(month=dt.month + 1, day=1)
                    last_day = next_month - timedelta(days=1)
                    return last_day.replace(hour=23, minute=0, second=0, microsecond=0)
                elif format_type == 'day':
                    # Конец дня: 23:00:00
                    return dt.replace(hour=23, minute=0, second=0, microsecond=0)
                elif format_type == 'hour':
                    # Для часа: тот же час
                    return dt.replace(minute=0, second=0, microsecond=0)
                elif format_type == 'full':
                    # Для полного времени: нормализуем до часа
                    return dt.replace(minute=0, second=0, microsecond=0)
        raise ValueError(f'Не удалось распарсить дату: {self}')

    def _get_format_type(self) -> str:
        '''Возвращает тип формата'''
        if re.fullmatch(r'^\d{4}$', self):
            return 'year'
        elif re.fullmatch(r'^\d{4}-\d{2}$', self):
            return 'month'
        elif re.fullmatch(r'^\d{4}-\d{2}-\d{2}$', self):
            return 'day'
        elif re.fullmatch(r'^\d{4}-\d{2}-\d{2} \d{2}$', self):
            return 'hour'
        elif re.fullmatch(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', self):
            return 'full'
        else:
            raise ValueError(f'Неизвестный формат: {self}')

    @property
    def start(self) -> str:
        '''Начало периода в формате YYYY-MM-DD HH:MM:SS'''
        return self._get_start_datetime().strftime('%Y-%m-%d %H:%M:%S')

    @property
    def stop(self) -> str:
        '''Конец периода в формате YYYY-MM-DD HH:MM:SS'''
        return self._get_stop_datetime().strftime('%Y-%m-%d %H:%M:%S')

    def __sub__(self, hours: int) -> 'DateHour':
        '''Вычитает указанное количество часов от начала периода'''
        start_dt = self._get_start_datetime()
        new_dt = start_dt - timedelta(hours=hours)
        return DateHour(new_dt.strftime('%Y-%m-%d %H:%M:%S'))

    def __add__(self, hours: int) -> 'DateHour':
        '''Добавляет указанное количество часов к началу периода'''
        start_dt = self._get_start_datetime()
        new_dt = start_dt + timedelta(hours=hours)
        return DateHour(new_dt.strftime('%Y-%m-%d %H:%M:%S'))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        source: type, 
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value: str) -> 'DateHour':
            if isinstance(value, cls):
                return value
            return cls(value)
            
        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda v: str(v))
        )


if __name__ == '__main__':
    # Тест 1: Год
    dh1 = DateHour("2024")
    print(f"DateHour('2024').start = {dh1.start}")  # 2024-01-01 00:00:00
    print(f"DateHour('2024').stop = {dh1.stop}")    # 2024-12-31 23:00:00
    print(f"DateHour('2024') - 1 = {(dh1 - 1).start}")  # 2023-12-31 23:00:00

    print()

    # Тест 2: Месяц
    dh2 = DateHour("2024-01")
    print(f"DateHour('2024-01').start = {dh2.start}")  # 2024-01-01 00:00:00
    print(f"DateHour('2024-01').stop = {dh2.stop}")    # 2024-01-31 23:00:00

    print()

    # Тест 3: День
    dh3 = DateHour("2024-01-15")
    print(f"DateHour('2024-01-15').start = {dh3.start}")  # 2024-01-15 00:00:00
    print(f"DateHour('2024-01-15').stop = {dh3.stop}")    # 2024-01-15 23:00:00

    print()

    # Тест 4: Час
    dh4 = DateHour("2024-01-15 14")
    print(f"DateHour('2024-01-15 14').start = {dh4.start}")  # 2024-01-15 14:00:00
    print(f"DateHour('2024-01-15 14').stop = {dh4.stop}")    # 2024-01-15 14:00:00

    print()

    # Тест 5: Полное время (нормализуется до часа)
    dh5 = DateHour("2024-01-15 14:59:59")
    print(f"DateHour('2024-01-15 14:59:59').start = {dh5.start}")  # 2024-01-15 14:00:00
    print(f"DateHour('2024-01-15 14:59:59').stop = {dh5.stop}")    # 2024-01-15 14:00:00
