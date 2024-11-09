from flask import Flask,render_template,request,url_for,redirect,make_response,flash,abort,session,send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PIL import Image, ImageDraw, ImageFont
import time,secrets,random
import json,requests
import tempfile
import win32api,win32print
import urllib.parse
from datetime import datetime
import os
import markdown
import threading
import copy
import string
import io

############################
file_route = "D:\qifan_maker\project\keynote\\blog\public\\"
server_ip = "192.168.1.78"
server_port = 80
debug = True
############################

app = Flask(__name__)
if (debug):
    app.secret_key = "_qifan_maker_love_luotianyi_998244353" 
else:
    app.secret_key = secrets.token_hex()
limiter = Limiter(
    key_func=get_remote_address,   #根据访问者的IP记录访问次数
    default_limits=["1000/day", "50/minute"]  #默认限制
)
limiter.init_app(app=app)

print(f"token:{app.secret_key}")

user = {}
web_name = "None"
web_footer = "None"
web_proclamation = "None"
image_list = {}
blog_list = {}
blog_typel = {
    "other":"其他",
    "record":"记录",
    "solution":"题解",
    "study":"笔记",
    "admin":"站务"
}
judgement = []

def read_setting():
    file = open(file_route+"\\data\\setting.json","r",encoding='utf-8')
    setting = json.loads(file.read())
    file.close()
    global web_name,web_footer,web_proclamation   
    web_name = setting.get("web_name")
    web_footer = setting.get("web_footer")
    web_proclamation = setting.get("web_proclamation")

def read_user():
    file = open(file_route+"\\data\\user_info.json","r",encoding='utf-8')
    user_info = json.loads(file.read())
    file.close()
    for i in user_info:
        user[i] = user_info[i]

def read_img():
    file = open(file_route+"\\data\\img_info.json","r",encoding='utf-8')
    img_info = json.loads(file.read())
    file.close()
    image_list.clear()
    for i in img_info:
        image_list[i] = img_info[i]

def read_blog():
    # id:[name,about,author,time,plate,topping,views,hiding]
    file = open(file_route+"\\data\\blog_info.json","r",encoding='utf-8')
    blog_info = json.loads(file.read())
    file.close()
    blog_list.clear()
    for i in blog_info:
        blog_list[i] = blog_info[i]

def read_judge():
    file = open(file_route+"\\data\\judgement.json","r",encoding='utf-8')
    judge_info = json.loads(file.read())
    file.close()
    for i in judge_info:
        judgement.append(i)

def updata_data():
    read_setting()
    read_user()
    read_img()
    read_blog()
    read_judge()
updata_data()

punctuation = {
    ",",
    ".",
    ":",
    "：",
    "，",
    "。",
    "；",
    ";",
    "(",
    ")",
    "（",
    "）",
    "—",
    "_",
    "！",
    "!",
    "？",
    "?"
}

def check_acc(username,password,lv):
    """
    0: NotFindUser; 
    1: PasswordError; 
    2: LoginNotAllowed
    3: Banned
    4: PowerError
    """
    if (not username in user):
        return 0
    if (user.get(username).get("password") != password):
        return 1
    if (password=="LoginNotAllowed"):
        return 2
    if (user.get(username).get("power") == "banned"):
        return 3
    if (lv == 2):
        if (user.get(username).get("power") == "super"):
            return 10
        else:
            return 4
    if (lv == 1):
        if (user.get(username).get("power") == "admin" or user.get(username).get("power") == "super"):
            return 10
        else: 
            return 4
    return 10

def check_login():
    if ("username" in session and "password" in session):
        return True
    else:
        return False
    
def get_blog(blogID):
    try:
        file = open(file_route+"blog\\"+blogID+".blog","r",encoding='utf-8')
        blogc = file.read()
        file.close()
    except:
        blogc = "## Error \n找不到该文件"
    return blogc

def save_user():
    write_info = str(user)
    for i in range(len(write_info)):
        if write_info[i] == "'":
            write_info = write_info[:i]+"\""+write_info[i+1:]
    file = open(file_route+"data\\user_info.json","w",encoding='utf-8')
    file.write(write_info)
    file.close()

    write_judge = str(judgement)
    for i in range(len(write_judge)):
        if write_judge[i] == "'":
            write_judge = write_judge[:i]+"\""+write_judge[i+1:]
    file = open(file_route+"data\\judgement.json","w",encoding='utf-8')
    file.write(write_judge)
    file.close()
    
