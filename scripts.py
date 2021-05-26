from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import spacy
import stanza
#stanza.download('en') # will only need to run this line first time
import pandas as pd

def get_chapters(file_name):
    chapters = []
    #to_ignore = ['afterword', 'bonus', 'copyright', 'cover', 'frontmatter', 'insert', 'sidecover', 'signup', 'toc']

    book = epub.read_epub(f'epubs/{file_name}')
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    for item in items:
        #if any([word in item.get_name() for word in to_ignore]): continue
        if 'chapter' in item.get_name():
            chapters.append(item)
    
    return chapters

def chapters_to_dict(chapters):
    texts = {}
    splits = []

    for c in chapters:
        chapter_name = c.get_name()
        if '_' in chapter_name:
            splits.append(c)
            continue
        chapter_num = int(chapter_name[chapter_name.find('chapter')+7:chapter_name.find('.')])
        texts[chapter_num] = chapter_to_str(c)

    for c in splits:
        chapter_name = c.get_name()
        chapter_num = int(chapter_name[chapter_name.find('chapter')+7:chapter_name.find('.')].split('_')[0])
        texts[chapter_num] = texts[chapter_num] + ' ' + chapter_to_str(c)
    
    return texts

def chapter_to_str(chapter):
    soup = BeautifulSoup(chapter.get_body_content(), 'html.parser')
    text = [paragraph.get_text() for paragraph in soup.find_all('p')]
    
    return ' '.join(text)

def find_names(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    
    proper_nouns = []
    for token in doc:
        if str(token.tag_) == 'NNP':
            proper_nouns.append(token.text)
            
    return list(set(proper_nouns))

def find_names_stanza(text, nlp):
    doc = nlp(text)
    
    proper_nouns = []
    for word in doc.ents:
        if 'PERSON' in word.type:
            proper_nouns.append(word.text)
            
    return list(set(proper_nouns))

"""
obsolete - used NLTK + Senna, didn't work as well as spacy, still neet to try stanza and flair

from nltk import sent_tokenize, word_tokenize#, download
from nltk.tag import SennaTagger
import string
#download('punkt') # will need to uncomment and run first time to download, and periodically after to update

def find_names(text):
    tagger = SennaTagger('C:/ProgramData/nltk_data/taggers/senna')
    tags = [tagger.tag(word_tokenize(sent)) for sent in sent_tokenize(text)]
    proper_nouns = list(filter(lambda x: x[1]!='O', [j for i in tags for j in i]))

    with open('words.txt') as file:
        words = set(line.strip().lower() for line in file)
    
    names = []
    punctuation = string.punctuation + '‘’“”'
    for noun, pos in proper_nouns:
        noun_compare = noun.translate(str.maketrans('', '', punctuation))
        if noun_compare != '' and noun_compare not in names and noun_compare.casefold() not in words:
            names.append(noun)

    return list(set(names))
""" 
 
def find_all_names(texts, verbose=False, use_stanza=False):
    names = []
    keys = sorted(texts.keys())
    if use_stanza:
        nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', logging_level='FATAL')
    
    for key in keys:
        if verbose:
            print(f'starting chapter {str(key)} of {keys[-1]}')
        if use_stanza:
            names.extend(find_names_stanza(texts[key], nlp))
        else:
            names.extend(find_names(texts[key]))

    return list(set(names))

def find_first(word, texts):
    keys = sorted(texts.keys())
    for key in keys:
        if word in texts[key]:
            return (key, round(100*texts[key].find(word)/len(texts[key])))

def find_last(word, texts):
    keys = sorted(texts.keys(), reverse=True)
    for key in keys:
        if word in texts[key]:
            return (key, round(100*texts[key].rfind(word)/len(texts[key])))
        
def find_all(words, texts):
    positions = []
    keys = sorted(texts.keys())
    for key in keys:
        for word in words:
            if word in texts[key]:
                positions.append((key, round(100*texts[key].find(word)/len(texts[key]))))
    
    if positions == []:
        return [(0, 0)]
    return sorted(positions)
        
def find_first_and_last(names, texts):
    rows = []
    for name in names:
        row = {}
        row['name'] = name
        
        positions = find_all(name.split('|'), texts)
        #first_ch, first_pos = find_first(name, texts)
        row['first_chapter'] = positions[0][0]
        row['first_position'] = positions[0][-1]
        
        #last_ch, last_pos = find_last(name, texts)
        row['last_chapter'] = positions[-1][0]
        row['last_position'] = positions[-1][-1]
        
        rows.append(row)
    
    return sorted(rows, key = lambda x: (x['first_chapter'], x['first_position']))

def find_words_between(row, texts):
    if row['first_chapter']==0 or row['last_chapter']==0:
        row['words_between'] = 0
        return row
        
    distance = 0
    first_pos = texts[row['first_chapter']].find(row['name'])
    last_pos = texts[row['last_chapter']].rfind(row['name'])
    
    if row['first_chapter']==row['last_chapter'] and row['first_position']!=row['last_position']:
        text_between = texts[row['first_chapter']][first_pos:last_pos]
        distance = len(text_between.split()) - 1
    
    elif row['first_chapter']!=row['last_chapter'] and row['first_position']!=row['last_position']:
        dist_first = len(texts[row['first_chapter']][first_pos:].split()) - 1
        dist_last = len(texts[row['last_chapter']][:last_pos].split())
        distance = dist_first + dist_last
        
        if row['last_chapter']-row['first_chapter'] > 1:
            for c in range(row['first_chapter']+1, row['last_chapter']):
                distance += len(texts[c].split())
    
    row['words_between'] = distance
    return row

def find_words_after(row, texts):
    if row['first_chapter']==0 or row['last_chapter']==0:
        row['words_after'] = 0
        return row
    
    last_pos = texts[row['last_chapter']].rfind(row['name'])
    distance = len(texts[row['last_chapter']][last_pos:].split()) - 1
    
    chapter_max = sorted(texts.keys(), reverse=True)[0]
    if row['last_chapter'] < chapter_max:
        for c in range(row['last_chapter']+1, chapter_max):
                distance += len(texts[c].split())
    
    row['words_after'] = distance
    return row
    

def get_data(filename, names=None):
    texts = chapters_to_dict(get_chapters(filename))
    if names is None:
        names = find_all_names(texts)
    df = pd.DataFrame(find_first_and_last(names, texts))
    df = df.apply(lambda row: find_words_between(row, texts), axis=1)
    df = df.apply(lambda row: find_words_after(row, texts), axis=1)
    df['name'] = df['name'].map(lambda x: x.replace('|', ' '))
                    
    return df