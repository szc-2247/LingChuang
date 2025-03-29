from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta, time
import geocoder
import socket
import openai
import requests
import time as time_module
import tkinter as tk
from bs4 import BeautifulSoup
import json



plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示为黑体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

DEEPSEEK_API_KEY = "sk-fdc6a02e984c4781b7c2d1e913f8806d"


class SmartAgricultureSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("智农兴商———智慧农业乡村振兴系统")
        self.root.geometry("1000x600")
        self.create_search_bar()

        # 全局变量
        self.image_path = None

        # 创建顶部信息栏
        self.create_top_info_bar()

        # 创建 Notebook 用于切换功能
        self.create_notebook()

        # 初始化显示
        self.show_current_moisture()
        self.update_time()
        self.update_location()  # 初始化时获取并显示当前地点
        self.update_ip()  # 初始化时获取并显示当前 IP
        self.create_weather_frame()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def create_search_bar(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        search_label = tk.Label(search_frame, text="搜索一下")
        search_label.pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_button = tk.Button(search_frame, text="搜索", command=self.search_webpage)
        search_button.pack(side=tk.RIGHT, padx=10)

    def create_weather_frame(self):


        # 创建当天天气数据展示区域
        self.today_weather_frame = tk.Frame(self.weather_frame)
        self.today_weather_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建未来7天天气数据展示区域
        self.future_weather_frame = tk.Frame(self.weather_frame)
        self.future_weather_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 获取并展示天气数据的按钮
        weather_button = tk.Button(self.weather_frame, text="获取并展示天气数据", command=self.show_weather_data)
        weather_button.pack(side=tk.TOP, padx=10, pady=5)

    def on_close(self):
        self.clear_files()
        self.root.destroy()

    def clear_files(self):
        file_paths = ["weather1.txt", "weather7.txt"]
        for file_path in file_paths:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.truncate()
            except FileNotFoundError:
                pass

    def getHTMLtext(self, url):
        """请求获得网页内容"""
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            print("成功访问")
            return r.text
        except:
            print("访问错误")
            return " "

    def get_content(self, html):
        """处理得到有用信息保存数据文件"""
        final = []  # 初始化一个列表保存数据
        bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
        body = bs.body
        data = body.find('div', {'id': '7d'})  # 找到div标签且id = 7d
        # 下面爬取当天的数据
        data2 = body.find_all('div', {'class': 'left-div'})
        text = data2[2].find('script').string
        text = text[text.index('=') + 1:-2]  # 移除改var data=将其变为json数据
        jd = json.loads(text)
        dayone = jd['od']['od2']  # 找到当天的数据

        # 反转列表，使其从 0 点开始
        dayone = dayone[::-1]

        final_day = []  # 存放当天的数据
        for i in dayone:
            temp = []
            temp.append(i['od21'])  # 添加时间
            temp.append(i['od22'])  # 添加当前时刻温度
            temp.append(i['od24'])  # 添加当前时刻风力方向
            temp.append(i['od25'])  # 添加当前时刻风级
            temp.append(i['od26'])  # 添加当前时刻降水量
            temp.append(i['od27'])  # 添加当前时刻相对湿度
            temp.append(i['od28'])  # 添加当前时刻空气质量
            final_day.append(temp)

        # 下面爬取7天的数据
        ul = data.find('ul')  # 找到所有的ul标签
        li = ul.find_all('li')  # 找到所有的li标签
        final = []  # 存放未来7天的数据
        for day in li[1:8]:  # 跳过第一天，从第二天开始
            temp = []
            date = day.find('h1').string  # 得到日期
            date = date[0:date.index('日')]  # 取出日期号
            temp.append(date)
            inf = day.find_all('p')  # 找出li下面的p标签
            temp.append(inf[0].string)  # 天气
            temp.append(inf[1].find('i').string[:-1])  # 最低气温
            if inf[1].find('span'):
                temp.append(inf[1].find('span').string[:-1])  # 最高气温
            else:
                temp.append(None)
            wind = [span['title'] for span in inf[2].find_all('span')]  # 风向
            temp.extend(wind)
            wind_scale = inf[2].find('i').string  # 风级
            temp.append(int(wind_scale[wind_scale.index('级') - 1:wind_scale.index('级')]))
            final.append(temp)

        return final_day, final

    def write_to_txt(self, file_name, data, day=7):
        """保存为txt文件"""
        with open(file_name, 'a', errors='ignore', encoding='utf-8') as f:
            if day == 7:
                header = ['日期', '天气', '最高气温', '最低气温', '风向1', '风向2', '风级']
            else:
                header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度', '空气质量']
            # 写入表头
            f.write('\t'.join(header) + '\n')
            for row in data:
                # 将每行数据转为字符串并用制表符连接
                row_str = '\t'.join(map(str, row))
                f.write(row_str + '\n')

    def show_weather_data(self):
        # 天气地址
        url1 = 'http://www.weather.com.cn/weather/101181001.shtml'  # 7天天气中国天气网

        html1 = self.getHTMLtext(url1)
        data1, data1_7 = self.get_content(html1)  # 获得1-7天和当天的数据

        self.write_to_txt('weather1.txt', data1, 1)
        self.write_to_txt('weather7.txt', data1_7, 7)

        # 展示txt内容
        self.display_txt_content('weather1.txt', self.today_weather_frame)
        self.display_txt_content('weather7.txt', self.future_weather_frame)

    def display_txt_content(self, file_path, frame):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text_widget = tk.Text(frame, font=("", 12), bg="#f0f0f0", bd=0, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, content)
        except FileNotFoundError:
            pass

    def display_txt_content(self, file_path, frame):
        try:
            # 读取文件内容
            headers, data = self.read_txt_file(file_path)
            # 根据文件路径判断表名
            if 'weather1.txt' in file_path:
                table_name = "当天天气数据"
            elif 'weather7.txt' in file_path:
                table_name = "未来7天天气数据"
            else:
                table_name = "天气数据"
            # 创建表格标题
            self.create_table_title(frame, table_name)
            # 创建 Treeview 表格
            self.create_table(frame, headers, data)
        except FileNotFoundError:
            pass

    def read_txt_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            headers = lines[0].strip().split('\t')
            data = [line.strip().split('\t') for line in lines[1:]]
        return headers, data

    def create_table_title(self, frame, table_name):
        title_label = tk.Label(frame, text=table_name, font=("", 14, "bold"))
        title_label.pack(pady=5)

    def create_table(self, frame, headers, data):
        tree = ttk.Treeview(frame, columns=headers, show='headings')
        # 设置列标题
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=100)
        # 插入数据
        for row in data:
            tree.insert('', 'end', values=row)
        tree.pack(fill=tk.BOTH, expand=True)

    def search_webpage(self):
        keyword = self.search_entry.get()
        if keyword:
            url = f"https://cn.bing.com/search?q={keyword}&qs=n&form=QBRE&sp=-1&lq=0&pq={keyword}&sc=15-3&sk=&cvid=B020E58B3B17479D897A8051D14F96BD&ghsh=0&ghacc=0&ghpl="  # 使用微软进行搜索
            webbrowser.open(url)

    def create_top_info_bar(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.time_label = tk.Label(top_frame, text="当前时间：--", font=("", 14))  # 原来没设置字体大小，这里设置为14，可按需调整
        self.time_label.pack(side=tk.LEFT)
        self.location_label = tk.Label(top_frame, text="当前地点：-", font=("", 14))  # 增大字体大小
        self.location_label.pack(side=tk.LEFT, padx=20)
        self.ip_label = tk.Label(top_frame, text="当前登录 IP：-", font=("", 14))  # 增大字体大小
        self.ip_label.pack(side=tk.LEFT, padx=20)
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.weather_frame = tk.Frame(self.notebook)
        self.notebook.add(self.weather_frame, text="***天气预报***")
        # 土壤湿度数据可视化功能
        self.soil_frame = tk.Frame(self.notebook)
        self.notebook.add(self.soil_frame, text="***土壤湿度数据***")
        self.create_soil_frame()

        # 农作物疾病识别功能
        self.disease_frame = tk.Frame(self.notebook)
        self.notebook.add(self.disease_frame, text="***农作物疾病识别***")
        self.create_disease_frame()

        # 对话功能模块
        self.chat_frame = tk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="***对话功能——已接入 deepseek - V3  满血版***")
        self.create_chat_frame()



    def create_soil_frame(self):
        # 创建中间数据展示区域
        middle_frame = tk.Frame(self.soil_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.current_label = tk.Label(middle_frame, text="当前土壤相对湿度：--%", font=("", 30),
                                      fg="blue")  # 原来24，这里增大到30
        self.current_label.pack(pady=20)
        self.progress = ttk.Progressbar(middle_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack()
        # 创建底部按钮区域
        bottom_frame = tk.Frame(self.soil_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        history_button = tk.Button(bottom_frame, text="查看历史数据", command=self.show_history_chart)
        history_button.pack(side=tk.LEFT, padx=10)
        refresh_button = tk.Button(bottom_frame, text="刷新当前数据", command=self.show_current_moisture)
        refresh_button.pack(side=tk.LEFT)

        # 创建历史数据图表展示区域
        self.history_frame = tk.Frame(self.soil_frame)
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_disease_frame(self):
        # 创建顶部按钮区域
        disease_top_frame = tk.Frame(self.disease_frame)
        disease_top_frame.pack(fill=tk.X, padx=10, pady=5)
        upload_button = tk.Button(disease_top_frame, text="上传图片", command=self.upload_image)
        upload_button.pack(side=tk.LEFT, padx=10)
        recognize_button = tk.Button(disease_top_frame, text="开始识别", command=self.recognize_image)
        recognize_button.pack(side=tk.LEFT, padx=10)
        refresh_button = tk.Button(disease_top_frame, text="刷新", command=self.refresh)
        refresh_button.pack(side=tk.LEFT, padx=10)
        exit_button = tk.Button(disease_top_frame, text="退出", command=self.root.destroy)
        exit_button.pack(side=tk.LEFT, padx=10)

        # 创建中间图片展示区域
        disease_middle_frame = tk.Frame(self.disease_frame)
        disease_middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.image_label = tk.Label(disease_middle_frame)
        self.image_label.pack()

        # 创建识别结果区域
        result_frame = tk.Frame(self.disease_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        self.result_label = tk.Label(result_frame, text="识别结果：")
        self.result_label.pack()

        # 创建识别正确概率区域
        confidence_frame = tk.Frame(self.disease_frame)
        confidence_frame.pack(fill=tk.X, padx=10, pady=5)
        self.confidence_label = tk.Label(confidence_frame, text="识别正确概率：")
        self.confidence_label.pack()

        # 创建防治措施区域（带滚动条的文本框）
        measures_frame = tk.Frame(self.disease_frame, borderwidth=2, relief=tk.GROOVE, padx=10, pady=10)
        measures_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加垂直滚动条
        scrollbar = tk.Scrollbar(measures_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 添加文本框
        self.measures_text = tk.Text(measures_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.measures_text.pack(fill=tk.BOTH, expand=True)

        # 关联滚动条和文本框
        scrollbar.config(command=self.measures_text.yview)

    def create_chat_frame(self):
        # 聊天记录显示区域
        self.chat_history = tk.Text(self.chat_frame, wrap=tk.WORD, font=("", 12))  # 增加字体大小设置
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输入框
        input_frame = tk.Frame(self.chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.input_entry = tk.Entry(input_frame, font=("", 12))  # 增加字体大小设置
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        send_button = tk.Button(input_frame, text="发送", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=10)

        # 绑定 Enter 键事件
        self.input_entry.bind("<Return>", lambda event: self.send_message())

        # 添加保存聊天记录的按钮
        save_button = tk.Button(self.chat_frame, text="保存聊天记录", command=self.save_chat_history)
        save_button.pack(side=tk.LEFT, padx=10, pady=5)

        # 添加加载聊天记录的按钮
        load_button = tk.Button(self.chat_frame, text="加载聊天记录", command=self.load_chat_history)
        load_button.pack(side=tk.LEFT, padx=10, pady=5)



    # 模拟土壤湿度数据
    def generate_soil_moisture_data(self):
        # 获取当前日期
        today = datetime.today()
        # 生成从五天前到昨天的正序日期列表
        dates = [
            (today - timedelta(days=5) + timedelta(days=i)).date()  # 从五天前开始递增
            for i in range(5)  # 连续生成5天
        ]
        # 将日期格式化为字符串
        dates = [date.strftime("%Y-%m-%d") for date in dates]
        # 随机生成湿度数据
        moisture_levels = [random.randint(40, 80) for _ in range(5)]
        return dates, moisture_levels

    # 显示历史数据图表
    def show_history_chart(self):
        try:
            dates, moisture_levels = self.generate_soil_moisture_data()
            fig, ax = plt.subplots()
            ax.plot(dates, moisture_levels, marker='o')
            ax.set_xlabel('日期')
            ax.set_ylabel('土壤湿度 (%)')
            ax.set_title('土壤湿度历史数据')
            ax.grid(True)

            # 将图表嵌入到 Tkinter 窗口中
            canvas = FigureCanvasTkAgg(fig, master=self.history_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        except Exception as e:
            messagebox.showerror("错误", f"显示历史数据图表时出错：{e}")

    # 显示当前土壤湿度
    def show_current_moisture(self):
        current_moisture = random.randint(40, 80)
        self.current_label.config(text=f"当前土壤相对湿度：{current_moisture}%")
        self.progress['value'] = current_moisture

    # 更新当前时间
    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"当前时间：{now}")
        self.root.after(1000, self.update_time)

    # 获取并更新当前地点
    def update_location(self):
        try:
            # 尝试使用不同的服务获取位置信息
            g = geocoder.ipinfo('me')  # 使用 ipinfo 服务
            if not g.ok:
                g = geocoder.geocodefarm('me')  # 如果 ipinfo 服务失败，尝试 geocodefarm 服务
            if g.ok:
                location = g.city or g.town or g.country or "未知地点"
                self.location_label.config(text=f"当前地点：商丘市 梁园区")
                # self.location_label.config(text=f"当前地点：{location}")
            else:
                self.location_label.config(text="当前地点：无法获取位置信息")
        except:
            self.location_label.config(text="当前地点：无法获取位置信息")
        self.root.after(60 * 1000, self.update_location)  # 每隔 60 秒尝试更新一次位置信息

    # 获取并更新当前 IP
    def update_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.ip_label.config(text=f"当前登录 IP：{ip}")
        except Exception:
            self.ip_label.config(text="当前登录 IP：无法获取 IP 信息")
        self.root.after(60 * 1000, self.update_ip)  # 每隔 60 秒尝试更新一次 IP 信息

    # 保存聊天记录到文件
    def save_chat_history(self):
        # 提供默认文件名，格式为年月日
        default_filename = datetime.now().strftime("%Y-%m-%d") + ".txt"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return  # 如果用户取消保存，则直接返回

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                # 获取聊天记录文本并写入文件
                chat_text = self.chat_history.get("1.0", tk.END)
                file.write(chat_text)
            messagebox.showinfo("成功", f"聊天记录已保存到 {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存聊天记录时出错：{e}")

    # 加载聊天记录文件
    def load_chat_history(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return  # 如果用户取消加载，则直接返回

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                chat_text = file.read()
            self.chat_history.delete("1.0", tk.END)  # 清空当前聊天记录
            self.chat_history.insert(tk.END, chat_text)  # 加载聊天记录
            messagebox.showinfo("成功", f"聊天记录已加载：{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"加载聊天记录时出错：{e}")
    # 模拟识别功能
    def simulate_recognition(self, image_path):
        diseases = ["小麦叶枯病"]
        disease = random.choice(diseases)
        confidence = random.uniform(0.7, 0.99)
        return disease, confidence

    # 上传图片并显示预览
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            messagebox.showinfo("提示", "未选择任何图片")
            return
        self.image_path = file_path
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
            self.image_label.pack(pady=20)
            self.result_label.config(text="识别结果：")
            self.confidence_label.config(text="识别正确概率：")
            self.measures_text.delete(1.0, tk.END)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片：{e}")

    # 开始识别
    def recognize_image(self):
        if not self.image_path:
            messagebox.showinfo("提示", "请先上传图片")
            return
        try:
            disease, confidence = self.simulate_recognition(self.image_path)
            self.result_label.config(text=f"识别结果：{disease}")
            self.confidence_label.config(text=f"识别正确概率：{confidence:.2f}")
            self.display_measures(disease)
        except Exception as e:
            messagebox.showerror("错误", f"识别图片时出错：{e}")

    # 刷新
    def refresh(self):
        self.image_label.config(image=None)
        self.image_label.pack_forget()
        self.result_label.config(text="识别结果：")
        self.confidence_label.config(text="识别正确概率：")
        self.measures_text.delete(1.0, tk.END)
        self.image_path = None

    # 显示防治措施
    def display_measures(self, disease):
        self.measures_text.delete(1.0, tk.END)
        measures = (
            "化学防治\n"
            "药剂拌种和种子消毒\n"
            "主要药剂有 25% 三唑酮（粉锈宁）可湿性粉剂 75g，拌麦种 100kg 闷种；\n"
            "75% 萎锈灵可湿性粉剂 250g，拌麦种 100kg 闷种；\n"
            "50% 多福混合粉（25% 多菌灵 + 25% 福美双）500 倍液，浸种 48 小时；\n"
            "50% 多菌灵可湿性粉剂、70% 甲基硫菌灵（甲基托布津）可湿性粉剂、40% 拌种灵可湿性粉剂、40% 拌种双可湿性粉剂等 4 种药剂，\n"
            "均按种子重量 0.2% 拌种，其中拌种灵和拌种双易产生药害，使用时要严格控制剂量，避免湿拌。\n"
            "有条件的地区，也可使用种子重量 0.15% 的噻菌灵（涕必灵）（有效成分）、0.03% 的三唑醇（羟锈宁）（有效成分）拌种，\n"
            "控制效果均较好 。\n"
            "\n"
            "喷药\n"
            "重病区，可在小麦分蘖前期，每亩用 70% 代森锰锌可湿性粉剂 143 克或 75% 百菌清可湿性粉剂 15 克（均加水 50 - 75 升），\n"
            "或 65% 代森锌可湿性粉剂 1000 倍液或 1:1:140 波尔多液进行喷药保护，每隔 7 - 10 天喷洒 1 次，共喷 2 - 3 次。\n"
            "也可在小麦挑旗期顶三叶病情达 5% 时，亩用 25% 或 50% 苯菌灵可湿性粉剂 17 - 20 克（有效成分）或 25% 丙环唑乳油 33 毫升，\n"
            "加水 50 - 75 升喷雾，每隔 14 - 28 天喷 1 次，共喷 1 - 3 次，可有效地控制小麦叶枯病的流行为害 。"
        )
        self.measures_text.insert(tk.END, f"针对{disease}的防治措施：\n{measures}")

    # 调用 DeepSeek API
    def call_deepseek_api(self, message):
        try:
            today = datetime.now().strftime("%Y-%m-%d %A %H:%M:%S")
            client = openai.OpenAI(
                api_key="sk-fdc6a02e984c4781b7c2d1e913f8806d",
                base_url="https://api.deepseek.com",
                timeout=100
            )

            # 直接读取天气文件
            try:
                with open('weather1.txt', 'r', encoding='utf-8') as f1:
                    today_weather = f1.read()
                with open('weather7.txt', 'r', encoding='utf-8') as f7:
                    future_weather = f7.read()
                with open('dirt.txt', 'r', encoding='utf-8') as dirt:
                    dirt_message = dirt.read()
            except FileNotFoundError:
                today_weather = "未知"
                future_weather = "未知"
                dirt_message = "未知"


            # 构建系统消息
            system_message = (
                f"你是一个商丘师范学院信息技术学院的翎创游戏研发社团所研发的一个名字叫'小农'的农业专家助手，"
                f"你在与用户聊天时，可以适当的使用颜文字，并且不能失去专业水准."
                f"今天是{today}，今天的天气是：{today_weather}\n未来七天的天气是：{future_weather}"
                f"检测的土壤湿度数据为：{dirt_message}"
            )

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            return "未收到有效响应"

        except requests.exceptions.RequestException as e:
            return f"网络请求失败：{str(e)}"
        except openai.APIConnectionError as e:
            return f"API连接异常：{str(e)}"
        except openai.APIError as e:
            return f"API返回错误：{str(e)}"
        except Exception as e:
            return f"未预期错误：{str(e)}"

    # 发送消息
    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.chat_history.insert(tk.END, f"你：{message}\n")
            self.input_entry.delete(0, tk.END)
            thinking_text = "DeepSeek（农业专家助手）：正在思考...\n"
            self.chat_history.insert(tk.END, thinking_text)
            self.chat_history.update()

            start_time = time_module.time()
            response = self.call_deepseek_api(message)
            end_time = time_module.time()
            elapsed_time = round(end_time - start_time, 2)

            self.chat_history.delete(self.chat_history.index(f"end - {len(thinking_text)}c"), tk.END)
            self.chat_history.insert(tk.END, f"eepSeek（农业专家助手）：（已思考{elapsed_time}秒）{response}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartAgricultureSystem(root)
    root.mainloop()