def save_blog(blogID,blogc):
    file = open(file_route+"blog\\"+blogID+".blog","w",encoding='utf-8',newline='')
    file.write(blogc)
    file.close()
    updata_blog()

def save_setting(new_name,new_footer,new_proclamation):
    setting = {}
    setting["web_name"] = new_name
    setting["web_footer"] = new_footer
    setting["web_proclamation"] = new_proclamation
    file = open(file_route+"\\data\\setting.json","w",encoding='utf-8')
    file.write(json.dumps(setting))
    file.close()
    read_setting()

def updata_img():
    file = open(file_route+"\\data\\img_info.json","w",encoding='utf-8')
    file.write(json.dumps(image_list))
    file.close()

def updata_blog():
    file = open(file_route+"\\data\\blog_info.json","w",encoding='utf-8')
    file.write(json.dumps(blog_list))
    file.close()
    
def get_word(word):
    geted = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").text
    return geted

def check_long(string,leng):
    if (len(string) > leng or len(string) == 0):
        return False
    else:
        return True

def legal(string):
    unl = {
        "&":"&amp;",
        "\"":"&quot;",
    }
    nl = {
    }
    for i in unl:
        string = string.replace(i,unl[i])
    for i in nl:
        string = string.replace(i,nl[i])
    return string

def legal2(string):
    unl = {
        "&":"&amp;",
    }
    nl = {
    }
    for i in unl:
        string = string.replace(i,unl[i])
    for i in nl:
        string = string.replace(i,nl[i])
    return string

def my_mktime(dtime):
    date_obj = datetime.strptime(dtime, "%Y-%m-%d")
    timestamp = time.mktime(date_obj.timetuple())
    return timestamp

# 允许上传的文件后缀
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','PNG', 'JPG', 'JPEG', 'GIF'])
# 配置上传文件保存位置
app.config['UPLOAD_FOLDER'] = os.getcwd()
# 上传文件大小
app.config['MAX_CfONTENT_LENGTH'] = 1024 * 1024 * 8

# 判断是否是允许的文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 生成随机的字符串
def random_string(length=8):
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))

def getcode(rid):
    try:
        file = open(file_route+f"judge\\{rid}\\r{rid}.cpp","r",encoding='utf-8')
        code = file.read()
        file.close()
    except:
        code = "Error:找不到该文件"
    return code



######################################################################################
# captcha
######################################################################################

def captcha_image():
    # 定义图片大小及背景颜色
    # bk_color=(73, 109, 137)
    bk_color=(random.randint(0,100), random.randint(0,100), random.randint(0,100))
    image = Image.new('RGB', (100, 35), bk_color)

    # 使用系统自带字体，或指定字体文件路径
    font_path = "./arial.ttf"
    fnt = ImageFont.truetype(font_path, random.randint(17,25))
    d = ImageDraw.Draw(image)

    # 生成4位数的验证码文本
    ct_color=((bk_color[0]+random.randint(100,150))%256, (bk_color[1]+random.randint(100,150))%256, (bk_color[2]+random.randint(100,150))%256)

    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    x1 = random.randint(0,25)
    x2 = random.randint(x1+10,x1+25)
    x3 = random.randint(x2+10,x2+25)
    x4 = random.randint(x3+10,x3+25)
    if (x4 > image.width-20):
        x4 = image.width-20
    d.text((x1, random.randint(0,10)), captcha_text[0], font=fnt, fill=ct_color)
    d.text((x2, random.randint(0,10)), captcha_text[1], font=fnt, fill=ct_color)
    d.text((x3, random.randint(0,10)), captcha_text[2], font=fnt, fill=ct_color)
    d.text((x4, random.randint(0,10)), captcha_text[3], font=fnt, fill=ct_color)

    # 添加干扰线条和噪点
    for _ in range(random.randint(3, 7)):
        start = (random.randint(0, image.width), random.randint(0, image.height))
        end = (random.randint(0, image.width), random.randint(0, image.height))
        d.line([start, end], fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    for _ in range(100):
        xy = (random.randrange(0, image.width), random.randrange(0, image.height))
        d.point(xy, fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))

    # 定义三个点
    point1 = (0, 0)
    point2 = (image.width, 0)
    point3 = (0, image.height)

    # 定义扭曲程度和方向
    offset = 30
    transform = (point1[0] + offset, point1[1] + offset, point2[0] - offset, point2[1] + offset, point3[0] + offset, point3[1] - offset)

    # 进行扭曲操作
    image.transform(image.size, Image.AFFINE, transform)

    return image, captcha_text


