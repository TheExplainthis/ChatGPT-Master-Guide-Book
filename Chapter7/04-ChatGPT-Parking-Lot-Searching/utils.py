import numpy as np
import twd97


def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


def query_similarity(q_embedding, c_embedding):
    similarities = []
    for doc_index, doc_embedding in c_embedding.items():
        similarities.append((vector_similarity(q_embedding, doc_embedding), int(doc_index)))
    return sorted(similarities, reverse=True)


def construct_sections(relevants, df):
    chosen_sections = []
    MAX_SECTION_LEN = 1800
    for _, index in relevants:
        if len(''.join(chosen_sections)) > MAX_SECTION_LEN:
            break
        chosen_sections.append(str({
            '地區': df.loc[index]['area'],
            '停車場名稱': df.loc[index]['name'],
            '摘要': df.loc[index]['summary'],
            '地址': df.loc[index]['address'],
            '總車位數': df.loc[index]['totalcar'],
            '空車位數': df.loc[index]['availablecar'],
            '入口': df.loc[index]['EntranceCoord'],
        }))
    return '\n'.join(chosen_sections)


def construct_result(df, names):
    results = []
    for name in names:
        info = df[df['name'] == name]
        tw97x = float(info['tw97x'].values)
        tw97y = float(info['tw97y'].values)
        lat, lon = twd97.towgs84(tw97x, tw97y)
        results.append({
            'name': info['name'].values[0],
            'area': info['area'].values[0],
            'summary': info['summary'].values[0],
            'address': info['address'].values[0],
            'payex': info['payex'].values[0],
            'serviceTime': info['serviceTime'].values[0],
            'lon': lon,
            'lat': lat,
            'availablecar': info['availablecar'].values[0]
        })
    return results
