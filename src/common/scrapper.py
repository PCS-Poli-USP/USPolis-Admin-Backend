import json
import requests
from bs4 import BeautifulSoup
import re

def extract_subjects_info(table):
    tr_elements = table.find_all("tr")

    subject_type = "Obrigatória"
    period = "1"

    subjects = []

    for tr in tr_elements:

        # encontra o tipo de disciplina
        if tr.get("bgcolor") == "#658CCF":
            text = tr.td.get_text(strip=True).strip()
            clean_text = re.sub(r'\s+', ' ', text)
            subject_type = clean_text.split(" ")[1][:-1]
            
        # encontra o periodo
        if tr.get("bgcolor") == "#CCCCCC":
            td_text = tr.find("td").get_text(strip=True)
            period = re.search(r"\d+", td_text).group()

        # encontra as disciplinas
        if tr.find("a", class_="link_gray"):
            td_elements = tr.find_all("td")
            code = re.sub(r'\s+', ' ', td_elements[0].get_text(strip=True))
            name = re.sub(r'\s+', ' ', td_elements[1].get_text(strip=True))

            subjects.append({
                "subject_type": subject_type,
                "period": period,
                "code": code,
                "name": name,
            })

    return subjects

def get_programs():
    BASE_URL = "https://uspdigital.usp.br/jupiterweb/"
    PROGRAMS_URL = f"{BASE_URL}jupCursoLista?codcg=3&tipo=N"

    page = requests.get(PROGRAMS_URL)
    soup = BeautifulSoup(page.content, "html5lib")

    tables = soup.select("table")
    tables = [tables[3], tables[5], tables[7]]

    # obtem todos os cursos da Poli
    tr_data = []
    for table in tables:
        tr_elements = table.find_all("tr")[1:]  # Ignore the first <tr> element

        for tr in tr_elements:
            td_elements = tr.find_all("td")
            if len(td_elements) >= 2:
                # Get the href from the first <td>
                first_td = td_elements[0]
                a_tag = first_td.find("a", class_="link_gray")
                tr_href = a_tag["href"] if a_tag else None

                # Get the text from the second <td>
                second_td = td_elements[1]
                tr_text = second_td.get_text(strip=True)

                tr_data.append({"text": tr_text, "href": tr_href})

    # remove entradas que nao tem um link para a pagina de grade curricular
    tr_data = [d for d in tr_data if d.get("href") is not None]

    # vai a cada grade curricular para obter as disciplinas
    for data in tr_data:
        page = requests.get(f"{BASE_URL}{data.get('href')}")
        soup = BeautifulSoup(page.content, "html5lib")

        try:
            target_table = soup.select("table")[-2]
        except IndexError:
            data["subjects"] = []
            continue

        subjects = extract_subjects_info(target_table)
        data["subjects"] = subjects

    with open('json_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(tr_data, outfile)

if __name__ == "__main__":
    get_programs()