@app.route('/captcha')
def captcha():
    # 使用上述函数生成验证码图片
    image, captcha_text = captcha_image()

    # 将验证码文本存储到session，以便之后进行验证
    session['captcha'] = captcha_text

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue(), 200, {
        'Content-Type': 'image/png',
        'Content-Length': str(len(buf.getvalue()))
}



######################################################################################
# static
######################################################################################

@app.route("/static/images/<src>", methods=["GET"])
@limiter.exempt
def images(src):
    return send_file(file_route+"static\\images\\"+src)

@app.route("/favicon.ico", methods=["GET"])
@limiter.exempt
def favicon():
    return send_file(file_route+"favicon.ico")

######################################################################################
# web
######################################################################################

@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html',web_name=web_name,web_footer=web_footer,user=user), 400

@app.errorhandler(403)
def page_insufficient_permissions(error):
    return render_template('403.html',web_name=web_name,web_footer=web_footer,user=user), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',web_name=web_name,web_footer=web_footer,user=user), 404

@app.errorhandler(429)
def page_not_found(error):
    return render_template('429.html',web_name=web_name,web_footer=web_footer,user=user,error=error), 429

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html',web_name=web_name,web_footer=web_footer,user=user), 500

@app.route("/", methods=["GET"])
def index():
    # print(session)
    key_data = list(blog_list.keys())
    keys_list = []
    for i in range(0,len(key_data)):
        if (blog_list[key_data[i]][7] and blog_list[key_data[i]][5]):
            keys_list.append(key_data[i])
    for i in range(len(key_data)-1,-1,-1):
        if (blog_list[key_data[i]][7] and not blog_list[key_data[i]][5]):
            keys_list.append(key_data[i])
            if (len(keys_list) >= 10):
                break
    display_list = {}
    for i in keys_list:
        display_list[i] = copy.deepcopy(blog_list[i])
        if (len(display_list[i][0])>15):
            display_list[i][0] = display_list[i][0][:15]+'...';
    return render_template("index.html",web_name=web_name,web_footer=web_footer,proclamation=markdown.markdown(web_proclamation),blog_list=display_list,user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)>=3):
            return redirect('/')
        return render_template("login.html",web_name=web_name,web_footer=web_footer,user=user)
    else:
        name = request.form.get("username")
        password = request.form.get("password")
        captcha = request.form.get("captcha")
        # print(name,password)
        # print(type(name),type(password))
        if (not "captcha" in session):
            error = "请刷新验证码后重试"
            return render_template("error.html", ERROR=error,web_name=web_name,web_footer=web_footer,user=user)
        if (captcha != session["captcha"]):
            del session["captcha"]
            error = "验证码错误"
            return render_template("error.html", ERROR=error,web_name=web_name,web_footer=web_footer,user=user)
        elif (check_acc(name,password,0)>=3):
            del session["captcha"]
            session["username"] = name
            session["password"] = password
            return redirect('/')
        else:
            del session["captcha"]
            error = "账号或密码错误"
            if (name in user and user[name].get("password")=="LoginNotAllowed"):
                error = "该账号已被禁止登录！"
            return render_template("error.html", ERROR=error,web_name=web_name,web_footer=web_footer,user=user)
        
@app.route("/unlogin", methods=["GET"])
def unlogin():
    if request.method == "GET":
        try:
            del session["username"]
            del session["password"]
        except:
            pass
        return redirect('/')

