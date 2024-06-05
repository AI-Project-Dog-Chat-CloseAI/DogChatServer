from underthesea import word_tokenize, ner
from newspaper import Article # import newspaper3k
import string
from urllib.parse import urlparse
from googlesearch import search
import operator
from flask import Flask, request, jsonify
import json
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2' )

app = Flask(__name__)
stopwords = set()


def tokenize(text): 
    # Hàm xử lí ngôn ngữ tự nhiên 
    # Bằng thư viện underthesea để xác định các từ trong câu 
    sents = word_tokenize(text, format='text')
    return sents

def keywords_extraction(sentences): 
    # Trả về mảng gồm các từ trong câu
    sent = sentences.lower()
    sent = sent.split() # tách các từ 
    sent = [s for s in sent if s not in stopwords and s not in string.punctuation] 
    # Loại bỏ dấu trong câu
    return sent

def ques_type(words): 
    # Xác định từ khóa cho mỗi loại câu hỏi
    who_keywords = ['ai', 'người']
    where_keywords = ['ở', 'tại', 'đâu']
    when_keywords = ['khi', 'lúc', 'bao_giờ']
    why_keywords = ['tại sao', 'vì_sao', 'tại_vì']
    what_keywords = ['gì', 'cái_gì']
    number_result_keywords = ['bao_nhiêu', 'mấy' ]
    # Kiểm tra từ khóa có trong câu hỏi hay không
    for word in words:
        if word in who_keywords:
            return "who"
        elif word in where_keywords:
            return "where"
        elif word in when_keywords:
            return "when"
        elif word in why_keywords:
            return "why"
        elif word in what_keywords:
            return "what"
        elif word in number_result_keywords:
            return "number"
        
    # Nếu không tìm thấy từ khóa nào, mặc định là "who"
    return "what"

def load_dialogs(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Hàm tìm kiếm câu tương tự nhất
def get_most_similar_response(user_input, dialogs, similarity_threshold=0.8, batch_size=10):
    questions = [dialog['question'] for dialog in dialogs]
    answers = [dialog['answers'] for dialog in dialogs]
    
    response = ""
    for i in range(0, len(questions), batch_size):
        batch_questions = questions[i:i+batch_size]
        batch_answers = answers[i:i+batch_size]
        
        # Mã hóa câu hỏi của người dùng và câu hỏi từ dữ liệu
        user_input_embedding = model.encode([user_input], convert_to_tensor=True)
        dialog_embeddings = model.encode(batch_questions, convert_to_tensor=True)
        
        # Tính toán độ tương tự cosine
        similarities = util.pytorch_cos_sim(user_input_embedding, dialog_embeddings)[0]
        
        # Tìm câu hỏi có độ tương tự cao nhất trong batch hiện tại
        max_similarity, max_index = similarities.max().item(), similarities.argmax().item()
        
        # Nếu độ tương tự cao hơn ngưỡng, lấy câu trả lời và kết thúc vòng lặp
        if max_similarity >= similarity_threshold:
            response = batch_answers[max_index]
            break
    
    return response

@app.route('/', methods=['POST'])
def main():
    data = request.get_json()
    question = data.get('question')
    file_path = 'dataset.json'
    dialogs = load_dialogs(file_path)
    response = get_most_similar_response(question, dialogs)
    if(response != "") : return jsonify(response), 200
    question_tokenized = tokenize(question)
    keywords = keywords_extraction(question_tokenized)
    type = ques_type(keywords)
    print(type)

    search_result = list(search(question, num= 5 ,lang = "vi", country='VN'))
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
        "laodong.vn": "laodong",
        "kenh14.vn" : "kenh14"
    } # Các trang báo sử dụng để lấy thông tin

    result = {}

    for url in search_result: 
        domain = urlparse(url).netloc
        if domain not in domain_dict.keys():
            continue
        domain = domain_dict[domain]
        article = Article(url)
        article.download() 
        try:
            article.parse()
            text = article.text #trả về data
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            continue

        passages = []

        for sent in text.split('.'): # Tách data trả về thành các câu
            sent_tok = tokenize(sent) # Phân tích các từ có trong câu
            sent_keywords = keywords_extraction(sent_tok)
            num_overlap_keywords = len(set(sent_keywords) & set(keywords)) #số từ trùng với keyword có trong câu
            if num_overlap_keywords > 1:
                passages.append(sent)  # Trả về câu có ít nhất 2 từ trùng với keyword
                print(sent)

        for p in passages:
            res = []
            if type == 'who':
                for info in ner(p): # Phân tích, phân loại từ thành thực thể
                    if info[3] == 'B-PER': # Từ là thực thể chỉ tên thì nhận
                        res.append(info[0])
                    if info[3] == 'I-PER':
                        res[-1] += ' ' + info[0]
            elif type == 'where':
                for info in ner(p): # Phân tích, phân loại từ thành thực thể
                    if info[3] == 'B-LOC': # Từ là thực thể chỉ tên thì nhận
                        res.append(info[0])
            elif type == 'what': 
                for info in ner(p): # Phân tích, phân loại từ thành thực thể
                    if info[3] == 'O' and info[1] == 'N': # Từ là thực thể chỉ tên thì nhận
                        res.append(info[0])
            elif type == 'number': 
                for info in ner(p): # Phân tích, phân loại từ thành thực thể
                    if info[1] == 'M': # Từ là thực thể chỉ tên thì nhậsn
                        res.append(info[0])
            for r in res: # Đếm số lần xuất hiện của từ
                if r in result.keys(): 
                    result[r] += 1
                else:
                    result[r] = 1
        for key in result.keys():
            if "_".join(key.split()).lower() in keywords: # Từ có trong câu hỏi thì loại
                result[key] = 0
            if key in string.punctuation: 
                result[key] = 0

    print(result)
    sorted_result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)
    if(sorted_result[0][0] == "") : return jsonify(), 404
    new_question = {
        "question": question,
        "answers": sorted_result[0][0],
    }
    dialogs.append(new_question)

    # Ghi cập nhật dữ liệu vào tập tin JSON
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(dialogs, file, ensure_ascii=False, indent=4)
    return jsonify(sorted_result[0][0]), 200

if __name__ == "__main__":
    app.run(debug=True)
