from flask import Flask, render_template, request
import gunicorn
#from requests import request
import spacy 

try:
    nlp = spacy.load("en_core_web_sm")
except: # If not present, we download
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Pkgs for Normalizing Text
from spacy.lang.en.stop_words import STOP_WORDS
from heapq import nlargest

def text_summarizer(raw_docx):
    raw_text = raw_docx
    docx = nlp(raw_text)
    stopwords = list(STOP_WORDS)
    # Build Word Frequency # word.text is tokenization in spacy
    word_frequencies = {}  
    for word in docx:  
        if word.text not in stopwords:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1


    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    # Sentence Tokens
    sentence_list = [ sentence for sentence in docx.sents ]

    # Sentence Scores
    sentence_scores = {}  
    for sent in sentence_list:  
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]


    summarized_sentences = nlargest(7, sentence_scores, key=sentence_scores.get)
    final_sentences = [ w.text for w in summarized_sentences ]
    summary = ' '.join(final_sentences)
    return summary



app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/summarize_text', methods=['GET', 'POST'])
def summarize_text():
    if request.method == 'POST':
        input_text = request.form['input-text']
        summarized_text = text_summarizer(input_text)

    return render_template('index.html', summarized_text=summarized_text)


# @app.route('/analyze',methods=['GET','POST'])
# def analyze():
# 	start = time.time()
# 	if request.method == 'POST':
# 		rawtext = request.form['rawtext']
# 		final_reading_time = readingTime(rawtext)
# 		final_summary = text_summarizer(rawtext)
# 		summary_reading_time = readingTime(final_summary)
# 		end = time.time()
# 		final_time = end-start
# 	return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)


if __name__ == '__main__':
    app.run(debug=True, port=33507)