@app.route("/image/list", methods=["GET"])
def image():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10):
            get_list = {}
            if (username in image_list):
                get_list[username] = image_list[username];
            return render_template("image_list.html",web_name=web_name,web_footer=web_footer,image_list=get_list,user=user)
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/image/new", methods=["POST"])
def image_new():
    if request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10):
            captcha = request.form.get("captcha")
            if (not "captcha" in session):
                error = "请刷新验证码后重试"
                return render_template("error.html", ERROR=error,web_name=web_name,web_footer=web_footer,user=user)
            if (captcha != session["captcha"]):
                del session["captcha"]
                error = "验证码错误"
                return render_template("error.html", ERROR=error,web_name=web_name,web_footer=web_footer,user=user)
            file = request.files.get('photo')
            if file and allowed_file(file.filename):
                suffix = os.path.splitext(file.filename)[1]
                filename = random_string() + suffix
                if (image_list.get(username)):
                    image_list[username].append(filename);
                else:
                    image_list[username] = [filename]
                file.save(os.path.join(file_route+"static\\images", filename))
                updata_img();
                return redirect("/image/list")
            else:
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="不被允许的文件类型",user=user)
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/image/del", methods=["GET"])
def image_del():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10):
            file_user = request.args.get("user");
            file = request.args.get("file");
            if (file_user == None or file == None or (not file in image_list[file_user])):
                abort(404)
            if (check_acc(username,userpw,1)==10 or file_user == username):
                image_list[file_user].remove(file);
            else:
                abort(403)
            updata_img();
            return redirect("/image/list")
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/blog/list", methods=["GET"])
def blogl():
    if request.method == "GET":
        page = int(request.args.get('page', default=1))
        search_tag = request.args.get("tag", default="all")
        keyword = request.args.get("keyword", default="")
        if (not search_tag in blog_typel):
            search_tag = "all";
        dis_list = {}
        for i in blog_list:
            if (blog_list[i][7] and (search_tag == "all" or blog_list[i][4] == search_tag) and (keyword == "" or keyword.lower() in blog_list[i][0].lower() or keyword.lower() in blog_list[i][1].lower())):
                dis_list[i] = blog_list[i];

        if (len(dis_list)):
            key_data = list(dis_list.keys())
            keys_list = []
            for i in range(len(key_data)-1,-1,-1):
                if (dis_list[key_data[i]][5]):
                    keys_list.append(key_data[i])
            for i in range(len(key_data)-1,-1,-1):
                if (not dis_list[key_data[i]][5]):
                    keys_list.append(key_data[i])

            items_per_page = 10
            total_pages = len(keys_list) // items_per_page + (len(keys_list) % items_per_page > 0)
            if (page > total_pages):
                abort(404)

            start_index = (page - 1) * items_per_page
            end_index = min((page - 1) * items_per_page + items_per_page, len(keys_list))
            
            current_items = keys_list[start_index:end_index]

            display_list = {}
            for i in current_items:
                display_list[i] = dis_list[i]
        else:
            display_list = {}
            page = 1;
            total_pages = 1;

        return render_template("blog_list.html",web_name=web_name,web_footer=web_footer,blog_list=display_list,page=page,total_pages=total_pages,blog_type=blog_typel,search_tag=search_tag,keyword=keyword,user=user)

