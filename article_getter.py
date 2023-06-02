import requests
import xml.etree.ElementTree as ET
from ftplib import FTP 
import logging

class ArticleGetter:

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")


    def make_request(self, link):
        response = requests.get(link)
        if response.status_code == 200:
            logging.info(f"Made request to {link}")
        else: 
            logging.warning(f"Failed to make request to {link}")
            return None
        return ET.fromstring(response.text)

    def get_links(self, article_id):
        article_link = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={article_id}"
        root_node = self.make_request(article_link)
        if root_node is None:
            return None, None
        tgz_link = None
        pdf_link = None
        for tag in root_node.findall('records/record/link'):
            format = tag.attrib['format']
            value = tag.attrib['href']
            if(format == 'pdf'):
                pdf_link = value
            if(format == 'tgz'):
                tgz_link = value
        return tgz_link, pdf_link

    def split_link(self, link):
        link = link.partition('pmc/')[2]
        link_split = link.split('/')
        file_name = link_split[-1]
        link_split.pop(-1)
        directory = "/".join(link_split)
        return directory, file_name
    
    def download_file(self, link):
        directory, file_name = self.split_link(link)

        my_file = open(file_name, 'wb+') # Откройте локальный файл, чтобы сохранить загруженный файл
        logging.info(f'created file for {file_name}')  
        
        ftp = FTP('ftp.ncbi.nlm.nih.gov')
        ftp.login()
        ftp.cwd(f'/pub/pmc/{directory}/')
        logging.info('created ftp connection')

        logging.info(f'start download of file {file_name}')
        ftp.retrbinary('RETR ' + file_name, my_file.write, 33554432) # Введите имя файла для загрузки  
        logging.info(f'file {file_name} was downloaded')

        ftp.quit() # Завершить FTP-соединение  
        logging.info('closed ftp connection')

        my_file.close()
        logging.info(f'closed file {file_name}')

        return file_name
        
    def get_article(self, article_id):
        tgz_link, pdf_link = self.get_links(article_id)

        if(pdf_link is not None): 
            logging.info(f"File {article_id} has pdf link {pdf_link}")
            file_name = self.download_file(pdf_link)
            return 'pdf', file_name        
        elif(tgz_link is not None):
            logging.info(f"File {article_id} has tgz link {tgz_link}")
            file_name = self.download_file(tgz_link)
            return 'tgz', file_name
        else: 
            logging.info(f"File {article_id} has no links")
            return None, None
