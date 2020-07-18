# Find-House

本项目主要是抓取使用者“房天下”或“58同城”网站上收藏的租房信息(初步，后续将进行拓展)。进行分析，找出最符合使用者需求的租房条件。利用这些租房条件到各大租房网站上抓取符合条件的房源，进行整合，以HTML页面的方式进行呈现。使用者亦可调用内置的方法进行收藏信息，房源信息的储存。

## 如何使用本工具

### 依赖安装

1. 安装[python3](https://www.python.org/downloads/)和Chrome浏览器
2. [安装与Chrome浏览器相同版本的驱动](http://chromedriver.storage.googleapis.com/index.html)
3. windows下只需pip install -r requirements.txt

### 工具运行

1. 进入 tools目录
2. 运行  main.py
3. 在打开的窗口点击对应按钮
4. 弹出的浏览器输入用户密码后会自动开始爬取数据**(只有在用户有对应信息的情况下才会进行下一步的爬取)**,爬取完成后将生成HTML页面并打开. 在对应的目录下可以查看下载下来的数据(xxx.html,xxx.json)