@app.route("/blog", methods=["GET"])
def blog(): 
    if request.method == "GET":
        username = userpw = None
        blogID = request.args.get("id");
        if (not blogID in blog_list):
            abort(404)
        topping = blog_list[blogID][5]
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10 or topping):
            blog_user = blog_list[blogID][2]
            blog_name = blog_list[blogID][0]
            blog_about = blog_list[blogID][1]
            blog_time = blog_list[blogID][3]
            blog_type = blog_list[blogID][4]
            hiding = blog_list[blogID][7]
            view_count = blog_list[blogID][6] = blog_list[blogID][6]+1
            if ((not blog_list[blogID][7]) and (not check_acc(username,userpw,1)==10) and (not blog_user==username)):
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="文章不可查看",user=user)
            if ((not blog_list[blogID][7]) and blog_user in user and check_acc(username,userpw,2)!=10 and user[blog_user].get("power")=="super"):
                abort(403)
            blogc = get_blog(blogID)
            if ("_ContentOnly" in request.args):
                return render_template("contentonly.html",content=blogc)
            return render_template("blog_templates.html",web_name=web_name,web_footer=web_footer,user=user,blogID=blogID,blog_about=blog_about,blogc=blogc,blog_name=blog_name,blog_user=blog_user,blog_time=blog_time,blog_type=blog_type,blog_typel=blog_typel,view_count=view_count,hiding=hiding)
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/blog/new", methods=["GET","POST"])
def blog_new():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10):
            return render_template("blog_new.html",web_name=web_name,web_footer=web_footer,blog_type=blog_typel,user=user)
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)
    elif request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        topping = False
        hiding = True
        if (check_acc(username,userpw,1)==10):
            topping = request.form.get("topping")
            if (topping == "on"):
                topping = True
            else:
                topping = False
            hiding = request.form.get("hiding")
            if (hiding == "on"):
                hiding = False
            else:
                hiding = True
        if (check_acc(username,userpw,0)==10):
            blogID = random_string()
            while (blogID in blog_list):
                blogID = random_string()
            blog_name = request.form.get("blog_name")
            blog_about = request.form.get("blog_about")
            blog_type = request.form.get("blog_type")
            blogc = request.form.get("blogc")
            blog_time = int(time.time())
            blog_name = legal(blog_name)
            blog_about = legal(blog_about)
            blogc = legal2(blogc)
            if ((not blog_type in blog_typel) or (blog_type == "admin" and check_acc(username,userpw,1)!=10)):
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="文章类型错误",user=user)
            if ((not check_long(blog_name,30)) or (not check_long(blog_about,50))):
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="文章名称、简介长度不合法",user=user)
            blog_list[blogID] = [blog_name,blog_about,username,blog_time,blog_type,topping,0,hiding]
            save_blog(blogID,blogc)
            return redirect(f"/blog?id={blogID}")
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/blog/change", methods=["GET","POST"])
def admin_blog():
    blogID = request.args.get("id")
    if (not blogID in blog_list):
        abort(404)
    blog_time = blog_list[blogID][3]
    blog_user = blog_list[blogID][2]
    topping = blog_list[blogID][5]
    hiding = not blog_list[blogID][7]
    view_count = blog_list[blogID][6]
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if ((not blog_list[blogID][7]) and (not check_acc(username,userpw,1)==10) and (not username == blog_user)):
            abort(403)
        if (check_acc(username,userpw,1)==10 or (username == blog_user and check_acc(username,userpw,0)==10)):
            blog_name = blog_list[blogID][0]
            blog_about = blog_list[blogID][1]
            blog_type = blog_list[blogID][4]
            blogc = get_blog(blogID)
            return render_template("blog_change.html",web_name=web_name,web_footer=web_footer,user=user,blogID=blogID,blog_name=blog_name,blog_about=blog_about,blogc=blogc,blog_user=blog_user,blog_time=blog_time,topping=topping,blog_typel=blog_typel,blog_type=blog_type,hiding=hiding)
        else:
            abort(403)
    elif request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            blog_user = request.form.get("blog_user")
            blog_time = request.form.get("blog_time")
            topping = request.form.get("topping")
            if (topping == "on"):
                topping = True
            else:
                topping = False
        if (check_acc(username,userpw,1)==10 or (username == blog_user and check_acc(username,userpw,0)==10)):
            blog_name = request.form.get("blog_name")
            blog_about = request.form.get("blog_about")
            blogc = request.form.get("blogc")
            blog_type = request.form.get("blog_type")
            blog_name = legal(blog_name)
            blog_about = legal(blog_about)
            blogc = legal2(blogc)
            hiding = request.form.get("hiding")
            if (hiding == "on"):
                hiding = False
            else:
                hiding = True
            if ((not blog_type in blog_typel) or (blog_type == "admin" and check_acc(username,userpw,1)!=10)):
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="文章类型错误",user=user)
            if ((not check_long(blog_name,30)) or (not check_long(blog_about,50))):
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="文章名称、简介长度不合法",user=user)
            blog_list[blogID] = [blog_name,blog_about,blog_user,blog_time,blog_type,topping,view_count,hiding]
            save_blog(blogID,blogc)
            return redirect(f"/blog?id={blogID}")
        else:
            abort(403)

@app.route("/blog/del", methods=["GET"])
def blog_del():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        blogID = request.args.get("id");
        if ((check_acc(username,userpw,0) and username == blog_list[blogID][2] and blog_list[blogID][7]) or check_acc(username,userpw,1)):
            if (blogID == None and (not blogID in blog_list)):
                abort(404)
            blog_list.pop(blogID)
            updata_blog()
            return redirect(request.referrer)
        else:
            abort(403)


