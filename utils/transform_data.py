def dict_data(qs, attr):
    dict = {}
    for q in qs:
        dict[q.__getattribute__(attr)] = q.rate
    return dict

def prepare_data(qs,dict,attr,default, name):
    data = []
    for q in qs:
        d = q.__getattribute__(attr)
        rate = dict.get(d.id, default)
        data.append({name: d, 'rate': rate})
    return data