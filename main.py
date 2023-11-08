import os
import sys
import platform
from pathlib import Path
from contextlib import contextmanager
from multiprocessing import Process
from celery import Celery
from mitmproxy.tools.main import mitmdump
from selenium.webdriver import Chrome, ChromeOptions
from utils import check_port, check_connect


app = Celery('quora-distributed-crawl', include=['tasks.get_answers', 'tasks.get_question_url', 'tasks.demo'])
app.config_from_object('config')


def open_proxy(port):
    print(f'Proxy Port: {port}')
    mitmdump(['-s', './proxy_script.py', '-p', str(port), '-q'])


def build_chrome_driver(port):
    options = ChromeOptions()
    # 隐藏自动化特征
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # 无头模式
    # options.add_argument("--headless")
    # 不加载图片，提升运行速度
    # options.add_argument('blink-settings=imagesEnabled=false')
    # 证书异常
    options.add_argument('--ignore-certificate-errors')
    # 设置代理
    proxy_server = f'127.0.0.1:{port}'
    # print(f'Browser Proxy: {proxy_server}')
    options.add_argument(f'--proxy-server={proxy_server}')

    driver = Chrome(options=options)
    driver.implicitly_wait(6)

    @contextmanager
    def new_tab_get(url):
        # driver.switch_to.new_window('tab')
        driver.get(url)
        yield driver
        driver.quit()
        # driver.switch_to.window(driver.window_handles[0])

    return new_tab_get


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    if platform.system().lower() == 'windows':
        os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
        print('Forked by multiprocessing = 1')

    if not check_connect.is_connectable():
        print('Unable to connect to www.quora.com.')
        sys.exit(1)
    else:
        print('Can connect to www.quora.com.')

    # 启动代理进程
    proxy_port = check_port.check_increment(8000)
    os.environ['selenium_proxy_port'] = str(proxy_port)
    proxy = Process(target=open_proxy, args=(proxy_port,), daemon=True)
    proxy.start()
    proxy.join(3)

    # 准备就绪的浏览器对象
    chrome_browser = build_chrome_driver(proxy_port)
    with chrome_browser('https://www.quora.com/search?q=hello&type=question'):
        input('Press enter to quit')

    app.start(['-A', 'main', 'worker', '--loglevel=info'])