@app.route("/user/<pageuser>", methods=["GET"])
def userpage(pageuser): 
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10 or (pageuser==username and check_acc(username,userpw,0)>2)):
            if (pageuser in user):
                key_data = list(blog_list.keys())
                keys_list = []
                for i in range(0,len(key_data)):
                    if ((blog_list[key_data[i]][7] or blog_list[key_data[i]][2]==username or (check_acc(username,userpw,1)==10 and check_acc(pageuser,user[pageuser].get("password"),2)!=10))\
                         and (blog_list[key_data[i]][5]) and (blog_list[key_data[i]][2]==pageuser)):
                        keys_list.append(key_data[i])
                for i in range(len(key_data)-1,-1,-1):
                    if ((blog_list[key_data[i]][7] or blog_list[key_data[i]][2]==username or (check_acc(username,userpw,1)==10 and check_acc(pageuser,user[pageuser].get("password"),2)!=10))\
                         and (not blog_list[key_data[i]][5]) and (blog_list[key_data[i]][2]==pageuser)):
                        keys_list.append(key_data[i])
                user_blog = {}
                for i in keys_list:
                    user_blog[i] = copy.deepcopy(blog_list[i])
                    if (len(user_blog[i][0])>15):
                        user_blog[i][0] = user_blog[i][0][:15]+'...';
                return render_template("user_templates.html",web_name=web_name,web_footer=web_footer,user=user,pageuser=pageuser,user_blog=user_blog,bio=user[pageuser].get("bio"))
            else:
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="找不到该用户",user=user)
        elif (check_acc(username,userpw,0)==3):
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="你已被封禁，申诉请联系管理员说明情况",user=user)
        else:
            return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="请先登录",user=user)

@app.route("/judgement", methods=["GET"])
def judgement_view(): 
    if request.method == "GET":
        view_ju = []
        for i in range(len(judgement)-1,max(len(judgement)-11,-1),-1):
            view_ju.append(judgement[i])
        return render_template("judgement.html",web_name=web_name,web_footer=web_footer,user=user,judgement=view_ju)

######################################################################################
#admin
######################################################################################

@app.route("/admin", methods=["GET"])
def admin():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            return render_template("admin.html",web_name=web_name,web_footer=web_footer,user=user)
        else:
            abort(403)

@app.route("/admin/setting", methods=["GET","POST"])
def web_setting():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,2)==10):
            return render_template("web_setting.html",web_name=web_name,web_footer=web_footer,web_proclamation=web_proclamation,user=user)
        else:
            abort(403)
    elif request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,2)==10):
            new_name = request.form.get("new_name")
            new_name = legal(new_name)
            new_footer = request.form.get("new_footer")
            new_footer = legal(new_footer)
            new_proclamation = request.form.get("new_proclamation")
            new_proclamation = legal(new_proclamation)
            save_setting(new_name,new_footer,new_proclamation)
            return render_template("web_setting.html",web_name=web_name,web_footer=web_footer,web_proclamation=web_proclamation,user=user)
        else:
            abort(403)

@app.route("/admin/upd", methods=["GET"])
def web_upd():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,2)==10):
            updata_data()       
            return redirect(request.referrer)
        else:
            abort(403)

@app.route("/admin/user", methods=["GET"])
def usermanage():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            return render_template("usermanage.html",user=user,web_name=web_name,web_footer=web_footer)
        else:
            abort(403)

