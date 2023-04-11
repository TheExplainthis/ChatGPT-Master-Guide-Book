import numpy as np


def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


def query_similarity(q_embedding, c_embedding):
    document_similarities = sorted([
        (vector_similarity(q_embedding, doc_embedding), int(doc_index)) for doc_index, doc_embedding in c_embedding.items()
    ], reverse=True)

    return document_similarities


def construct_sections(relevants, df):
    chosen_sections = []
    MAX_SECTION_LEN = 1800
    for _, section_index in relevants:
        if len(''.join(chosen_sections)) > MAX_SECTION_LEN:
            break
        cate = df.loc[section_index]['category']
        que = df.loc[section_index]['question']
        ans = df.loc[section_index]['answer']
        chosen_sections.append(f'category title: {cate}\nQ:{que}\nA:{ans}')
    return '\n'.join(chosen_sections)
