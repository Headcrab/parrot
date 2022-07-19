tree_menu = {
    1: {
        'Name': 'Бурение ЭРР, всего', 'Kids': {
            2: {
                'Name': 'в т.ч. ОЭР в карьере', 'Kids': {}, 'Data': {6: 'view_prob: в т.ч. ОЭР в карьере', 'p1':'300'}
            },
            3: {
                'Name': 'в т.ч. СЭР в карьере', 'Kids': {}, 'Data': {7: 'view_prob: в т.ч. СЭР в карьере', 'p1':'600'}
            }
        }, 'Data': {}
    },
    4: {
        'Name': 'Программа бурения, всего', 'Kids': {
            5: {
                    'Name': 'Карьер «Северо-западный»', 'Kids': {}, 'Data': {}
            },
            6: {
                'Name': 'карьер «Приречный»', 'Kids': {}, 'Data': {}
            },
            7: {
                'Name': '«Перевод запасов»', 'Kids': {
                    8: {
                        'Name': 'в т.ч. Керновое бурение', 'Kids': {}, 'Data': {
                            44: 'view_prob: в т.ч. Керновое бурение'
                        }
                    },
                    9: {
                        'Name': 'в т.ч. Шламовое бурение', 'Kids': {}, 'Data': {}
                    }
                }, 'Data': {}
            },
            10: {
                'Name': 'Разведочное бурение', 'Kids': {}, 'Data': {}
            }
        }, 'Data': {}
    }
}

def rc_rows(data, i, f, l):
    lk = []
    for key in data:
        # print(i, data[i]['Name'], data[i]['Data'])
        l.append({'id':i+f-1,'Name':data[i]['Name'],'value':''})
        k = i
        i, t = rc_rows(data[key]['Kids'], i+1, f, l)
        l[k-1]['value'] = f'=СУММ({";".join("C"+str(tr+f-1) for tr in t)})' if t else data[k]['Data']['p1'] if 'p1' in data[k]['Data'] else '0'
        lk.append(k)
    return i,lk


class app_rows:
    def run(self):
        i = 1
        f = 0
        l = []
        rc_rows(tree_menu, i, f, l)
        for it in l:
            print(f'{it["id"]}|{it["Name"]}|{it["value"]}')
        print(l)