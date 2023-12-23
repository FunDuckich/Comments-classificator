import re
import pymystem3
from nltk.corpus import stopwords
from navec import Navec
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional, Input
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

m = pymystem3.Mystem()

max_comment_len = 12
vector_size = 300
russian_stopwords = stopwords.words("russian")
important_words = ['не', 'и', 'или', 'но']

for word in important_words:
    if word in russian_stopwords:
        russian_stopwords.remove(word)

mlight = Sequential()
mlight.add(Input(shape=(1, max_comment_len * vector_size)))
mlight.add(Bidirectional(LSTM(8,
                              return_sequences=True,
                              dropout=0.8,
                              recurrent_dropout=0.8)))
mlight.add(Bidirectional(LSTM(16,
                              return_sequences=True,
                              dropout=0.8,
                              recurrent_dropout=0.8)))
mlight.add(Bidirectional(LSTM(4,
                              return_sequences=False,
                              dropout=0.8,
                              recurrent_dropout=0.8)))
mlight.add(Dense(1, activation='sigmoid'))


mlight.compile(optimizer='adam',
               loss='binary_crossentropy',
               metrics=['accuracy'])


mlight.load_weights('BiLSTM_light')


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


def vectorize_tokens(tokens, navec, max_len):
    unk = navec['<unk>']
    text_embeddings = []
    for tocken in tokens:
        embedding = navec.get(tocken, unk)
        text_embeddings.append(embedding)
    l_ = len(text_embeddings)
    if l_ > max_len:
        text_embeddings = text_embeddings[:max_len]
    else:
        text_embeddings = [navec['<pad>']] * (max_len - l_) + text_embeddings
    return text_embeddings


def get_result(inp: str) -> int:
    vectors = vectorize_tokens(tokenize(clear_text(inp)), Navec, max_comment_len)
    vectors = vectors.reshape(1, max_comment_len * vector_size)
    vectors = vectors[:, None, :]
    result = mlight.predict(vectors)
    return int(result[0][0] * 100)