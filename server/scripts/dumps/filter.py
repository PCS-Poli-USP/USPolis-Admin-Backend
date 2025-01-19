import csv


# Função para processar e converter o dump para CSV
def dump_to_csv(dump_file: str, csv_file: str) -> None:
    with open(dump_file, "r", encoding="utf-8") as file:  # noqa: UP015
        lines = file.readlines()

    # Aqui você pode ajustar a lógica para filtrar os dados de interesse
    # Por exemplo, procurando os dados após a instrução COPY
    inside_copy = False
    data = []

    for line in lines:
        # Detectar quando começa a leitura dos dados após o COPY
        if line.startswith("COPY public.classroom"):
            inside_copy = True
            continue  # Ignora a linha COPY

        # Finaliza quando encontra a linha que encerra o COPY
        if line.startswith("\\."):
            inside_copy = False
            continue  # Ignora a linha de fim de COPY

        # Processa as linhas de dados dentro do COPY
        if inside_copy:
            # Limpa a linha de qualquer excesso de espaços ou caracteres desnecessários
            cleaned_line = line.strip()
            if cleaned_line:  # Só adiciona linhas não vazias
                data.append(cleaned_line.split("\t"))  # Divide por tabulação

    # Escreve os dados no arquivo CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["id", "name", "created_by_id", "updated_at"]
        )  # Cabeçalhos do CSV
        writer.writerows(data)  # Escreve as linhas de dados

    print(f"Dados salvos no CSV: {csv_file}")


# Caminho dos arquivos
dump_file = (
    "dump-uspolis-202411071451.sql"  # Substitua com o nome do seu arquivo de dump
)
csv_file = "classroom.csv"  # Nome do arquivo CSV que será gerado

# Chama a função para converter o dump para CSV
dump_to_csv(dump_file, csv_file)
