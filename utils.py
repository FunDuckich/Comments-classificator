import re
import numpy as np
from keras import models
import pymystem3
from nltk.corpus import stopwords
from navec import Navec
import os


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


m = pymystem3.Mystem()
navec = Navec.load('navec_hudlit_v1_12B_500K_300d_100q.tar')


max_comment_len = 12
vector_size = 300
russian_stopwords = stopwords.words("russian")
important_words = ['не', 'и', 'или', 'но']


for word in important_words:
    if word in russian_stopwords:
        russian_stopwords.remove(word)


mlight = models.load_model('BiLSTM_light')


def clear_text(text: str) -> str:
    cleared_text = re.sub(r'[^А-яЁё]+', ' ', text).lower()
    return ' '.join(cleared_text.split())


def tokenize(text: str) -> list:
    tokens = text.split()
    passed_tokens = []
    for token in tokens:
        if not (token in russian_stopwords):
            passed_tokens.append(token)
    return passed_tokens


def vectorize_tokens(tokens, nav, max_len):
    unk = nav['<unk>']
    text_embeddings = []
    for tocken in tokens:
        embedding = nav.get(tocken, unk)
        text_embeddings.append(embedding)
    l_ = len(text_embeddings)
    if l_ > max_len:
        text_embeddings = text_embeddings[:max_len]
    else:
        text_embeddings = [nav['<pad>']] * (max_len - l_) + text_embeddings
    return text_embeddings


def get_result(inp: str) -> float:
    cleared = clear_text(inp)
    tokens = tokenize(cleared)
    vectors = vectorize_tokens(tokens, navec, max_comment_len)
    vectors = np.array([vectors])
    vectors = vectors.reshape(1, max_comment_len * vector_size)
    vectors = vectors[:, None, :]
    result = mlight.predict(vectors)
    print(result[0][0])
    return result[0][0]