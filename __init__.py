from ast import Mod
from copy import copy, deepcopy
from json import load
import pickle
import random
import sqlite3
import sys
import timeit


class Object:
    pass


class Model:
    pass


class LinkedProperty:
    pass


def draw_text_in_box(f: object, text: str, x: int, y: int, width: int, height: int, color: str) -> None:
    f.write(
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" style="fill:{color};stroke:black;stroke-width:1"/>\n')
    f.write(
        f'<text x="{x + width / 2}" y="{y + height / 2+5}" text-anchor="middle">{text}</text>\n')


def make_svg_from_model(model: Model, file_name: str) -> None:
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg"\n'
                '    xmlns:xlink="http://www.w3.org/1999/xlink"\n'
                '    width="1000px"\n'
                '    height="1000px">\n')
        item_width = 1000 / len(model)-20
        item_number = 0
        for key, value in model.items():
            box_color = '#ccc'
            draw_text_in_box(f, key, item_number * item_width +
                             10, 10, item_width-10, 50, box_color)
            property_number = 0
            for key2, value2 in value.items():
                box_color = '#cbb'
                val = value2.value
                try:
                    val = str(round(float(value2.value), 4))
                except:
                    pass
                draw_text_in_box(f, f'{key2} = {val}', item_number *
                                 item_width+10, property_number * 50 + 60, item_width-10, 50, box_color)
                property_number += 1
            item_number += 1
        f.write('</svg>\n')


# def load_model_from_sqlite(file_name: str, model_name: str) -> Model:
#     with sqlite3.connect(file_name) as conn:
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT * FROM models WHERE name='{model_name}'")
#         model = cursor.fetchone()
#         cursor.execute(f"SELECT * FROM objects WHERE model_id={model[0]}")
#         objects = cursor.fetchall()
#         model = Model(model[1])
#         for i in objects:
#             cursor.execute(f"SELECT * FROM properties WHERE object_id={i[0]}")
#             properties = cursor.fetchall()
#             model[i[1]] = Object(i[1])
#             model[i[1]].model = model
#             for k in properties:
#                 model[i[1]][k[1]] = eval(k[2])(k[1], k[3])
#                 model[i[1]][k[1]].object = model[i[1]]

#     return model


# def save_model_to_sqlite(model: Model, file_name: str) -> None:
#     with sqlite3.connect(file_name) as conn:
#         cursor = conn.cursor()
#         cursor.execute(f"SELECT * FROM models WHERE name='{model.name}'")
#         model_id = cursor.fetchone()
#         if model_id is None:
#             cursor.execute(
#                 f"INSERT INTO models (name) VALUES ('{model.name}')")
#             model_id = cursor.lastrowid
#         else:
#             model_id = model_id[0]
#         for nm, i in model.items():
#             cursor.execute(
#                 f"SELECT * FROM objects WHERE name='{nm}' AND model_id={model_id}")
#             object_id = cursor.fetchone()
#             if object_id is None:
#                 cursor.execute(
#                     f"INSERT INTO objects (name, model_id) VALUES ('{nm}', {model_id})")
#                 object_id = cursor.lastrowid
#             else:
#                 object_id = object_id[0]
#             for nm2, k in i.items():
#                 cursor.execute(
#                     f"SELECT * FROM properties WHERE name='{nm2}' AND object_id={object_id}")
#                 property_id = cursor.fetchone()
#                 if property_id is None:
#                     cursor.execute(
#                         f"INSERT INTO properties (name, object_id, value, type) VALUES ('{nm2}', {object_id}, '{k.real_value}', '{k.__class__.__name__}')")
#                 else:
#                     cursor.execute(
#                         f"UPDATE properties SET value='{k.real_value}' WHERE id={property_id[0]}")


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
        # self.object.execute()

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
        for key, value in self.items():
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

    # def save(self, file_name: str) -> None:
    #     with open(file_name, 'wb') as f:
    #         pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    # def load(self, file_name: str) -> Model:
    #     with open(file_name, 'rb') as f:
    #         self = pickle.load(f)
    #     return self


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


# m3 = Model('Продажа мяса')
# m3.add('Курс валют')
# m3['Курс валют'].add(Property('Рубль', '1.0'))
# m3['Курс валют'].add(Property('Доллар', '0.0092'))
# m3['Курс валют'].add(Property('Евро', '0.0082'))
# m3['Курс валют'].add(Property('Тенге', '5.23'))

# m3.add('Кошелек')
# m3['Кошелек'].add(Property('Бабки', '10000'))

# m3.add('Мясо')
# m3['Мясо'].add(Property('Валюта', 'Доллар'))
# m3['Мясо'].add(Property('Кол-во', '10'))
# m3['Мясо'].add(Property('Цена', '243'))
# m3['Мясо'].add(LinkedProperty('Доллар', 'Курс валют.Доллар,Курс валют.Евро,Курс валют.Тенге'))
# m3['Мясо'].add(LinkedProperty('Рубль', 'Курс валют.Рубль'))
# m3['Мясо'].add(LinkedProperty('Тенге', 'Курс валют.Тенге'))
# m3['Мясо'].add(LinkedProperty('В кошелке', 'Кошелек.Бабки'))
# m3['Мясо'].add(CalculatedProperty('Сумма', 'Кол-во*Цена*Валюта'))
# m3['Мясо'].add(CalculatedProperty('Алярм', '"Нет денег" if Сумма>10000 else "Бабла полно"'))

# o4 = m3['Мясо']
# o4 = deepcopy(o4)
# o4.name = 'Мясо гов.'
# print (o4.name)
# print (m3['Мясо'].name)


# m3['Мясо']['Валюта'].value = 'Тенге'
# m3['Мясо']['Кол-во'].value = '10'
# m3.execute()
# m3['Мясо']['Кол-во'].value = '5'
# m3.execute()
# make_svg_from_model(m3, 'new_model.svg')

# save_model_to_sqlite(m3, 'base.sqlite')

m4 = SQLiteSerialiser('base.sqlite', 'Продажа мяса').load()
m4.name = 'Продажа мяса гов.'
m4.execute()
m4['Мясо']['Кол-во'].value = '66'
m4.execute()
m5 = deepcopy(m4)
m5.name = 'Продажа мяса гов. копия'
m5.execute()
BJsonSerialiser('model5.pkl').save(m5)
# save_model_to_sqlite(m4, 'base.sqlite')

