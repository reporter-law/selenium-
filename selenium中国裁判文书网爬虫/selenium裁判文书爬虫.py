"""程序说明"""
# -*-  coding: utf-8 -*-
# Author: cw
# Datetime : 2020
# software: PyCharm
# 收获:整体思路：通过全国区县、以及相应关键词进行限制以突破文书网只能显示600条的限制
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import math
import time
from datetime import datetime
import logging
import pyautogui

"""日志记录"""
logging.disable(logging.DEBUG)
def start_logger():
    """日志初始化设置、文件名（时间）、DEBUG为调试级别(级别导致输出内容的不同）、日志的记录格式、日期格式"""
    logging.basicConfig(
        filename='daily_report_%s.log' %datetime.strftime(datetime.now(), '%m%d%Y_%H%M%S'),
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%m-%d %H:%M:%S')
start_logger()


def content_change(county,index_,keyword,keyword_1):
    """主要的爬取函数"""
    global index
    # 无图:加快速度
    profile = FirefoxProfile()
    profile.set_preference('browser.migration.version', 9001)
    profile.set_preference('permissions.default.image', 2)
    browser = webdriver.Firefox(profile)
    """网页获取"""
    try:
        browser.get('http://wenshu.court.gov.cn')
        wait = WebDriverWait(browser, 20)
        """传入第一个参数，需要自行选择"""
        send = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="_view_1540966814000"]/div/div[1]/div[2]/input')))
        send.send_keys(str(keyword_1))
        time.sleep(1)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_view_1540966814000"]/div/div[1]/div[3]')))
        button.click()
        try:
            """关键字传入"""
            click1 = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="search-middle"]/input')))
            click1.clear()
            click1.send_keys(str(keyword))
            button1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="search-rightBtn search-click"]')))
            button1.click()
            click1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_view_1545034775000"]/div/div[1]/div[1]')))
            click1.click()

            """优化为：高级检索 ，发送country："""
            send1 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="s2"]')))
            send1.send_keys(county)
            button_1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchBtn"]')))
            button_1.click()

            """文书数量：15"""
            button_ = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="left_7_3"]/div/select')))
            button_.click()
            button_ = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="left_7_3"]/div/select/option[3]')))
            button_.click()

            """目的：进行页数遍历，减少遍历次数，"""
            condition = browser.find_element_by_xpath('//div[@class="LM_con clearfix"]/div[@class="fr con_right"]/span')
            logging.info(condition.text)
            conditions = math.ceil(int(condition.text) / 15)
            logging.info("一共%d页-----------------------------"%conditions)#输出当前检索条件下有多少页数
            """对于不同页数进行不同处理，超过40页的就需要更改条件进行再次筛选，保存下来了当前超过40页的参数"""
            if int(condition.text) == 0:
                browser.quit()
            elif int(conditions) > 40:  # condition本身已经除了15
                with open('超过600页.txt', 'a+', encoding='utf-8')as file:
                    file.write('出现超过600条的裁判文书,其所在区域为：' + str(county) + '，其数量为：' + str(condition.text) + str(keyword) + '\n')
                logging.warning('出现超过600条的裁判文书,其所在区域为：' + str(county) + '，其数量为：' + str(condition.text)+ str(keyword) + '\n')
            else:
                for index in range(conditions):
                    """由于不明原因而需要两次移动"""
                    try:
                        '''全选的点击'''
                        click_1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="LM_tool clearfix"]/div[4]/a[1]/label')))
                        click_1.click()
                        '''批量下载的点击'''
                        click_2 = wait.until(EC.presence_of_element_located((By.XPATH, '//html/body/div/div[4]/div[2]//div[@class="LM_tool clearfix"]/div[4]/a[3]')))
                        click_2.click()
                        """弹出框确认点击"""
                        pyautogui.moveTo(505, 410)
                        pyautogui.click()
                        pyautogui.moveTo(765, 465)
                        pyautogui.click()
                        print('第%d页下载成功============================================' % index)
                        browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                        """下一页的点击"""
                        button_ = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="left_7_3"]/a[last()]')))
                        button_.click()
                        """需要设置等待时间以便下一页刷新过来，根据网络速度进行调节"""
                        time.sleep(1)
                    except:
                        logging.info('第%d页出现缺失,出现问题的城市为： ' % index + str(county))
        except:
            print('第%d页出现缺失,出现问题的城市为： ' % index + str(county))
            index_ += 1
            browser.quit()
        """退出显得频繁是为了在异常时能够退出，否者异常不退出导致页面太多，系统中断"""
        browser.quit()
    except:
        logging.info("成功退出------------------------2---------------------------------")
        browser.quit()

def main(keyword,keyword_1):
    """主函数遍历页数,传入区县进行遍历以突破600页的限制"""
    path = r'J:\PyCharm项目\项目\selenium中国裁判文书网爬虫\城市.txt'
    with open(path,'r',encoding='utf-8')as f:
        contents = f.readlines()
        index_ = 0
        for i in contents:
            try:
                content_change(i.strip(),index_,keyword,keyword_1)
            except:
                print("成功退出-------------------------3--------------------------------")
                browser = webdriver.Firefox()
                browser.quit()

if __name__ == "__main__":
    """两个需要传入的参数"""
    keywords=['故意',"数罪"]
    keyword_1 = "认罪认罚"
    for keyword in keywords:
        main(keyword,keyword_1)

