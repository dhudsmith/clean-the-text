import regex as re
from typing import Union, Optional
from io import StringIO
from html.parser import HTMLParser
from emoji import UNICODE_EMOJI


nltk_stopwords = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                  "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
                  "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
                  "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                  "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as",
                  "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
                  "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
                  "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how",
                  "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
                  "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
                  "now", "could", "rt"}


# convert common contractions
def expand_contractions(txt: str):
    """
    Expand common contractions
    """
    # specific
    txt = re.sub(r"won\'t", "will not", txt)
    txt = re.sub(r"Won\'t", "Will not", txt)
    txt = re.sub(r"can\'t", "can not", txt)
    txt = re.sub(r"Can\'t", "Can not", txt)
    txt = re.sub(r"cant", "can not", txt)
    txt = re.sub(r"wont", "will not", txt)

    # general
    txt = re.sub(r"n\'t", " not", txt)
    txt = re.sub(r"\'re", " are", txt)
    txt = re.sub(r"â€™s", " is", txt)  # funny apostrophe
    txt = re.sub(r"\'s", " is", txt)
    txt = re.sub(r"\'d", " would", txt)
    txt = re.sub(r"\'ll", " will", txt)
    txt = re.sub(r"\'t", " not", txt)
    txt = re.sub(r"\'ve", " have", txt)
    txt = re.sub(r"\'m", " am", txt)

    return txt


def clean_misc(txt: str):
    """
    Handle a funny unicode symbols and stray
    garbage from encoding/decoding
    """
    txt = re.sub(r'\\x[a-zA-Z0-9]{2}', ' ', txt)  # stray \x.. utf-8 symbols
    txt = re.sub(r'\.\.\.', '', txt)  # 3 dot ellipses
    txt = re.sub(r"â€¦", '', txt)
    txt = re.sub(r"&amp", "and", txt)
    txt = re.sub(re.compile('(\d+(\.\d+)?%)'), '', txt)
    txt = re.sub(re.compile('[\$]{1}[\d,]+\.?\d{0,2}'), '', txt)
    txt = re.sub(re.compile(r'\b\d+(?:,\d+)?\b'), '', txt)
    return txt


def remove_punct(txt: str):
    """
    Remove all punctuation
    """
    txt = re.sub(r"\p{P}+", " ", txt)  # remove/pad all punct
    txt = re.sub('\n', ' ', txt)  # remove/pad newline characters
    txt = re.sub('ー|…|’|–|–', ' ', txt)  # remove/pad funny unicode
    txt = re.sub(r'\s+', ' ', txt)  # remove extra whitespace

    return txt

def remove_stopwords(txt, stopwords: Optional[Union[set, list]] = None):
    """
    Remove stopwords. By default the nltk stopwords list is used.
    """
    if stopwords is None:
        stopwords = nltk_stopwords
    txt = " ".join([x for x in txt.split() if x not in stopwords])

    return txt


def pad_emoji(txt):
    """
    Adds whitespace around emoji to separate from words
    """
    return ''.join(f' {char} ' if char in UNICODE_EMOJI else char for char in txt).strip()


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def remove_html_tags(txt: str):
    s = HTMLStripper()
    s.feed(txt)
    return s.get_data()


def remove_links(txt: str):
    """
    Remove weblinks from the text
    """
    pattern = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    txt = re.sub(pattern, " ", txt)
    txt = re.sub('http|https', " ", txt)

    return txt


def remove_emails(txt: str):
    """
    Remove email addresses
    """
    txt = re.sub(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", "", txt)
    return txt


# Combined processing function
def kitchen_sink(txt: str, stopwords: Optional[Union[set, list]] = None):
    """
    Apply all preprocessing steps.
    """
    if stopwords is None:
        stopwords = nltk_stopwords

    txt = remove_html_tags(txt)
    txt = remove_links(txt)
    txt = remove_emails(txt)
    txt = expand_contractions(txt)
    txt = clean_misc(txt)
    txt = remove_punct(txt)
    txt = pad_emoji(txt)
    txt = txt.lower()
    txt = remove_stopwords(txt, stopwords)

    return txt


if __name__ == '__main__':
    import argparse

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text', type=str, nargs='+', help="Space-separated listed of quoted docs to be cleaned",
                        required=True)
    args = vars(parser.parse_args())

    # load the input data, process it, and write to the output file
    print(args)
    cleaned_docs = [kitchen_sink(doc) for doc in args['text']]
    print(cleaned_docs)
