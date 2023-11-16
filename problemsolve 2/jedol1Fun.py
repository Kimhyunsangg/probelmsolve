from bs4 import BeautifulSoup
from urllib.request import urlopen
import os
import requests
import random
import string
from datetime import datetime, timedelta
import re
import asyncio
from transformers import GPT2Tokenizer
from langchain.text_splitter import Document

tokenizer = None

def tiktoken_len(text):
    global tokenizer
    if tokenizer is None:
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokens = tokenizer.tokenize(text)
    return len(tokens)

def page_content_append(oldChat="",newChat="",sourece=""):
       
       page_content=oldChat+ ' \n' + newChat if oldChat!="" else newChat
            
       return Document( page_content=page_content ,metadata={'source': sourece})
       
       
                    

def image_url_to_save(image_url, folder_name="", image_name=""):
   # 이미지 저장  
    if image_url    =="" :  return False
    if folder_name  =="":  folder_name="." 
    if image_name   =="":   image_name ="image-" + rnd_str(5,"n") +".jpg"
    if not os.path.exists(folder_name):   os.makedirs(folder_name)
 
    response = requests.get(image_url)

    file_path = os.path.join(folder_name, image_name)

    file=open(file_path, "wb")

    file.write(response.content)
    return True

def today_year():
    today = datetime.now().today()
    return f"{today.strftime('%y년')}"  
def today_month():
    today = datetime.now().today()
    return f"{today.strftime('%m월')}"  

def today_date():
    today = datetime.now().today()
    return f"{today.strftime('%Y년 %m월 %d일')}"  
    
def today_week_name():
    today = datetime.now().today()
    days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    return f"{days[today.weekday()]}" 
    
def rnd_str(n=5, type="ns"):
    if type == "n":
        characters = string.digits
    elif type == "s":
        characters = string.ascii_letters
    else:  # "ns" 또는 기타
        characters = string.digits + string.ascii_letters
    return ''.join(random.choices(characters, k=n))

def getMealMenuNeis(page_content=[]):
    page_content_tmp=""
    for m in page_content:
        date= datetime.strptime(m["date"], "%Y%m%d")
        date = date.strftime("%Y년 %m월 %d일")
        
        mm=m["menu"]
        mm= re.sub("<[^<>]*>", "",mm)
        mm= re.sub(r'\([^)]*\)', '', mm)
        mm=mm.strip().replace(" ",",")
        page_content_tmp += f'{m["schoolName"]} {date} {m["codeName"]} 메뉴는 {mm} 입니다.\n '
    return page_content_tmp    

def getMealMenu(today="",period="",type=""):
    if today=="":
       today = str(datetime.date.today())
    period="lunch" if  period =="" else  period
    meal_name=[ "breakfast","lunch","dinner"]
    period_ko= "아침" if  period=="breakfast" else "점식" if period=="lunch" else "저녁"
    t=today.split("-")
    url=f"http://jeju-s.jje.hs.kr/jeju-s/food/{t[0]}/{t[1]}/{t[2]}/{period}"

    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    bap = soup.select(".ulType_food > li:nth-child(2) > dl > dd")[0]
    image_url=""
    if  soup.select(".food_img> img"): 
        image=soup.select(".food_img> img")[0].get("src") 
        image_url="http://jeju-s.jje.hs.kr" + image
    menu=str(bap).split("<br/>")
    tmp=[]
    menuName= today +" " + period_ko + " 메뉴는 "
    sw=0
    for m in menu:
        m= re.sub("<[^<>]*>", "",m)
        m= re.sub(r'\([^)]*\)', '', m)
        if m !='' and not "축산물" in m  and not "." in m:
         
          tmp.append( m )
          menuName +=(", " if sw==1 else "") + m 
          sw=1

    if type=="ai":
        return menuName.replace(" , ",", ") +  ( "없습니다." if sw==0 else "입니다." )  +"\n\n"
    else:
        return {"item":tmp,"image":image_url} 

def remove_words(text="",remove_words=["게시", "안내"] ):
    # remove_words 문자열 제거 
    words = text.split()
    filtered_words = [word for word in words if not any(remove_word in word for remove_word in remove_words)]
    return ' '.join(filtered_words)

def get_text_after_words( text="",start_str="",end_str="",re=""):

    start_index = text.find(start_str)
    end_index = text.find(end_str)

    if start_index != -1 and end_index != -1:
        text = text[start_index:end_index]
    else:
        if start_index != -1:
            text = text[start_index]
        else:
            if  re =="" :
                text="데이터 없음!"  
            else:
                text= text
    return text


def html_parsing_text(page_content="",start_str="",end_str="",length=20,removeword=[]):

    page_content = re.sub("\n+", "\n", page_content)
    page_content = re.sub("\s+", " ", page_content)
    page_content=remove_words(text=page_content,remove_words=["게시","안내"])
    page_content=get_text_after_words(text=page_content,start_str=start_str,end_str=end_str)
    parts = page_content.split(" ")  # 공백을 기준으로 문자열 분리
    newStr=""
    for s in parts:

        if len(s)< length :
        #   s=s.replace("\n"," ")
          newStr += s +" "  
    return newStr +"\n\n"

def loader_documents_viewer(documents):

    print(documents)
    print("="*100)
    print("Page Content:\n", documents[0].page_content)
    print("\nMetadata:", documents[0].metadata)

def splitter_pages_viewer(pages):
    print("="*100)
    print("pages = ", len(pages) )
    print("-"*100)
    for index,page  in enumerate(pages):
         print( "{:02d} {}".format(index+1, tiktoken_len(page.page_content)), page.page_content.replace('\n', ''), page.metadata['source'])

    print("="*100)
    
def similarity_score_viewer(vector_db,query ):
    loop = asyncio.get_event_loop() # 비동기 처리;
    docs = loop.run_until_complete(vector_db.asimilarity_search_with_relevance_scores(query) ) # 유사도 있는 비동기 개체호출 
    similarity=[]
    for doc, score in docs:
         similarity.append( ( doc.page_content,score) )
    
    print("="*100)
    print( query ,"  추천한 유사 페이지")
    print("-"*100)
    for index, (doc, score) in enumerate(similarity) :
        print(f"{index+1}:  {score}\t{doc}\n\n")
    print("="*00)
    return similarity



def school_schedule(year):

    ret =""
    section=[1,2] 
    for hakgi in section:
        html = urlopen(f"https://jeju-s.jje.hs.kr/jeju-s/0202/schedule?section={hakgi}")
        soup = BeautifulSoup(html, "html.parser")
        bap = soup.select("a")
       
        for b in bap:
            if  ':' in b.text:
                bb=b.get("onclick")
                t=bb.replace("'","")
                t=t.split(",")
                t.pop(0)
                t.pop()
                t = [e.strip() for e in t]
                    
                if t[0] != t[1] :
                    tt=t[0] + "~" + t[1] + ":" + t[2] 
                else:
                    tt=t[0] + ":" + t[2]     
                ret += tt + ", "   
    return ret +"\n\n "
if __name__ == "__main__":
    
    resp=school_schedule(datetime.now().today().year)
    print(resp)
   