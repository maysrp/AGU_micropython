import wifimgr
import ntptime
import network,time,requests,json,gc
from machine import SPI, Pin,I2C,Timer,freq,RTC,WDT
from driver import st7789_spi
from lib.easydisplay import EasyDisplay

#心知天气API私钥请自行申请,城市拼音请自行设置
KEY="SFBgZ_NMzMaWbjrXW"
CITY="shanghai"

#字体颜色信息
GREEN=0xF0F
RED=0xF10
BLACK=0x000
LINE=20

# 配置信息CPU，读取股票JSON
freq(240000000)
f=open("config.json","r")
info=json.loads(f.read())
f.close()



#天气查询
def weather(key,city):
        url="http://api.seniverse.com/v3/weather/now.json?key=%s&location=%s&language=zh-Hans&unit=c" % (key,city)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE' }
        ba=[]
        print(url)
        re=requests.get(url,headers=headers)
        my=re.json()
        weather_status=["晴","晴","晴","晴","多云","晴间多云","晴间多云","大部多云","大部多云","阴","阵雨","雷阵雨","雷阵雨伴有冰雹","小雨","中雨","大雨","暴雨","大暴雨","特大暴雨","冻雨","雨夹雪","阵雪","小雪","中雪","大雪","暴雪","浮尘","扬沙","沙尘暴","强沙尘暴","雾","霾","风","大风","飓风","热带风暴","龙卷风","冷","热","未知"]
        code=my['results'][0]['now']['code']#天气代码
        tep=my['results'][0]['now']['temperature']#温度
        return [tep,code,weather_status[int(code)]]

# 股票查询
class gp(object):
    def __init__(self,code="000858",ty="sz"):
        self.code=str(code)
        self.ty=ty
        self.get_url()
        self.get_info()
    def get_url(self):
        init_url="http://qt.gtimg.cn/q="
        self.url=init_url+self.ty+str(self.code)
    def get_info(self):
        try:
            self.re_obj=requests.get(self.url)
            self.tr_info()
            return self.re_obj
        except:
           return False
    def tr_info(self):
        d=self.re_obj.content
        li=d.split(b"~")
        self.name=li[1] #编码问题 无法str
        self.now=li[3]
        self.yestday=li[4]
        self.start=li[5]
        self.ud=li[31] #涨跌
        self.rate=li[32] #涨跌率
        self.top=li[33]
        self.down=li[34]
        self.buy_n=li[36]
        self.buy_m=li[37] #万元
        self.change=li[38] #成交率
        
#LCD 初始化
spi = SPI(1, baudrate=60000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(8))
dp = st7789_spi.ST7789(width=320, height=240, spi=spi, cs=2, dc=4, res=6, rotate=2, bl=1,invert=False, rgb=False)

sm= EasyDisplay(display=dp, font="/text_full_16px_2312.v3.bmf", show=True, color=0xFFFF, auto_wrap=True, clear=True,color_type="RGB565")
bg = EasyDisplay(display=dp, font="/text_full_24px_2312.v3.bmf", show=True, color=0xFFFF, auto_wrap=True, clear=True,color_type="RGB565")
bg.clear()



# wifi 配网

bg.text("WIFI连接中.....", 0, 30 ,clear=False,color=0xD1D)
sm.text("连接WIFI:WifiManager 密码:12345678", 0, 70 ,clear=False,color=0xCCD)
sm.text("打开浏览器连接:http://192.169.4.1", 0, 120 ,clear=False,color=0xCCD)
wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass

#显示LCD信息
bg.clear()
bg.text("WIFI:"+wlan.config("essid"), 0, 0 ,clear=False,color=0xAAA)
bg.text("IP:"+wlan.ifconfig()[0], 0, 32 ,clear=False,color=0xBBB)
bg.text("管理页面:", 0, 64 ,clear=False,color=0xDDD)
sm.text("http://"+wlan.ifconfig()[0]+":5000", 0, 96 ,clear=False,color=0xBBB)
print("ESP OK")

#NTP更新，datetime
def datetime():
#     返回UTC0
    date=time.localtime(time.time()+28800)
    #(2024, 4, 29, 9, 58, 14, 0, 120) 年 月 日 时 分 秒 周 全年的第几天
    return date
