    
def resultados_do_dia(flow_resultados_dia, delay, jitter, pacotes_perdidos, usuarios_nao_atendidos):

    delay_dia = 0
    jitter_dia = 0
    pacotes_perdidos_dia = 0
    usuarios_nao_atendidos_dia = 0
    for i in range(0, 24):
        delay_dia += delay[i]
        jitter_dia += jitter[i]
        pacotes_perdidos_dia += pacotes_perdidos[i]
        usuarios_nao_atendidos_dia += usuarios_nao_atendidos[i]
        
    delay_dia /= 24
    jitter_dia /= 24
    pacotes_perdidos_dia /= 24
    usuarios_nao_atendidos_dia /= 24
    
    with open(flow_resultados_dia,'w') as f: # Limpando  o arquivo
        pass

    with open(flow_resultados_dia, 'a') as arquivo:
                    arquivo.write(f'    RESULTADOS DO DIA: \n\n')

    with open(flow_resultados_dia, 'a') as arquivo:
                    arquivo.write(f'Delay médio do dia: {delay_dia:.2f}\n')
    with open(flow_resultados_dia, 'a') as arquivo:
                    arquivo.write(f'Jitter médio do dia: {jitter_dia:.2f}\n')
    with open(flow_resultados_dia, 'a') as arquivo:
                    arquivo.write(f'Média de pacotes perdidos do dia: {pacotes_perdidos_dia:.2f}%\n')
    with open(flow_resultados_dia, 'a') as arquivo:
                    arquivo.write(f'Média de usuários não atendidos do dia: {usuarios_nao_atendidos_dia:.2f}\n')   