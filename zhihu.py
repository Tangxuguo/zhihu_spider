#!/usr/bin/env python
#!encoding:utf-8
#!filename:zhihu_to_evernote.py
import os
import time
import re
import sys
import requests
import configparser
import smtplib
import traceback
#import urllib2
from BeautifulSoup import BeautifulSoup
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart


#===========================================================================
def Login_Zhihu(email,password):
    """先登录知乎网站之后才能访问"我关注的问题"列表
    """

    zhihu_login = r"http://www.zhihu.com/login"
    
    
    global zhihu_status
    global zhihu_session
    
    zhihu_session = requests.Session() #用requests设置cookie
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0)\
        Gecko/20100101 Firefox/24.0",
        "Referer":"http://www.zhihu.com/login"
            }

    #提交账号密码
    logininfo = {"email":email,
                "password":password,
                "sign-button":"登录"}
   
    print logininfo
    #post登录知乎网站
    login = zhihu_session.post(zhihu_login,data=logininfo, headers=headers, timeout=10)
    #print (post.text)
    print login
    print login.text
    if login.status_code == 200: #判断是否post成功
        html_text = login.text
        #登录成功会出现下面字符
        login_status = "zg-icon-dd-home"
        if re.search(login_status, html_text) != None:#判断登录状态
            print ("Login Success")
            zhihu_status = "Login Success"

        else:
            print ("Login Failure")
            zhihu_status = "Login Failure"
            #login_status = "zg-icon-dd-home"
            #if re.search(login_status, html_text) != None:#判断是否需要验证码
            #    relogin()
    else: 
        zhihu_status = "Login Failure"
        
    return  zhihu_status    

#===========================================================================
def get_question_url(url):
    """
    接收用户输入的知乎收藏页面地址、提取所有分页的url地址存入列表中
    通过正则表达式匹配内容并提取出来所有分页地址的url
    @url_list_regex :提取URL规则、如果为空说明本页已没收藏的文章
    @page_url       :用于存放所有分页url
    """
    
    global page_url
    global question_url
    page_url = []
    single_page_url = []
    question_url = []
    

        
    for i in range(1, 1000):
            
        # 通过知乎页面规则来增加后面的分页数量、
        # http://www.zhihu.com/collection/20261977?page=2 就表示第二页、以此类推。
        url_temp = url + "?page=" + str(i)
       
        r = requests.get(url_temp)
        if r.status_code == 200:
            # 用正则表达式去匹配是否有收藏内容，如果有则添加到列表中，否则循环中断
            url_list_regex = r"(<h2 class.*href=\")(/\w+/\d+)(\">)(.*)(</a></h2>)"  # 匹配问题页面/question/20685509
                 
            single_page_url = re.findall(url_list_regex, r.text)
            
            if len(single_page_url):  
                page_url.append(url_temp)  # 将单页面地址url提取出来增加到page_url总表中
                     
                for x in single_page_url:  # 将单页面问题地址url提取出来增加到url总表中
                    #question_url:http://www.zhihu.com/question/21606800
                    question_url.append("http://www.zhihu.com" + x[1])
                    print "http://www.zhihu.com" + x[1]
                    print len(question_url)
            else:
                print ("No Next Page")
                print len(question_url)
                break
                 
                    # soup = BeautifulSoup(r.text)
                    # soup.find("div", { "class" : "zm-invite-pager" }).string
    return question_url
   