# 定义NTP服务器列表
ntp_servers = [
    'ntp.ntsc.ac.cn',
    'ntp1.aliyun.com',
    'ntp.tencent.com',
    'pool.ntp.org'
]

def ntp(ntp_servers):
    for server in ntp_servers:
        try:
            # 尝试从当前服务器同步时间
            ntptime.host = server
            ntptime.settime()
            print("时间已从 {} 同步".format(server))
            return
        except Exception as e:
            print("从 {} 同步时间失败: {}".format(server, e))
            continue
    print("无法从任何服务器同步时间")

ntp(ntp_servers)
hour=datetime()[3]



#日期天气
def show_day(t=False):
    key=KEY
    city=CITY
    global hour
    dt=datetime()
    time_str=str(dt[0])+"-"+str(dt[1])+"-"+str(dt[2])+" "+str(dt[3])+":"+str(dt[4])
    if (hour-dt[3])!=0 or t:
        hour=dt[3]
        ntp(ntp_servers)
        try:
            ty=weather(key,city)
            weather_str=ty[0]+"度 "+ty[2]
            bg.text(weather_str, 200,202  ,clear=False,color=0x0FF)
        except:
            pass
    bg.text(time_str, 0,202  ,clear=False,color=0xECC)
    gc.collect()
   


#股票查询显示
def show_gp_info(info):
    k=0
    for i in info:
        sm.text(info[i][1], 0, k*LINE ,clear=False,color=0xFFF)
        sm.text(info[i][2], 60, k*LINE ,clear=False,color=0xAFA)
        k=k+1

def show_gp_now(t=False):
    if t:
        print("第一次执行") 
    else:
        print("定时器执行")
        if (datetime()[6] not in [0,1,2,3,4])or(datetime()[3] not in [9,10,11,13,14]):
            print("非股票交易时间不执行")
            return False
   
    print("第一次执行查询")
    k=0
    for i in info:
        if t:
            sm.text("                   ",135, k*LINE ,clear=False,color=BLACK)
        m=gp(info[i][1],info[i][0])
        if float(m.ud.decode())>=0:
            color=RED
        else:
            color=GREEN
        sm.text(m.now.decode(), 135, k*LINE ,clear=False,color=color)
        sm.text(m.ud.decode(), 190, k*LINE ,clear=False,color=color)
        sm.text(m.rate.decode()+"%", 240, k*LINE ,clear=False,color=color)
        k=k+1


time.sleep(3)
bg.clear()

#股票信息 60秒更新股票信息   
show_gp_info(info)
show_gp_now(True)
tim=Timer(0)
tim.init(mode=Timer.PERIODIC, period=60000, callback=lambda x:show_gp_now(False))

# 天气情况 55秒更新时间 1小时更新天气
show_day(True)
weather_tim=Timer(1)
weather_tim.init(mode=Timer.PERIODIC, period=55000, callback=lambda x:show_day(False))

#喂狗 10秒限制 5秒一次
wdt=WDT(timeout=22000)
tdog=Timer(2)
tdog.init(mode=Timer.PERIODIC, period=10000, callback=lambda x:wdt.feed())



# 设置网络股票配置
from microdot import Microdot, send_file

app = Microdot()

@app.route('/')
async def index(request):
    return send_file('g.html')


@app.route('/all', methods=['GET', 'POST'])
async def all_index(req):
    a={}
    a['info']=info
    a['status']=True
    return a

@app.route('/del', methods=['GET', 'POST'])
async def del_index(req):
    ty = req.form.get('ty')
    name = req.form.get('name')
    code = req.form.get('code')
    try:
        del info[code]
        f=open("config.json","w")
        f.write(json.dumps(info))
        f.close()
        bg.clear()
        show_gp_info(info)
        show_gp_now(True)
        show_day(True)
        return {"status":True}
    except:
        return {"status":False}

@app.route('/add', methods=['GET', 'POST'])
async def add_index(req):
    ty = req.form.get('ty')
    name = req.form.get('name')
    code = req.form.get('code')
    add_info=[ty,code,name]
    info[code]=add_info
    if len(info)>10:
        ke=list(info.keys())
        del info[ke[0]]
    f=open("config.json","w")
    f.write(json.dumps(info))
    f.close()
    a={}
    a['status']=True
    a['info']=add_info
    bg.clear()
    show_gp_info(info)
    show_gp_now(True)
    show_day(True)
    return a


app.run(debug=True)
