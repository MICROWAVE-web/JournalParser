import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from time import sleep
from dataclasses import dataclass
import csv
from tqdm import tqdm
# geckodriver_path = r'C:/Users/ktoto/Documents/geckodriver.exe'

url = 'https://paperity.org'


@dataclass
class Data:
    name: str
    link: str
    RSS: str
    ISSN: str
    Publisher: str
    Subjects: str

    def unpack(self):
        return [self.name, self.link, self.RSS, self.ISSN, self.Publisher, self.Subjects]


class Parser:
    data = []

    def __init__(self):
        self.driver = uc.Chrome()
        self.driver.get('https://paperity.org/journals/1')
        sleep(5)
        while func := self.parse_all_jornals():
            sleep(2)
        self.driver.quit()
        self.write_data()

    def parse_all_jornals(self):
        links_class = self.driver.find_elements(By.CLASS_NAME, 'color-blue')
        links = [i.find_element(By.TAG_NAME, 'a') for i in links_class]
        for link in tqdm(links):
            link.click()
            sleep(2)
            page = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'row')))
            page_html = page.get_attribute('innerHTML')
            soup = BeautifulSoup(page_html, 'html.parser')
            name = soup.h1.text
            link = soup.find('a', attrs={'rel': "nofollow"})['href']
            rss = url + soup.find('a', 'btn btn-primary width-100')['href']
            info_panel = soup.find('div', 'panel panel-body panel-sidebar bg-blue bg-blue hidden-xs')
            self.get_info(name, link, rss, info_panel)
            self.driver.execute_script('window.history.go(-1)')  # возврат на страницу с журналами
            sleep(2)
        try:
            next_button = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.pagination:nth-child(1) > li:nth-child(3) > a:nth-child(1)')))
        except:
            return False
        sleep(0.5)
        next_button.click()
        sleep(1)
        return True

    def get_info(self, name, link, rss, info_panel):
        info_text = info_panel.text
        info = info_panel.find_all('dd')
        if 'ISSN' in info_text:
            issn = info.pop(0).text
        else:
            issn = '-'
        if 'Publisher' in info_text:
            publisher = info.pop(0).text
        else:
            publisher = '-'
        if 'Subject(s)' in info_text:
            subjects = info.pop(0).text
        else:
            subjects = '-'
        self.data.append(Data(name, link, rss, issn, publisher, subjects))

    def write_data(self):
        with open('result.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in self.data:
                writer.writerow(i.unpack())


if __name__ == '__main__':
    parser = Parser()
