import os
import re
import glob
from bs4 import BeautifulSoup
import quopri


def content_decode(encoded_text):
    """
    Декодирует закодированный текст в формате quoted-printable.

    Args:
    - encoded_text (str): Закодированный текст в формате quoted-printable.

    Returns:
    - str: Декодированный текст в формате UTF-8.
    """
    return quopri.decodestring(encoded_text.encode('utf-8')).decode('utf-8')


def mht2html(mht_path, output_pth):
    """
    Преобразует MHT-файл в HTML-файл и сохраняет связанные CSS файлы.

    Args:
    - mht_path (str): Путь к MHT-файлу.
    - output_pth (str): Путь для сохранения результатов.

    Создаёт HTML-файл и каталог с CSS файлами для MHT-файла.
    """
    file_name = os.path.basename(mht_path)
    html_name = os.path.splitext(file_name)[0]
    css_folder_name = file_name[:4] + '_files'
    css_folder_path = f'{output_pth}/{css_folder_name}'

    with open(mht_path, 'r') as mht_file:
        content = mht_file.read()

    pattern = re.compile(r'------MultipartBoundary--\w+----\n'
                         r'Content-Type: text/html\n'
                         r'Content-ID:.*?\n'
                         r'Content-Transfer-Encoding:.*?\n'
                         r'Content-Location:.*?\n\n'
                         r'(.*?)'
                         r'(?=------MultipartBoundary--\w+--|$)', re.DOTALL)

    html_match = pattern.search(content)

    if html_match:
        html_content = html_match.group(1).strip()
        html_content = content_decode(html_content)
        soup = BeautifulSoup(html_content, 'lxml')
        head_tag = soup.head
        for link_tag in head_tag.find_all('link', href=True):
            link_tag['href'] = (
                f'./{css_folder_name}/{os.path.basename(link_tag["href"])}'
            )
        fixed_html_content = str(soup)
        with open(f'{output_pth}/{html_name}.html',
                  'w',
                  encoding='utf-8') as html_file:
            html_file.write(fixed_html_content)

    css_pattern = re.compile(
        r'------MultipartBoundary--\w+----\n'
        r'Content-Type: text/css\n'
        r'Content-Transfer-Encoding:.*?\n'
        r'Content-Location:.*?/([^/]+\.css)\n\n'
        r'(.*?)'
        r'(?=------MultipartBoundary--\w+--|$)',
        re.DOTALL
    )
    css_matches = css_pattern.findall(content)

    if css_matches:
        os.makedirs(css_folder_path, exist_ok=True)
        for css_match in css_matches:
            css_name = css_match[0]
            css_content = content_decode(css_match[1])
            with open(f'{css_folder_path}/{css_name}',
                      'w',
                      encoding='utf-8') as css_file:
                css_file.write(css_content.strip())


if __name__ == "__main__":
    target_extension = '*.mht'
    folder_path = 'parse_files'

    file_list = glob.glob(os.path.join(folder_path, target_extension))
    output_path = os.path.join(folder_path, 'result')
    for file_path in file_list:
        mht2html(file_path, output_path)