#===========================================================================
def get_answer_url(url):
    """
    接收用户输入的知乎问题页面地址、提取所有答案的-url地址存入列表中
    如 http://www.zhihu.com/question/19915290
    返回http://www.zhihu.com/question/19915290/answer/15757929
    
    
    """
    answer_url=[]
    print url
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        #soup.prettify()
        soup = BeautifulSoup(html_text)
        soup_list=soup.findAll("div",attrs={"class":"zm-item-answer ",})
        
        #获取前20个答案
        for i in range(len(soup_list)):
            
            #answer_id= re.findall(url_list_regex, r.text)
            data_aid = soup_list[i]['data-aid']
            data_atoken =soup_list[i]['data-atoken']
            data_created=soup_list[i]['data-created']
            
            
            #获取答案页面data-atoken:22268855
            #answer_url:http://www.zhihu.com/question/21606800/answer/22268855
            answer_url_temp =url+"/answer/"+data_atoken
            answer_url.append(answer_url_temp)
            
            
            #获取赞同用户data-aid:4108367
            #构造:http://www.zhihu.com/node/AnswerFullVoteInfoV2?params=%7B%22answer_id%22%3A%224108367%22%7D
            get_vote_user_url(data_aid)
            
            
            
            
            #print get_votes
    print answer_url        
    return answer_url
        
#=============================================================================
def Email_zhihu_content(url):
    """
    接收输入的单个收藏页面的URL地址、然后提取title、并将其作为邮件主题。
    用requests.get()下载页面内容、然后用smtplib发送html内容到
    Evernote的邮件地址中，Evernote会自动添加到笔记本中.
    @title_name_regex   :提取问答的title
    @subject            :用于作为邮件主题
    @

    """
    #提取问题的标题，并将其作为邮件的主题
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        #soup.prettify()
        soup = BeautifulSoup(html_text)
        title_name = soup.title.string
        print (title_name)

        #设置邮件主题
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(title_name + notebook,"utf-8") 
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        part = MIMEText(html_text,"html",'utf-8') #设置以html格式发送内容
        msg.attach(part)
        
        #发送邮件
        smtp = smtplib.SMTP()
        smtp.connect(mail_host) 
        smtp.login(mail_user,mail_password) 
        smtp.sendmail(mail_user,evernote_mail,msg.as_string()) 
        smtp.quit()

#===========================================================================
def get_vote_user_url(data_aid):
    """
    接收用户输入的知乎答案页面地址的data_aid、提取所有用户的-url地址存入列表中
    
    
    """
    get_votes_url="http://www.zhihu.com/node/AnswerFullVoteInfoV2?params=%7B%22answer_id%22%3A%22"+data_aid+"%22%7D"
    get_votes=requests.get(get_votes_url)
    user_soup = BeautifulSoup(get_votes.text)  
    
    #不含匿名用户
    user_soup_list=user_soup.findAll("a")
    for user_count in range(len(user_soup_list)):
        #print user_soup_list[user_count]
        
        #user_index:http://www.zhihu.com/people/zhang-gu-du  user_name:张孤独  user_token:[u'zhang-gu-du']
        user_index="http://www.zhihu.com"+user_soup_list[user_count]["href"]
        user_name=user_soup_list[user_count]["title"]
        url_token=re.findall("/people/(.*)",user_soup_list[user_count]["href"])
        url_token=url_token[0]
        #print user_index,user_name,url_token
        get_user_information(url_token)
        #获取用户其他信息
   
    #含匿名用户
    user_soup_list_total=user_soup.findAll("li")
            
    print get_votes_url
    print len(user_soup_list)
    print len(user_soup_list_total)




#===========================================================================
def get_user_information( url_token):
    """
    接收用户个人token、提取所有需要的信息存入列表中
    
    """
    #获取用户信息,昵称,性别,回答,文章,关注,
           
    user_simple_url="http://www.zhihu.com/node/MemberProfileCardV2?params=%7B%22url_token%22%3A%22"+url_token+"%22%7D"
    print user_simple_url
    try:
        get_user = requests.get(user_simple_url)
    
        if get_user.status_code == 200:
            soup = BeautifulSoup(get_user.text)
            user_name=soup.findAll("span")[0].string
            if len(soup.findAll("i")):
                user_gender=re.findall("zg-icon (.*)",soup.findAll("i")[0]['class'])
            else:
                user_gender=None
            user_reply=soup.findAll("div",attrs={'class':"value"})[0].string
            user_article=soup.findAll("div",attrs={'class':"value"})[1].string
            user_follower=soup.findAll("div",attrs={'class':"value"})[2].string
            user_index="http://www.zhihu.com/people/"+url_token
            print user_name,user_gender,user_reply,user_article,user_follower,user_index
        
    except:
        #捕获错误,打印到日志
        f=open("log.txt",'a')
        f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"/n")
        traceback.print_exc(file=f)
        f.flush()
        f.close
        #屏幕显示
        info=sys.exc_info()
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),":" ,info[0],":" ,info[1]
        print "error"
