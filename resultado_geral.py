    
def resultado_geral(quantidade_de_arquivos, flow_resultado_geral, delay, jitter, pacotes_perdidos, usuarios_nao_atendidos):

    delay_dia = 0
    jitter_dia = 0
    pacotes_perdidos_dia = 0
    usuarios_nao_atendidos_dia = 0
    for i in range(0, quantidade_de_arquivos):
        delay_dia += delay[i]
        jitter_dia += jitter[i]
        pacotes_perdidos_dia += pacotes_perdidos[i]
        usuarios_nao_atendidos_dia += usuarios_nao_atendidos[i]
        
    delay_dia /= quantidade_de_arquivos
    jitter_dia /= quantidade_de_arquivos
    pacotes_perdidos_dia /= quantidade_de_arquivos
    usuarios_nao_atendidos_dia /= quantidade_de_arquivos
    
    with open(flow_resultado_geral,'w') as f: # Limpando  o arquivo
        pass

    with open(flow_resultado_geral, 'a') as arquivo:
                    arquivo.write(f'    RESULTADO GERAL: \n\n')

    with open(flow_resultado_geral, 'a') as arquivo:
                    arquivo.write(f'Delay Médio Geral: {delay_dia:.2f} ms\n')
    with open(flow_resultado_geral, 'a') as arquivo:
                    arquivo.write(f'Jitter Médio Geral: {jitter_dia:.2f} ms\n')
    with open(flow_resultado_geral, 'a') as arquivo:
                    arquivo.write(f'Média Geral de pacotes perdidos: {pacotes_perdidos_dia:.2f}%\n')
    with open(flow_resultado_geral, 'a') as arquivo:
                    arquivo.write(f'Média de Usuários não Atendidos no Geral: {usuarios_nao_atendidos_dia:.2f}\n')   