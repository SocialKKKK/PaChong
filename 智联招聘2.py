from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import sys



def get_keyword_encoded(position):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 如果需要隐藏浏览器窗口，可以取消注释
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.zhaopin.com")

    # 等待搜索框加载
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-wrapper__input"))
    )

    # 输入搜索关键词
    search_box.send_keys(position)

    # 使用 JavaScript 触发搜索按钮点击
    driver.execute_script("document.querySelector('.search-wrapper__button').click();")

    # 获取所有打开的窗口句柄
    all_windows = driver.window_handles

    # 切换到新打开的窗口
    driver.switch_to.window(all_windows[-1])

    # 等待新页面加载完成
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    # 获取当前URL
    url = driver.current_url
    print(f"搜索后的URL: {url}")

    # 解析 URL 获取 keyword_encoded
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')

    # 查找路径中包含 "kw" 的部分
    keyword_encoded = None
    for part in path_parts:
        if part.startswith('kw'):
            keyword_encoded = part[2:]  # 提取 "kw" 后面的编码部分
            break

    if keyword_encoded:
        print(f"提取的 keyword_encoded: {keyword_encoded}")
    else:
        print("未能提取到 keyword_encoded")

    # 关闭浏览器
    driver.quit()

    return keyword_encoded


# 使用 Selenium 获取页面源码
def get_html(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 如果需要隐藏浏览器窗口，可以取消注释
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )

    try:
        # 初始化 Selenium WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # 访问指定的URL
        driver.get(url)

        # 等待几秒钟以确保页面完全加载
        time.sleep(2)

        # 获取页面源码
        page_source = driver.page_source

        # 关闭浏览器
        driver.quit()

        # 返回页面源码
        return page_source
    except Exception as e:
        print(f"获取页面源码失败: {e}")
        return None


def get_html_list(city_code, keyword_encoded, num_pages):
    html_list = []

    for i in range(1, num_pages + 1):
        # 构建URL
        url = f"https://www.zhaopin.com/sou/jl{city_code}/kw{keyword_encoded}/p{i}"
        html = get_html(url)
        if html:
            time.sleep(2)  # 增加等待时间，确保页面加载完成
            soup = BeautifulSoup(html, 'html.parser')
            jobs = soup.find_all(name='div', attrs={'class': 'joblist-box__iteminfo'})
            if not jobs:
                print(f'未找到职位信息: 页码 {i}, URL: {url}')
            html_list.extend([str(job) for job in jobs])
        else:
            print(f'无法获取HTML内容: 页码 {i}, URL: {url}')

    return html_list

def get_csv(html_list):
    # 初始化各字段的列表
    cities, positions, company_names, company_sizes, company_types, company_industries, salaries, educations, abilities, experiences = ([] for i in range(10))

    for html in html_list:
        soup = BeautifulSoup(html, 'html.parser')

        # 提取城市信息、工作经验和学历要求
        info_tags = soup.find_all('div', class_='jobinfo__other-info-item')
        if len(info_tags) >= 3:
            city = info_tags[0].find('span').get_text(strip=True) if info_tags[0].find('span') else ' '
            experience = info_tags[1].get_text(strip=True)
            education = info_tags[2].get_text(strip=True)
        else:
            city = ' '
            experience = ' '
            education = ' '

        # 提取职位名称
        position_tag = soup.find('a', class_='jobinfo__name')
        position = position_tag.get_text(strip=True) if position_tag else ' '

        # 提取公司名称
        company_tag = soup.find('a', class_='companyinfo__name')
        company_name = company_tag.get_text(strip=True) if company_tag else ' '

        # 提取公司规模、公司类型和公司行业
        company_info_tags = soup.find('div', class_='companyinfo__tag')
        if company_info_tags:
            company_info_list = company_info_tags.find_all('div')
            if len(company_info_list) >= 3:
                company_type = company_info_list[0].get_text(strip=True)
                company_size = company_info_list[1].get_text(strip=True)
                company_industry = company_info_list[2].get_text(strip=True)
            elif len(company_info_list) == 2:
                company_size = company_info_list[0].get_text(strip=True)
                company_industry = company_info_list[1].get_text(strip=True)
                company_type = ' '
            else:
                company_type = ' '
                company_size = ' '
                company_industry = ' '
        else:
            company_type = ' '
            company_size = ' '
            company_industry = ' '

        # 提取薪资信息
        salary_tag = soup.find('p', class_='jobinfo__salary')
        salary = salary_tag.get_text(strip=True) if salary_tag else ' '

        # 提取技能要求
        skill_tags = soup.find('div', class_='jobinfo__tag')
        skills = ' '.join(tag.get_text(strip=True) for tag in skill_tags.find_all('div', class_='joblist-box__item-tag')) if skill_tags else ' '

        # Append data to lists
        cities.append(city)
        positions.append(position)
        company_names.append(company_name)
        company_sizes.append(company_size)
        company_types.append(company_type)
        company_industries.append(company_industry)
        salaries.append(salary)
        educations.append(education)
        abilities.append(skills)
        experiences.append(experience)

    # 将所有列表打包成一个表格
    table = list(zip(cities, positions, company_names, company_sizes, company_types, company_industries, salaries, educations, abilities, experiences))

    return table



if __name__ == '__main__':

    # 从命令行参数中获取职位名称
    if len(sys.argv) < 2:
        print("请提供职位名称作为参数")
        sys.exit(1)

    position = sys.argv[1]
    print(f"正在处理职位: {position}")

    # position = 'Java工程师'
    keyword_encoded = get_keyword_encoded(position)
    citys = {'上海': 538, '北京': 530, '广州': 763, '深圳': 765, '天津': 531, '武汉': 736, '西安': 854, '成都': 801,
             '南京': 635, '杭州': 653, '重庆': 551, '厦门': 682}
    for city, city_num in citys.items():
        html_list = get_html_list(city_num,keyword_encoded,1)
        table = get_csv(html_list)
        print(table)
        df = pd.DataFrame(table, columns=['city', 'position', 'company_name', 'company_size', 'company_type',
                                          'company_industry', 'salary', 'education', 'ability', 'experience'])
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df.to_csv(file_name, index=False, encoding='utf-8')


