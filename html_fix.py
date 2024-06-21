import os
import re
import glob
import shutil
from bs4 import BeautifulSoup


def html_fix(html_path, output_pth):
    """
    Исправляет ссылки на CSS файлы в HTML-файле и копирует соответствующие CSS файлы.

    Args:
    - html_path (str): Путь к HTML-файлу.
    - output_pth (str): Путь для сохранения исправленного HTML и CSS файлов.

    Исправляет ссылки на CSS файлы в HTML-файле, сохраняет его и копирует связанные CSS файлы в новый каталог.
    """
    html_name = os.path.basename(html_path)
    html_name = os.path.splitext(html_name)[0]
    css_folder_name = html_name[:4] + '_files'
    css_folder_path = f'{output_pth}/{css_folder_name}'

    os.makedirs(css_folder_path, exist_ok=True)

    with open(html_path, 'r', encoding='utf-8') as html_file:
        content = html_file.read()

    soup = BeautifulSoup(content, 'lxml')
    head_tag = soup.head
    for link_tag in head_tag.find_all('link', href=True):
        print(link_tag['href'])
        css_name = re.search(r'/([^/]+\.css)', link_tag['href'])
        if css_name:
            css_name = css_name.group(1)
            link_tag['href'] = f'./{css_folder_name}/{css_name}'
    fixed_content = str(soup)

    with open(
        f'{output_pth}/{html_name}.html', 'w', encoding='utf-8'
    ) as html_file:
        html_file.write(fixed_content)

    shutil.copytree(f'{folder_path}/{html_name}_files',
                    css_folder_path,
                    dirs_exist_ok=True)


if __name__ == '__main__':
    folder_path = 'parse_files'
    target_extension = '*.html'

    file_list = glob.glob(os.path.join(folder_path, target_extension))
    output_path = os.path.join(folder_path, 'result')
    for file_path in file_list:
        html_fix(file_path, output_path)
