
celulas = client.open_by_url('https://docs.google.com/spreadsheets/d/1zZDaemdx5IABjMUAu9rqsgXomFoGBMNbrLFNFfvnTSY/edit#gid=0')
celulas = celulas.worksheet("Hojas")
celulas = celulas.get_all_values()
plani_tag = client.open_by_url(str(celulas[int(spreadsheet_name) - 1]))
spreadsheet_name = plani_tag.title