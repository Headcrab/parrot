import pickle
import sqlite3
import requests

class Object:
    pass


class Model:
    pass


class LinkedProperty:
    pass


class ModelSerialiser:
    def save(self, model: Model) -> None:
        pass
    def load(self) -> Model:
        pass


class SQLiteSerialiser (ModelSerialiser):
    file_name: str
    model_name: str

    def __init__(self, file_name:str, model_name:str=''):
        self.file_name = file_name
        self.model_name = model_name

    def save(self, model: Model) -> None:
        mod_name = self.model_name if not self.model_name == '' else model.name
        with sqlite3.connect(self.file_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM models WHERE name='{mod_name}'")
            model_id = cursor.fetchone()
            if model_id is None:
                cursor.execute(
                    f"INSERT INTO models (name) VALUES ('{mod_name}')")
                model_id = cursor.lastrowid
            else:
                model_id = model_id[0]
            for nm, i in model.items():
                cursor.execute(
                    f"SELECT * FROM objects WHERE name='{nm}' AND model_id={model_id}")
                object_id = cursor.fetchone()
                if object_id is None:
                    cursor.execute(
                        f"INSERT INTO objects (name, model_id) VALUES ('{nm}', {model_id})")
                    object_id = cursor.lastrowid
                else:
                    object_id = object_id[0]
                for nm2, k in i.items():
                    cursor.execute(
                        f"SELECT * FROM properties WHERE name='{nm2}' AND object_id={object_id}")
                    property_id = cursor.fetchone()
                    if property_id is None:
                        cursor.execute(
                            f"INSERT INTO properties (name, object_id, value, type) VALUES ('{nm2}', {object_id}, '{k.real_value}', '{k.__class__.__name__}')")
                    else:
                        cursor.execute(
                            f"UPDATE properties SET value='{k.real_value}' WHERE id={property_id[0]}")

    def load(self) -> Model:
        with sqlite3.connect(self.file_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM models WHERE name='{self.model_name}'")
            model = cursor.fetchone()
            cursor.execute(f"SELECT * FROM objects WHERE model_id={model[0]}")
            objects = cursor.fetchall()
            model = Model(model[1])
            for i in objects:
                cursor.execute(f"SELECT * FROM properties WHERE object_id={i[0]}")
                properties = cursor.fetchall()
                model[i[1]] = Object(i[1])
                model[i[1]].model = model
                for k in properties:
                    model[i[1]][k[1]] = eval(k[2])(k[1], k[3])
                    model[i[1]][k[1]].object = model[i[1]]
        return model


class BJsonSerialiser (ModelSerialiser):
    file_name: str
    def __init__(self, name:str):
        self.file_name = name
    def save(self, model: Model) -> None:
        with open(self.file_name, 'wb') as f:
            pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)

    def load(self) -> Model:
        with open(self.file_name, 'rb') as f:
            model = pickle.load(f)
        return model
    

class Property:
    name: str
    __val: str
    object: Object

    def __init__(self, name: str = 'нонейм', value: str = '0.0'):
        self.name = name
        self.value = value
        self.object = None

    @property
    def real_value(self):
        return self.__val

    @property
    def value(self):
        return self.__val

    @value.setter
    def value(self, val):
        self.__val = val

    def execute(self):
        v = self.value
        try:
            v = str(round(float(v), 4))
        except:
            pass
        print(f'  {self.name} = {v}')


class Object(dict[Property]):
    name: str
    model: Model

    def __init__(self, name: str = 'нонейм'):
        self.name = name
        self.model = None

    def add(self, value: Property) -> Property:
        self[value.name] = value
        value.object = self
        return self[value.name]

    def execute(self) -> None:
        print(f' {self.name}')
        for _, value in self.items():
            value.execute()


class Model(dict[str, Object]):
    name: str

    def __init__(self, name: str = 'нонейм'):
        self.name = name

    def add(self, name: str) -> Object:
        self[name] = Object(name)
        self[name].model = self
        return self[name]

    def execute(self) -> None:
        print(f'\n{self.name}')
        for _, value in self.items():
            value.execute()

    def save(self, serialiser:ModelSerialiser):
        serialiser.save(self)

    # def load(self, serialiser:ModelSerialiser): 
    #     self = serialiser.load()
    # TODO: так не работает, разобраться
    # FIXME: не работает, разобраться
    # BUG: не работает, разобраться
    # HACK: не работает, разобраться
    
class LinkedProperty(Property):
    link: str

    def __init__(self, name: str = 'нонейм', link: str = '', value: str = '0.0'):
        super().__init__(name, value)
        self.link = link

    @property
    def real_value(self):
        return self.link

    def execute(self) -> None:
        self.value = 0
        for i in self.link.split(','):
            try:
                self.value = float(
                    self.value)+float(self.object.model[i.split('.')[0]][i.split('.')[1]].value)
            except:
                self.value += f"+{self.object.model[i.split('.')[0]][i.split('.')[1]].value}"
        super().execute()


class CalculatedProperty(Property):
    formula: str

    def __init__(self, name: str = 'нонейм', formula: str = '', value: float = 0.0) -> None:
        super().__init__(name, value)
        self.formula = formula

    @property
    def real_value(self):
        return self.formula

    def execute(self) -> None:
        frm = self.formula
        for i in self.object:
            frm = frm.replace(i, str(self.object[i].value))
        try:
            self.value = eval(frm)
        except Exception as e:
            print(f'  {self.name} = Ошибка в формуле "{self.formula}" - {e}')
            self.value = '0.0'
        else:
            super().execute()

class URLSingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class URLSingleton(metaclass=URLSingletonMeta):
    data = {}
    def get(self):
        if(len(self.data) == 0):
            try:
                self.data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
            except Exception as e:
                pass
        return self.data

class CurrProperty(Property):
    charCode: str
    def __init__(self, name: str = 'нонейм', charCode: str = '', value: float = 0.0) -> None:
        super().__init__(name, value)
        self.charCode = charCode
    
    @property
    def real_value(self):
        return self.charCode

    def execute(self) -> None:
        data = URLSingleton().get()
        self.value = data['Valute'][self.charCode]['Value']/data['Valute'][self.charCode]['Nominal'] if len(data)>0 else '0.0'
        super().execute()

