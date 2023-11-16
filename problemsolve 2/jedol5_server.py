from flask import Flask, request, abort, render_template, send_from_directory, jsonify, session
import os
import jedol3AiFun as jedol3AiFun
from datetime import datetime
import jedol1Fun as jshs
import jedol2ChatDbFun as chatDB
from dotenv import load_dotenv
from file_uploader import upload_file

load_dotenv()  # openai_key .env 선언 사용
# print( os.getenv('OPENAI_KEY')) 
app = Flask(__name__) 
chatDB.setup_db()
app.secret_key = 'jedolstory'



@app.errorhandler(404)
def not_found(e):
    return render_template('/html/404.html'), 404



@app.route('/uploader', methods=['POST'])
def uploader():
    result = upload_file()
    return result

@app.route('/', methods=['GET', 'POST'])
def showfiles():
    folder_path = "data"
    files = os.listdir(folder_path)
    return render_template('/html/show.html', files=files)

selected_file = ''

@app.route("/chat")
def index():
   global selected_file
   selected_file = request.args.get('selected_file', default='', type=str)
   print(selected_file)
   if not 'token' in session:
        session['token'] = jshs.rnd_str(n=20, type="s")
        print("new-token",session['token'])    
        chatDB.new_user(session['token'])
   else:
        print("old-token",session['token'])
    
   return render_template("/html/index.html",token=session['token'])


# 페이지 경로
@app.route('/<path:page>')
def page(page):
    print(f"Page request: {page}")
    try:
        if ".html" in page:
            return render_template(page)
        else:
            return send_from_directory("templates", page)
    except Exception as e:
        print(f'Error serving page {page}: {e}', exc_info=True)
        abort(404)

# AI 쿼리 경로
@app.route("/query", methods=["POST"])
def query():
    
    global selected_file
    #return jsonify({"answer": '제돌이 공부 중입니다. 14시 ~ 15시까지'})
    query = request.json.get("query")
    
    ai_mode = request.json.get("ai_mode")  # chatGPT or jedolGPT
    today = str(datetime.now().date().today())
    vectorDB_folder = f"vectorDB-faiss-jshs-{today}"

    
    if os.path.exists(vectorDB_folder) and os.path.isdir(vectorDB_folder):
      print(" used  vectorDB_folder ")
    else:
        print(" vectorDB_folder = ", vectorDB_folder )
        vectorDB_folder=jedol3AiFun.vectorDB_create(vectorDB_folder,selected_file)
        print(" vectorDB_folder ok ")
       

    print(f"User token: {session['token']}, AI mode: {ai_mode}, Query: {query}")
    try:
        answer = jedol3AiFun.ai_response(
            vectorDB_folder=vectorDB_folder if ai_mode in ["jedolGPT", "jshsGPT"] else "",
            query=query,
            token=session['token'],
            ai_mode=ai_mode
        )
    except Exception as e:
        print(f'Error in query processing: {e}')
        answer = f"{e}"
    
        
    print(f"Answer: {answer}")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
