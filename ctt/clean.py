import re
from typing import Union, Optional
import string
from io import StringIO
from html.parser import HTMLParser

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


# Remove stray utf8
def remove_utf8(txt: str):
    """
    Remove stray utf symbols from encoding/decoding errors
    """
    patt = r'\\x[a-zA-Z0-9]{2}'
    txt = re.sub(patt, ' ', txt)

    return txt


def clean_misc(txt: str):
    """
    Convert ellipses into "<ellipses>", ampersands into "and",
    percantage signs into "<percent>", dollars into "<dollars>",
    and numbers into "<number>".
    """
    txt = re.sub(r'\.\.\.', '', txt)
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
    txt = txt.translate(str.maketrans('', '', string.punctuation))
    txt = re.sub('\n', ' ', txt)  # remove newline characters

    return txt


def remove_stopwords(txt, stopwords: Optional[Union[set, list]] = None):
    """
    Remove stopwords. By default the nltk stopwords list is used.
    """
    if stopwords is None:
        stopwords = nltk_stopwords
    txt = " ".join([x for x in txt.split() if x not in stopwords])

    return txt


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
    txt = re.sub(r'http\S+', '', txt)  # remove http links
    txt = re.sub(r'bit.ly/\S+', '', txt)  # rempve bitly links
    txt = re.sub(r"[a-zA-Z0-9+_.-]+.edu", "", txt)  # remove .edu links
    txt = txt.strip('[link]')  # remove [links]

    return txt


def remove_emails(txt: str):
    """
    Remove email addresses
    """
    txt = re.sub(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", "", txt)
    return txt


def remove_twitter(txt: str):
    """
    Removes @user and RT @usr
    """
    txt = re.sub(r"(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)", '', txt)  # remove retweet
    txt = re.sub(r"(@[A-Za-z]+[A-Za-z0-9-_]+)", '', txt)  # remove tweeted at
    return txt


# Combined processing function
def kitchen_sink(txt: str, stopwords: Optional[Union[set, list]] = None):
    """
    Apply all preprocessing steps.
    """
    if stopwords is None:
        stopwords = nltk_stopwords

    txt = remove_html_tags(txt)
    txt = remove_emails(txt)
    txt = remove_twitter(txt)
    txt = remove_links(txt)
    txt = expand_contractions(txt)
    txt = remove_utf8(txt)
    txt = clean_misc(txt)
    txt = remove_punct(txt)
    txt = txt.lower()
    txt = remove_stopwords(txt, stopwords)

    return txt


if __name__ == '__main__':
    import argparse
    from sklearn.datasets import fetch_20newsgroups

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text', type=str, nargs='+', help="Space-separated listed of quoted docs to be cleaned",
                        required=True)
    args = vars(parser.parse_args())

    # load the input data, process it, and write to the output file
    print(args)
    cleaned_docs = [kitchen_sink(doc) for doc in args['text']]
    print(cleaned_docs)