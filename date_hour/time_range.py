from datetime import datetime
from typing import Union
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler
from date_hour import DateHour

class TimeRange:
    '''
    Универсальный класс для работы с временными диапазонами на основе DateHour.
    '''

    def __init__(self, start: Union[str, datetime, 'DateHour'],
                 stop: Union[str, datetime, 'DateHour'] = None):
        '''
        Инициализирует временной диапазон.
        
        Args:
            start: Начало диапазона или самодостаточный период
            stop: Конец диапазона (опционально)
        '''
        self.start = DateHour(start)
        if stop is None:
            self.stop = DateHour(self.start.stop)
        else:
            self.stop = DateHour(stop)

    def __str__(self) -> str:
        return f"TimeRange({self.start} - {self.stop})"

    def __len__(self) -> int:
        '''
        Возвращает количество часов в диапазоне
        '''
        start_dt = self.start._get_datetime()
        stop_dt = self.stop._get_datetime()
        
        hours_diff = int((stop_dt - start_dt).total_seconds() / 3600) + 1
        return hours_diff


    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source: type,
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate(value) -> 'TimeRange':
            if isinstance(value, cls):
                return value
            return cls(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda v: {
                'start': v.start_str,
                'stop': v.stop_str
            })
        )


# Тестирование
if __name__ == '__main__':
    print("1. Самодостаточные периоды:")
    
    year = TimeRange("2024")
    print(f"   Год: {year} | Кол-во часов: {len(year)}")
    
    month = TimeRange("2024-01") 
    print(f"   Месяц: {month} | Кол-во часов: {len(month)}")
    
    day = TimeRange("2024-01-15")
    print(f"   День: {day} | Кол-во часов: {len(day)}")
    
    hour = TimeRange("2024-01-15 14")
    print(f"   Час: {hour} | Кол-во часов: {len(hour)}")

    print("\n2. Произвольные диапазоны:")
    custom = TimeRange("2024-01-01", "2024-01-15 14:30:00")
    print(f"   Диапазон: {custom}")

    print("\n3. Арифметические операции:")
    current = TimeRange("2024-01-15 10:00:00", "2024-01-15 14:00:00")
    print(f"   Исходный: {current}")
    print(f"   Начало -2ч: {current.start - 2}")
    print(f"   Конец +3ч: {current.stop + 3}")