#===========================================================================
def send_to_mysql(data):
    """
    把收集的数据发送到数据库
    
    """

#===========================================================================

def analysis_data(url):
    """ 
   分析数据
    
    """
#===========================================================================   
def get_question_beautiful_url(url):
    """
    接收用户输入的知乎收藏页面地址、提取所有分页的url地址存入列表中
    通过正则表达式匹配内容并提取出来所有分页地址的url
    @url_list_regex :提取URL规则、如果为空说明本页已没收藏的文章
    @page_url       :用于存放所有分页url
    """
    
    global page_url
    global question_url
    page_url = []
    single_page_url = []
    question_url = []
    print url

        
    for i in range(1, 1000):
            
        # 通过知乎页面规则来增加后面的分页数量、
        # http://www.zhihu.com/collection/20261977?page=2 就表示第二页、以此类推。
        url_temp = url + "?page=" + str(i)
        print url_temp
        r = requests.get(url_temp)
        if r.status_code == 200:
            # 用正则表达式去匹配是否有收藏内容，如果有则添加到列表中，否则循环中断
            url_list_regex = r"(<h2 class.*href=\")(/\w+/\d+)(\">)(.*)(</a></h2>)"  # 匹配问题页面/question/20685509   
            single_page_url = re.findall(url_list_regex, r.text)
            
            soup = BeautifulSoup(r.text)
            soup_list=soup.findAll("a",href=re.compile("\?page=\d+"))
            print soup_list
            
            soup_list=soup.findAll("a",attrs={"href":re.compile("\?page=\d+"),"href":True},limit=20,text=re.compile("2"))
            print soup_list
            #print soup_list.contents
            #print soup_list.span
            #print soup_list.span.nextSibling
            print len(single_page_url) 
            if len(single_page_url):  
                page_url.append(url_temp)  # 将单页面地址url提取出来增加到page_url总表中
                       
                for x in single_page_url:  # 将单页面问题地址url提取出来增加到url总表中
                    question_url.append("http://www.zhihu.com" + x[1])
                    print "http://www.zhihu.com" + x[1]
                    print len(question_url)
            else:
                print ("No Next Page")
                print len(question_url)
                break
 
    return question_url
   
#=============================================================================

if __name__ == "__main__":
    
    global zhihu_status
    global zhihu_session
    global url_list
    url_list = []
    #从配置文件读取内容
    cf = configparser.ConfigParser()
    cf.read("config.ini")
    url = cf.get("info","url")
    #print url
    mail_host = cf.get("info","mail_host")
    mail_user = cf.get("info","mail_user")
    mail_password = cf.get("info","mail_password")
    evernote_mail = cf.get("info","evernote_mail")
    notebook = "@" + cf.get("info","notebook")
    zhihu_email = cf.get("info", "zhihu_email")
    zhihu_password = cf.get("info", "zhihu_password")

    #判断是否填写知乎账号
    zhihu_email= "no"
    if zhihu_email != "no":
        follow_url = "http://www.zhihu.com/question/following"
        print ("Follow")
        zhihu_status=Login_Zhihu(zhihu_email,zhihu_password)
        if zhihu_status == "Login Success": #判断是否登录成功
            question_url=get_question_url(url) 
            for i in question_url:
                print (i)
                #Email_zhihu_content(i)
        else:
            print (zhihu_status)

    else:
        
        question_url=get_question_url(url)
        
        print (len(question_url))
        for x in question_url: #循环所有的单页收藏文章url列表
            print (x)
            #Email_zhihu_content(x)
            
            get_answer_url(x)
