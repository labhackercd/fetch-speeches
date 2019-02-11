from collections import Counter
from functools import lru_cache
import unidecode
import pandas as pd
import string
import re

STOPWORDS = [
    'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'nao',
    'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas',
    'ao', 'ele', 'das', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'ja',
    'eu', 'tambem', 'so', 'pelo', 'pela', 'ate', 'isso', 'ela', 'entre',
    'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse',
    'eles', 'voce', 'essa', 'num', 'nem', 'suas', 'meu', 'minha', 'numa',
    'pelos', 'elas', 'qual', 'lhe', 'deles', 'essas', 'esses', 'pelas',
    'este', 'dele', 'tu', 'te', 'voces', 'vos', 'lhes', 'meus', 'minhas',
    'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas',
    'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles',
    'aquelas', 'isto', 'aquilo', 'estou', 'estamos', 'estao', 'estive',
    'esteve', 'estivemos', 'estiveram', 'estava', 'estavamos', 'estavam',
    'estivera', 'estiveramos', 'esteja', 'estejamos', 'estejam', 'estivesse',
    'estivessemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei',
    'ha', 'havemos', 'hao', 'houve', 'houvemos', 'houveram', 'houvera',
    'houveramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvessemos',
    'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houveremos',
    'houverao', 'houveria', 'houveriamos', 'houveriam', 'sou', 'somos',
    'sao', 'era', 'eramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora',
    'foramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fossemos', 'fossem',
    'for', 'formos', 'forem', 'serei', 'sera', 'seremos', 'serao', 'seria',
    'seriamos', 'seriam', 'tenho', 'tem', 'temos', 'tinha', 'tinhamos',
    'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tiveramos',
    'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivessemos', 'tivessem',
    'tiver', 'tivermos', 'tiverem', 'terei', 'tera', 'teremos', 'terao',
    'teria', 'teriamos', 'teriam', 'agora', 'ainda', 'alguem', 'algum',
    'alguma', 'algumas', 'alguns', 'ampla', 'amplas', 'amplo', 'amplos',
    'ante', 'antes', 'apos', 'atraves', 'cada', 'coisa', 'coisas', 'contra',
    'contudo', 'daquele', 'daqueles', 'dessa', 'dessas', 'desse', 'desses',
    'desta', 'destas', 'deste', 'destes', 'deve', 'devem', 'devendo', 'dever',
    'devera', 'deverao', 'deveria', 'deveriam', 'devia', 'deviam', 'disse',
    'disso', 'disto', 'dito', 'diz', 'dizem', 'enquanto', 'fazendo', 'fazer',
    'feita', 'feitas', 'feito', 'feitos', 'grande', 'grandes', 'la', 'lo',
    'mesma', 'mesmas', 'mesmos', 'muita', 'muitas', 'muitos', 'nenhum',
    'nessa', 'nessas', 'nesta', 'nestas', 'ninguem', 'nunca', 'outra',
    'outras', 'outro', 'outros', 'pequena', 'pequenas', 'pequeno', 'pequenos',
    'per', 'perante', 'pode', 'podendo', 'poder', 'poderia', 'poderiam',
    'podia', 'podiam', 'pois', 'porem', 'porque', 'posso', 'pouca', 'poucas',
    'pouco', 'poucos', 'primeiro', 'primeiros', 'propria', 'proprias',
    'proprio', 'proprios', 'quais', 'quanto', 'quantos', 'sempre', 'sendo',
    'si', 'sido', 'sob', 'sobre', 'talvez', 'tampouco', 'tendo', 'ter', 'ti',
    'tido', 'toda', 'todas', 'todavia', 'todo', 'todos', 'tudo', 'ultima',
    'ultimas', 'ultimo', 'ultimos', 'umas', 'uns', 'vendo', 'ver', 'vez',
    'vindo', 'vir', 'ah', 'ai', 'algo', 'alo', 'ambos', 'apenas', 'bis',
    'certa', 'certas', 'certo', 'certos', 'chi', 'comigo', 'conforme',
    'conosco', 'consigo', 'contigo', 'convosco', 'cuja', 'cujas', 'cujo',
    'cujos', 'desde', 'daquela', 'daquelas', 'daquilo', 'eia', 'embora',
    'hem', 'hum', 'ih', 'logo', 'menos', 'mim', 'nada', 'nela', 'nelas',
    'nele', 'neles', 'nenhuma', 'nenhumas', 'nenhuns', 'nesse', 'nesses',
    'nisso', 'neste', 'nestes', 'nisto', 'naquela', 'naquelas', 'naquele',
    'naqueles', 'naquilo', 'oba', 'oh', 'ola', 'onde', 'opa', 'ora', 'outrem',
    'portanto', 'psit', 'psiu', 'quaisquer', 'qualquer', 'quanta', 'quantas',
    'tanta', 'tantas', 'tanto', 'tantos', 'tras', 'ue', 'uh', 'ui', 'varia',
    'varias', 'vario', 'varios', 'vossa', 'vossas', 'vosso', 'vossos',
]

TOKENS = Counter()


def clear_speech(text):
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'[OA] SRA?[\w\s.]+-', '', text)
    text = re.sub(r'PRONUNCIAMENTO[\sA-Z]+\s', '', text)
    text = re.sub(r'\s[\.\"]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[Vv]\.[Ee][Xx][Aa]\.', 'v.exa', text)
    text = re.sub(r'[Aa][Rr][Tt]\.', 'art', text)
    text = re.sub(r'[Ss][Rr][Ss]?\.', 'sr', text)
    text = re.sub(r'[Ss][Rr][Aa][Ss]?\.', 'sr', text)
    text = re.sub(r'\d', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    text = unidecode.unidecode(text)
    text = text.lower().strip()

    TOKENS.update(set(tokenize_speech(text)))

    return text


@lru_cache()
def tokenize_speech(text):
    tokens = text.split()
    return tokens


def tokens_to_string(tokens):
    return ','.join([token for token in tokens if token not in set(STOPWORDS)])


def update_stopwords(num_documents):
    for token, occurr in TOKENS.most_common():
        if occurr >= num_documents * 0.99 or occurr <= num_documents * 0.01:
            STOPWORDS.append(token)


def load_speeches():
    speeches_df = pd.read_csv('speeches.csv')
    speeches_df['speech'] = speeches_df['speech'].apply(clear_speech)
    update_stopwords(speeches_df.shape[0])
    speeches_df['tokens'] = speeches_df['speech'].apply(lambda x: tokens_to_string(tokenize_speech(x)))
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    load_speeches()