@app.route("/admin/user/<uns>", methods=["GET","POST"])
def usersetting(uns):
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if ((check_acc(username,userpw,1)==10 and ((check_acc(uns,user[uns].get("password"),1)!=10) or check_acc(username,userpw,2)==10 or uns==username))):
            return render_template("usersetting.html",user=user,uns=uns,web_name=web_name,web_footer=web_footer)
        else:
            abort(403)
    elif request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if ((check_acc(username,userpw,1)==10 and ((check_acc(uns,user[uns].get("password"),1)!=10) or check_acc(username,userpw,2)==10 or uns==username))):
            new_power = request.form.get("power")
            new_pass = request.form.get("password")
            new_bio = request.form.get("bio")
            note = request.form.get("note")
            if (new_pass == "" and uns in user):
                new_pass = user[uns].get("password");
            new_pass = legal(new_pass)
            new_bio = legal(new_bio)
            note = legal(note)
            if (check_acc(username,userpw,2)!=10 and uns!=username):
                if (((new_power == "admin" or new_power=="super") and check_acc(username,userpw,2)!=10)):
                    abort(403)
            if (new_power != user[uns].get("power") or \
                (new_pass != user[uns].get("password") and new_pass=="LoginNotAllowed") or (new_pass != user[uns].get("password") and user[uns].get("password")=="LoginNotAllowed")):
                power_ch = ""
                if (new_power != user[uns].get("power")):
                    if (new_power == "super"):
                        power_ch += "- 身份组变更为 `超级管理员`\n"
                    elif (new_power == "admin"):
                        power_ch += "- 身份组变更为 `管理员`\n"
                    elif (new_power == "user"):
                        power_ch += "- 身份组变更为 `用户`\n"
                    elif (new_power == "banned"):
                        power_ch += "- 身份组变更为 `封禁用户`\n"

                if (new_pass != user[uns].get("password") and new_pass=="LoginNotAllowed"):
                    power_ch += "- 撤销 `登录账号` 权限\n"
                if (new_pass != user[uns].get("password") and user[uns].get("password")=="LoginNotAllowed"):
                    power_ch += "- 授予 `登录账号` 权限\n"
                judgement.append({"user":uns,"time":int(time.time()),"operator":username,"content":markdown.markdown(power_ch),"note":markdown.markdown(note)})
            user[uns] = {"power":new_power,"password":new_pass,"bio":new_bio}
            save_user()
            return redirect(request.referrer)
        else:
            abort(403)

@app.route("/admin/user/_new", methods=["GET","POST"])
def newuser():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            return render_template("user_new.html",user=user,web_name=web_name,web_footer=web_footer)
        else:
            abort(403)
    elif request.method == "POST":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            new_name = request.form.get("name")
            new_power = request.form.get("power")
            new_pass = request.form.get("password")
            new_bio = request.form.get("bio")
            if (not check_long(new_name,15)):
                return render_template("error.html",ERROR="用户名长度非法",web_name=web_name,web_footer=web_footer,user=user)
            if (new_name == "_new"):
                return render_template("error.html",ERROR="用户名非法",web_name=web_name,web_footer=web_footer,user=user)
            new_pass = legal(new_pass)
            new_bio = legal(new_bio)
            user[new_name] = {"power":new_power,"password":new_pass,"bio":new_bio}
            save_user()
            return redirect("/admin/user")
        else:
            abort(403)

@app.route("/admin/user/del/<uns>", methods=["GET"])
def deluser(uns):
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            if uns in user:
                user.pop(uns)
            else:
                return render_template("error.html",web_name=web_name,web_footer=web_footer,ERROR="找不到该用户",user=user)
            save_user()
            return redirect("/admin/user")
        else:
            abort(403)

@app.route("/admin/es/list", methods=["GET"])
def esmanage():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            return render_template("es_list.html",esl=esl,web_name=web_name,web_footer=web_footer,user=user)
        else:
            abort(403)

@app.route("/admin/image/list", methods=["GET"])
def admin_image():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,2)==10):
            return render_template("image_manage.html",web_name=web_name,web_footer=web_footer,image_list=image_list,user=user)
        else:
            abort(403)

@app.route("/admin/image/del", methods=["GET"])
def admin_image_del():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,0)==10):
            user = request.args.get("user");
            file = request.args.get("file");
            if (user == None or file == None or (not file in image_list[user])):
                abort(404)
            if (check_acc(username,userpw,1)==10 or user == username):
                image_list[user].remove(file);
            else:
                abort(403)
            updata_img();
            return redirect(-1)
        else:
            abort(403)

@app.route("/admin/blog/list", methods=["GET"])
def blog_manage():
    if request.method == "GET":
        username = userpw = None
        if (check_login()):
            username = session.get("username")
            userpw = session.get("password")
        if (check_acc(username,userpw,1)==10):
            key_data = list(blog_list.keys())
            keys_list = []
            for i in range(len(key_data)-1,-1,-1):
                keys_list.append(key_data[i])
            display_list = {}
            for i in keys_list:
                display_list[i] = blog_list[i]
            return render_template("blog_manage.html",web_name=web_name,web_footer=web_footer,user=user,blog_list=display_list,blog_type=blog_typel)
        else:
            abort(403)

if __name__ == '__main__':
    app.run(host=server_ip,port=server_port,debug=debug)