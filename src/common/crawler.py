import requests
from bs4 import BeautifulSoup
import re


def get_jupiter_class_infos(subject_code):
    URL = f"https://uspdigital.usp.br/jupiterweb/obterTurma?nomdis=&sgldis={subject_code}"
    table1_names = ['cod_turma', 'inicio', 'fim', 'tipo', 'obs']
    table2_names = ['dia_semana', 'hora_inicio', 'hora_fim', 'prof']
    table3_names = ['tipo_vaga', 'vagas', 'inscritos', 'pendentes', 'matriculados']

    # attributes used to identify the <div>s containing the classes informations
    class_div_attr = {
        "style" : "border: 2px solid #658CCF; padding: 5px; border-radius: 5px;"
    }
    table3_filter = {
        'tag' : 'span',
        'attrs' : {'class' : 'txt_arial_8pt_black'}
    }

    out = []

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    subject = soup.find_all('b', text=re.compile('Disciplina:(.*)'))[0]
    subject_name = subject.get_text().replace(f'Disciplina: {subject_code} - ', '')

    class_div = soup.find_all("div", attrs=class_div_attr)

    for c_info in class_div:

        info_table = c_info.find_all("table")

        info1 = parse_table(info_table[0], orientation='hor', labels=table1_names)
        info2 = parse_table(info_table[1], orientation='vert', labels=table2_names)
        info3 = parse_table(info_table[2], orientation='vert', labels=table3_names, filter=table3_filter)

        out.append(
            {
                'cod_disciplina' : subject_code,
                'nome_disciplina' : subject_name,
                'cod_turma' : info1['cod_turma'][0],
                'inicio' : info1['inicio'][0],
                'fim' : info1['fim'][0],
                'tipo' : info1['tipo'][0],
                #'obs' : info1['obs'][0],
                'prof' : info2['prof'],
                'dia_semana' : info2['dia_semana'],
                'hora_inicio' : info2['hora_inicio'],
                'hora_fim' : info2['hora_fim'],
                'vagas' : list( [int(x) if x.isdigit() else 0 for x in info3['vagas']] ),
                'inscritos' : list( [int(x) if x.isdigit() else 0 for x in info3['inscritos']] ),
                'pendentes' : list( [int(x) if x.isdigit() else 0 for x in info3['pendentes']] )
            }
        )


    return out

def parse_table(table, orientation='vert', labels=[], filter=None):
    if orientation == 'vert':
        return parse_vertical_table(table, labels, filter)
    elif orientation == 'hor':
        return parse_horizontal_table(table, labels, filter)


def parse_horizontal_table(table, labels=[], filter=None):
    out_dict = {}
    rows = table.find_all("tr")

    for i in range(len(rows)):
        if filter == None:
            data = rows[i].find_all("td")
        else:
            data = rows[i].find_all(filter['tag'], attrs=filter['attrs'])

        out_dict[labels[i]] = [val.get_text(strip=True) for val in data[1:] if (val.get_text(strip=True) != '')]

    return out_dict




def parse_vertical_table(table, labels=[], filter=None):
    out_dict = {}
    rows = table.find_all("tr")

    names=[]
    for col in labels:
        out_dict[col] = []

    for i in range(1, len(rows)): #skip the first row of labels
        if filter == None:
            data = rows[i].find_all("td")
        else:
            data = rows[i].find_all(filter['tag'], attrs=filter['attrs'])


        for j in range(len(data)):
            data_text = data[j].get_text(strip=True)
            if data_text != '':
                out_dict[labels[j]].append(data_text)

    return out_dict
