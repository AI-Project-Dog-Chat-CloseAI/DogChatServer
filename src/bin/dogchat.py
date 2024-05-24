from underthesea import word_tokenize, ner
from nltk import sent_tokenize
import framler
import string
from urllib.parse import urlparse
from googlesearch import search
import operator
from tqdm import tqdm
import sys

stopwords = set()

def tokenize(text):
    sents = sent_tokenize(text)
    sents = [word_tokenize(s, format='text') for s in sents]
    return sents

def keywords_extraction(sentences):
    sent = sentences.lower()
    sent = sent.split()
    sent = [s for s in sent if s not in stopwords and s not in string.punctuation]
    return sent

def main():
    question = sys.argv[1]
    question_tokenized = tokenize(question)
    keywords = keywords_extraction(" ".join(question_tokenized))

    search_result = list(search(question, num=50 ,lang = "vi", country= "VN"))
    print(search_result)

    domain_dict = {
        "vi.wikipedia.org": "wiki",
        "vnexpress.net": "vnexpress",
        "news.zing.vn": "zingnews",
        "dantri.com.vn": "dantri",
        "thethao.thanhnien.vn": "thethaothanhnien",
        "vietnamnet.vn": "vietnamnet",
        "tuoitre.vn": "tuoitrevn",
        "thanhnien.vn": "thanhnien",
        "cafebiz.vn": "cafebiz",
        "laodong.vn": "laodong"
    }

    result = {}

    with tqdm(total=len(search_result)) as pbar:
        for url in search_result: 
            domain = urlparse(url).netloc
            if domain not in domain_dict.keys():
                continue
            domain = domain_dict[domain]

            dt = framler.NewspapersParser(domain)
            print(url)
            try:
                text = dt.parse(url).text
            except Exception as e:
                print(f"Error parsing {url}: {e}")
                continue

            passages = []

            for sent in text.split('.'):
                sent_tok = " ".join(tokenize(sent))
                sent_tok = sent_tok.replace('\n', '').strip().lower()
                sent_keywords = keywords_extraction(sent_tok)
                num_overlap_keywords = len(set(sent_keywords) & set(keywords))
                if num_overlap_keywords > 0:
                    passages.append(sent)

            for p in passages:
                res = []
                for info in ner(p):
                    if info[3] == 'B-PER':
                        res.append(info[0])
                    if info[3] == 'I-PER':
                        res[-1] += ' ' + info[0]
                for r in res:
                    if r in result.keys():
                        result[r] += 1
                    else:
                        result[r] = 1
            for key in result.keys():
                if "_".join(key.split()).lower() in keywords:
                    result[key] = 0

            pbar.update(1)

    sorted_result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)

    print("Top results:")
    for name, count in sorted_result[:5]:
        print(f"{name}: {count}")

if __name__ == "__main__":
    main()