####zhihu_spider

**一个知乎爬虫，可以抓取收藏夹所有问题及内容，获取问题页面所有用户信息（包括主页地址。性别，回答数，赞同数等），并做入库处理

知乎登录和配置部分参考http://www.hiadmin.org/code/zhihu_to_evernote_3
项目地址：https://github.com/huaisha1224/zhihu_to_evernote

在此基础上增加了部分信息，修改成python2.7版本**

###安装第三方库

- 1、安装requests 2.1.0版本的第三方库
- 2、安装BeautifulSoup 4.2版本的第三方库

###使用说明

- 1、修改config.ini里面的内容为自己真实信息
- 2、然后命令行下python zhihu.py即可

		python zhihu.py

###配置文件config.ini说明

	[info]
	url = http://www.zhihu.com/collection/20261977
	mail_host = smtp.126.com
	mail_user = huaisha******@126.com
	mail_password = password
	evernote_mail=huaisha*****@m.yinxiang.com
	notebook = 知乎收藏文章
	zhihu_email = no
	zhihu_password = no

**字段解释**

	[info]
	;知乎收藏页面的URL地址
	url = http://www.zhihu.com/collection/20261977
	;发送邮件的服务器
	mail_host = smtp.126.com
	;发送邮件的Email地址
	mail_user = huaisha****@126.com
	;登陆密码
	mail_password = password
	;接收邮件的Evernote地址
	evernote_mail=huaisha***@m.yinxiang.com
	;evernote上的一个笔记本、所有的收藏文章都会添加到这个笔记本下面，需要先有此笔记本
	notebook = 知乎收藏文章
	;下面2项为知乎账号密码/如果你需要吧"我关注的问题"也发送到Evernote那么填上账号密码,
	如果是把知乎收藏发送到Evernote的话下面2项请填写no
	zhihu_email = no
	zhihu_password = no


