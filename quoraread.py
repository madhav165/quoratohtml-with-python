#!/usr/bin/env python3

from urllib.request import urlretrieve
import urllib.request
from bs4 import BeautifulSoup
import argparse
import contextlib
import os
import re

global URL

def get_url():
    global URL
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    URL = args.url
    # URL = 'https://www.quora.com/Computer-Vision-What-are-the-fastest-object-recognition-algorithms-in-Python'

def get_html():
    req = urllib.request.Request(URL, 
      headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2816.0 Safari/537.36'})
    with contextlib.closing(urllib.request.urlopen(req)) as f:
        return f.read().decode('utf-8');

def _remove_attrs(soup):
    for tag in soup.findAll(True): 
        tag.attrs = {}
    return soup

def get_matches(html_doc):
    soup = BeautifulSoup(html_doc, 'lxml')

    #Page title
    title = soup.title.text

    #Remove scripts
    [s.extract() for s in soup('script')]

    #Create HTML file
    script_path = os.path.realpath(__file__)
    script_dir = os.path.split(script_path)[0]
    html_folder_path = os.path.join(script_dir, 'html')
    if (not os.path.exists(html_folder_path)):
        os.makedirs(html_folder_path)
    rel_path = 'html/'+title.replace('/','')+'.html'
    abs_file_path = os.path.join(script_dir, rel_path)
    f = open(abs_file_path ,'w')

    #Start writing to HTML file
    f.write('<!doctype html><html><head><title>'+title+'</title><meta author="stackexchange.com"></head><body>')
    f.write ('<h1>'+title+'</h1>')

    main_area = soup.find('div', class_='layout_2col_main')
    
    question_area = main_area.find('div', class_='header').div.find('div', class_='QuestionArea')
    question_text = question_area.find('div', class_='question_text_edit').find('span', class_='rendered_qtext').text.strip()
    question_details = question_area.find('div', class_='question_details_text').find('span', class_='rendered_qtext').text.strip()
    if question_details is not None:
      f.write ('<p>' + question_details + '</p>')

    answers_area = main_area.findAll('div', recursive=False)[1]

    answers_main_div = answers_area.findAll('div', recursive=False)

    for d in answers_main_div:
      maybe_num_of_answers = d.find('div', class_='QuestionPageAnswerHeader', recursive=False)
      maybe_answer_list_div = d.find('div', class_='AnswerPagedList', recursive=False)

      maybe_answer_text = d.parent.find('div', {'id' : re.compile('_answer_content$')})

      if maybe_num_of_answers is not None:
        num_of_answers = maybe_num_of_answers.find('div', class_='answer_count').find(text=True).strip()
        f.write('<h2>' + num_of_answers + '</h2>')
      elif maybe_answer_list_div is not None:
        answer_divs = maybe_answer_list_div.findAll('div', class_='pagedlist_item', recursive=False)
        for ans in answer_divs:
          maybe_answerer_name = ans.find('span', class_='feed_item_answer_user')
          if maybe_answerer_name is not None:
            if maybe_answerer_name.find('span', class_='anon_user') is not None:
              answerer_name = maybe_answerer_name.find('span', class_='anon_user').text.strip()
              f.write ('<p><b>' + answerer_name + '</b>')
            else:
              answerer_name = maybe_answerer_name.find('a', class_='user').text.strip()
              answerer_details = maybe_answerer_name.find('span', class_='rendered_qtext').text.strip()
              f.write ('<p><b>' + answerer_name + '</b>, <i>' + answerer_details + '</i>')
            number_of_views = ans.find('div', class_='CredibilityFacts').text.strip()
            f.write('<br/>' + number_of_views + '</p>')
            ans_text = ans.find('div', class_='ExpandedAnswer').find('span', class_='rendered_qtext')
            f.write('<p>' + str(ans_text) + '</p>')

      elif maybe_answer_text is not None:
        ans_text = maybe_answer_text.div.div.span

    f.write('</body></html>')
    f.close()


get_url()
html_doc = get_html()
print ('Connection established')
get_matches(html_doc)