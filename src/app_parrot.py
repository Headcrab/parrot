from model import *
class app_parrot:
    def __init__(self):
        self.name = "app"
        self.version = "0.0.1"
        self.description = "app"
        self.author = "app"
        self.author_email = ""
    
    def run(self):
        m3 = Model('Модель 3')
        m3.add('Курс валют')
        m3['Курс валют'].add(CurrProperty('Доллар', 'USD'))
        m3['Курс валют'].add(CurrProperty('Евро', 'EUR'))
        m3['Курс валют'].add(CurrProperty('Тенге', 'KZT'))

        m3.add('Кошелек')
        m3['Кошелек'].add(Property('Рублей в кошелке', '10000'))

        m3.add('Обменник')
        m3['Обменник'].add(LinkedProperty('Курс тенге', 'Курс валют.Тенге'))
        m3['Обменник'].add(LinkedProperty('Курс доллара', 'Курс валют.Доллар'))
        m3['Обменник'].add(LinkedProperty('Рублей в кошелке', 'Кошелек.Рублей в кошелке'))
        m3['Обменник'].add(CalculatedProperty('Тенге в кошельке', 'Рублей в кошелке/Курс тенге'))
        m3['Обменник'].add(CalculatedProperty('Долларов в кошельке', 'Рублей в кошелке/Курс доллара'))
        m3.execute()
        m3['Кошелек']['Рублей в кошелке'].value = 666
        m3.execute()
        m3.save(SQLiteSerialiser('base.sqlite','Модель 3'))

        # # m4 = Model('Модель 4')
        # # m4.load(SQLiteSerialiser('base.sqlite','Модель 3'))
        # m4 = SQLiteSerialiser('base.sqlite', 'Модель 3').load()
        # m4.name = 'Модель 4'
        # m4['Курс валют'].add(CurrProperty('Рупия', 'INR'))
        # m4['Обменник'].add(LinkedProperty('Курс рупии', 'Курс валют.Рупия'))
        # m4['Обменник'].add(CalculatedProperty('Рупий в кошельке', 'Рублей в кошелке/Курс рупии'))
        # m4.execute()    