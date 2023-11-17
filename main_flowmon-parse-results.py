from __future__ import division
import pandas as pd
from create_dataset import create_dataset
from resultado_geral import resultado_geral
import sys
import os
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree



def parse_time_ns(tm):
    if tm.endswith('ns'):
        return long(tm[:-4])
    raise ValueError(tm)



## FiveTuple
class FiveTuple(object):
    ## class variables
    ## @var sourceAddress 
    #  source address
    ## @var destinationAddress 
    #  destination address
    ## @var protocol 
    #  network protocol
    ## @var sourcePort 
    #  source port
    ## @var destinationPort 
    #  destination port
    ## @var __slots__ 
    #  class variable list
    __slots__ = ['sourceAddress', 'destinationAddress', 'protocol', 'sourcePort', 'destinationPort']
    def __init__(self, el):
        '''The initializer.
        @param self The object pointer.
        @param el The element.
        '''
        self.sourceAddress = el.get('sourceAddress')
        self.destinationAddress = el.get('destinationAddress')
        self.sourcePort = int(el.get('sourcePort'))
        self.destinationPort = int(el.get('destinationPort'))
        self.protocol = int(el.get('protocol'))
        
## Histogram
class Histogram(object):
    ## class variables
    ## @var bins
    #  histogram bins
    ## @var nbins
    #  number of bins
    ## @var number_of_flows
    #  number of flows
    ## @var __slots__
    #  class variable list
    __slots__ = 'bins', 'nbins', 'number_of_flows'
    def __init__(self, el=None):
        ''' The initializer.
        @param self The object pointer.
        @param el The element.
        '''
        self.bins = []
        if el is not None:
            #self.nbins = int(el.get('nBins'))
            for bin in el.findall('bin'):
                self.bins.append( (float(bin.get("start")), float(bin.get("width")), int(bin.get("count"))) )

## Flow
class Flow(object):
    ## class variables
    ## @var flowId
    #  delay ID
    ## @var delayMean
    #  mean delay
    ## @var packetLossRatio
    #  packet loss ratio
    ## @var rxBitrate
    #  receive bit rate
    ## @var txBitrate
    #  transmit bit rate
    ## @var fiveTuple
    #  five tuple
    ## @var packetSizeMean
    #  packet size mean
    ## @var probe_stats_unsorted
    #  unsirted probe stats
    ## @var hopCount
    #  hop count
    ## @var flowInterruptionsHistogram
    #  flow histogram
    ## @var rx_duration
    #  receive duration
    ## @var __slots__
    #  class variable list
    __slots__ = ['flowId', 'delayMean', 'packetLossRatio', 'rxBitrate', 'txBitrate',
                 'fiveTuple', 'packetSizeMean', 'probe_stats_unsorted',
                 'hopCount', 'flowInterruptionsHistogram', 'rx_duration', 'jitterMean']
    def __init__(self, flow_el):
        ''' The initializer.
        @param self The object pointer.
        @param flow_el The element.
        '''
        self.flowId = int(flow_el.get('flowId'))
        rxPackets = float(flow_el.get('rxPackets'))
        txPackets = float(flow_el.get('txPackets'))
        tx_duration = float(float(flow_el.get('timeLastTxPacket')[:-4]) - float(flow_el.get('timeFirstTxPacket')[:-4]))*1e-9
        rx_duration = float(float(flow_el.get('timeLastRxPacket')[:-4]) - float(flow_el.get('timeFirstRxPacket')[:-4]))*1e-9
        self.rx_duration = rx_duration
        
        self.probe_stats_unsorted = []
        if rxPackets:
            self.hopCount = float(flow_el.get('timesForwarded')) / rxPackets + 1
        else:
            self.hopCount = -1000
        if rxPackets:
            self.delayMean = float(flow_el.get('delaySum')[:-4]) / rxPackets * 1e-9
            self.packetSizeMean = float(flow_el.get('rxBytes')) / rxPackets
            
            if (rxPackets-1): 
                self.jitterMean = float(flow_el.get('jitterSum')[:-4]) / (rxPackets-1) * 1e-9
            else:
                self.jitterMean = None


        else:
            self.delayMean = None
            self.packetSizeMean = None
            self.jitterMean = None
        if rx_duration > 0:
            self.rxBitrate = float(flow_el.get('rxBytes'))*8 / rx_duration
        else:
            self.rxBitrate = None
        if tx_duration > 0:
            self.txBitrate = float(flow_el.get('txBytes'))*8 / tx_duration
        else:
            self.txBitrate = None
        # lost = float(flow_el.get('lostPackets'))
        lost = txPackets - rxPackets 

        #print "rxBytes: %s; txPackets: %s; rxPackets: %s; lostPackets: %s" % (flow_el.get('rxBytes'), txPackets, rxPackets, lost)
        if rxPackets == 0:
            self.packetLossRatio = None
        else:
            self.packetLossRatio = (lost / (rxPackets + lost))

        interrupt_hist_elem = flow_el.find("flowInterruptionsHistogram")
        if interrupt_hist_elem is None:
            self.flowInterruptionsHistogram = None
        else:
            self.flowInterruptionsHistogram = Histogram(interrupt_hist_elem)

## ProbeFlowStats
class ProbeFlowStats(object):
    ## class variables
    ## @var probeId
    #  probe ID
    ## @var packets
    #  network packets
    ## @var bytes
    #  bytes
    ## @var delayFromFirstProbe
    #  delay from first probe
    ## @var __slots__
    #  class variable list
    __slots__ = ['probeId', 'packets', 'bytes', 'delayFromFirstProbe']

## Simulation
class Simulation(object):
    ## class variables
    ## @var flows
    #  list of flows
    def __init__(self, simulation_el):
        ''' The initializer.
        @param self The object pointer.
        @param simulation_el The element.
        '''
        self.flows = []
        FlowClassifier_el, = simulation_el.findall("Ipv4FlowClassifier")
        flow_map = {}
        for flow_el in simulation_el.findall("FlowStats/Flow"):
            flow = Flow(flow_el)
            flow_map[flow.flowId] = flow
            self.flows.append(flow)
        for flow_cls in FlowClassifier_el.findall("Flow"):
            flowId = int(flow_cls.get('flowId'))
            flow_map[flowId].fiveTuple = FiveTuple(flow_cls)

        for probe_elem in simulation_el.findall("FlowProbes/FlowProbe"):
            probeId = int(probe_elem.get('index'))
            for stats in probe_elem.findall("FlowStats"):
                flowId = int(stats.get('flowId'))
                s = ProbeFlowStats()
                s.packets = int(stats.get('packets'))
                s.bytes = long(stats.get('bytes'))
                s.probeId = probeId
                if s.packets > 0:
                    s.delayFromFirstProbe =  parse_time_ns(stats.get('delayFromFirstProbeSum')) / float(s.packets)
                else:
                    s.delayFromFirstProbe = 0
                flow_map[flowId].probe_stats_unsorted.append(s)


def main(flow_mon, flow_txt):
    file_obj = open(flow_mon)

    with open(flow_txt,'w') as f: # Limpando  o arquivo
        pass

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write('Reading XML file\n')

    print("Reading XML file ")
 
    sys.stdout.flush()        
    level = 0
    sim_list = []
    for event, elem in ElementTree.iterparse(file_obj, events=("start", "end")):
        if event == "start":
            level += 1
        if event == "end":
            level -= 1
            if level == 0 and elem.tag == 'FlowMonitor':
                sim = Simulation(elem)
                sim_list.append(sim)
                elem.clear() # won't need this any more
                sys.stdout.write(".")
                sys.stdout.flush()
    print(" done.")

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(' done.\n')

    tx_bitrate = []
    rx_bitrate = []
    mean_delay = []
    mean_jitter = []
    packet_loss_ratio = []
    numero_usuarios_cobertos = 0
    total_numero_usuarios = 0
    contador_usuarios_nao_atendidos = 0
    contador_tcp = 0


    for sim in sim_list:
        for flow in sim.flows:
            t = flow.fiveTuple
            proto = {6: 'TCP', 17: 'UDP'} [t.protocol]
            print ("FlowID: %i (%s %s/%s --> %s/%i)" % \
                (flow.flowId, proto, t.sourceAddress, t.sourcePort, t.destinationAddress, t.destinationPort))

            with open(flow_txt, 'a') as arquivo:
                    arquivo.write("FlowID: %i (%s %s/%s --> %s/%i)\n" % \
                (flow.flowId, proto, t.sourceAddress, t.sourcePort, t.destinationAddress, t.destinationPort))
            
            if flow.txBitrate is None:
                print("\tTX bitrate: None")
                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tTX bitrate: None\n")
            else:
                print("\tTX bitrate: %.2f kbit/s" % (flow.txBitrate*1e-3,))
                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tTX bitrate: %.2f kbit/s\n" % (flow.txBitrate*1e-3,))

                if proto == 'UDP':
                    if flow.rxBitrate is not None:
                        tx_bitrate.append(round(flow.txBitrate*1e-3))

                if proto == 'TCP':
                    contador_tcp += 1


            if (flow.rxBitrate is None) or (flow.packetLossRatio*100 >= 80):
                print("\tRX bitrate: None")
                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tRX bitrate: None\n")

                contador_usuarios_nao_atendidos += 1
            else:
                print("\tRX bitrate: %.2f kbit/s" % (flow.rxBitrate*1e-3,))

                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tRX bitrate: %.2f kbit/s\n" % (flow.rxBitrate*1e-3,))

                if proto == 'UDP':
                    rx_bitrate.append(flow.rxBitrate*1e-3)

            if flow.delayMean is None or (flow.packetLossRatio*100 >= 80):
                print("\tMean Delay: None")
                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tMean Delay: None\n")
            else:
                print("\tMean Delay: %.2f ms" % (flow.delayMean*1e3,))

                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tMean Delay: %.2f ms\n" % (flow.delayMean*1e3,))
                
                if proto == 'UDP':
                    mean_delay.append(flow.delayMean*1e3)

            if flow.jitterMean is None or (flow.packetLossRatio*100 >= 80):
                print("\tMean Jitter: None")
                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tMean Jitter: None\n")
            else:
                print("\tMean Jitter: %.2f ms" % (flow.jitterMean*1e3,))

                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tMean Jitter: %.2f ms\n" % (flow.jitterMean*1e3,))

                if proto == 'UDP':
                    mean_jitter.append(flow.jitterMean*1e3)

            if flow.packetLossRatio is None or (flow.packetLossRatio*100 >= 80):
                print ("\tPacket Loss Ratio: None")

                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tPacket Loss Ratio: None\n")
            else:
                print ("\tPacket Loss Ratio: %.2f %%" % (flow.packetLossRatio*100))

                with open(flow_txt, 'a') as arquivo:
                    arquivo.write("\tPacket Loss Ratio: %.2f %%\n" % (flow.packetLossRatio*100))

                if proto == 'UDP':
                    packet_loss_ratio.append(flow.packetLossRatio)
                    numero_usuarios_cobertos += 1
            
            total_numero_usuarios += 1

    total_numero_usuarios = total_numero_usuarios - contador_tcp # Retirando comunicações TCP


    final_tx_bitrate = sum(tx_bitrate) / total_numero_usuarios
    final_rx_bitrate = sum(rx_bitrate) / numero_usuarios_cobertos
    final_mean_delay = sum(mean_delay) / numero_usuarios_cobertos
    final_mean_jitter = sum(mean_jitter) / numero_usuarios_cobertos
    final_packet_loss_ratio = sum(packet_loss_ratio) / numero_usuarios_cobertos

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'\n\n    MÉTRICAS NO GERAL: \n')

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'TX bitrate média: {final_tx_bitrate:.2f} kbit/s\n')

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'RX bitrate média: {final_rx_bitrate:.2f} kbit/s\n')

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'Delay Médio: {final_mean_delay:.2f} ms\n')
                    delay.append(final_mean_delay)

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'Jitter Médio: {final_mean_jitter:.2f} ms\n')
                    jitter.append(final_mean_jitter)

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'Média da taxa de pacotes perdidos: {final_packet_loss_ratio*100:.2f}%\n')
                    pacotes_perdidos.append(final_packet_loss_ratio*100)

    with open(flow_txt, 'a') as arquivo:
                    arquivo.write(f'Usuários não atendidos: {contador_usuarios_nao_atendidos}\n')
                    usuarios_nao_atendidos.append(contador_usuarios_nao_atendidos)


    return tx_bitrate, rx_bitrate, mean_delay, mean_jitter, packet_loss_ratio


if __name__ == '__main__':

    print('\n')
    linha = '-'*50
    print(linha)
    print('FLOWMON PARSE RESULTS:'.center(50))
    print(linha)

    # Dataframe que armazenará os métricas obtidas
    df_metrics = pd.DataFrame()

    delay = []
    jitter = []
    pacotes_perdidos = []
    usuarios_nao_atendidos = []

    # Laço que contém o input que pede para o usuário informar o cenário que será utilizado
    # O laço é quebrado apenas quando o usuário informa um cenário correto
    while(1):

        # modo corresponde ao cenário que será executado
        modo = str(input('Indique o cenário (Opcões: SA, HDSO, SUI e ECC): '))
        quantidade_de_arquivos = int(input('Indique a quantidade de arquivos flowmon: '))

        if modo.strip().upper() == 'SA':
            break
        elif modo.strip().upper() == 'HDSO':
            break
        elif modo.strip().upper() == 'SUI':
            break
        elif modo.strip().upper() == 'ECC':
            break
        else:
            print('\nCENÁRIO INCORRETO! TENTE NOVAMENTE.\n')

    # Obtém as informações da quantidade de arquivos do cenário escolhido
    # A sáida para cada arquivo será um arquivo txt com as métricas de cada usuário e a média das métricas para esse arquivo
    # Os arquivos flowmon são gerados pela simulação no NS-3
    
    for i in range(1, quantidade_de_arquivos + 1):

        if modo.strip().upper() == 'SA': 
            flow_mon = f'switch_SA_flowmon/switch_SA_{i}.flowmon'
            flow_txt = f'flows_SA/flow_SA{i}.txt'
            model = 'SA'

        elif modo.strip().upper() == 'HDSO':
            flow_mon = f'switch_HDSO_flowmon/switch_HDSO_{i}.flowmon'
            flow_txt = f'flows_HDSO/flow_HDSO{i}.txt'
            model = 'HDSO'

        elif modo.strip().upper() == 'SUI':
            flow_mon = f'switch_SUI_flowmon/switch_SUI_{i}.flowmon'
            flow_txt = f'resultados_SUI/flow_SUI_{i}.txt'
            model = 'SUI'
        
        elif modo.strip().upper() == 'ECC':
            flow_mon = f'switch_ECC_flowmon/switch_ECC_{i}.flowmon'
            flow_txt = f'resultados_ECC/flow_ECC_{i}.txt'
            model = 'ECC'

        # Função principal que obtém as métricas médias de cada usuário
        tx_bitrate, rx_bitrate, mean_delay, mean_jitter, packet_loss_ratio = main(flow_mon, flow_txt)
        # Dataframe com as métricas para a hora i
        df_per_hour = create_dataset(tx_bitrate, rx_bitrate, mean_delay, mean_jitter, packet_loss_ratio, i, model)
        # Concate os dataframes a cada hora i
        df_metrics = pd.concat([df_metrics, df_per_hour])

    # Salva as métricas em um CSV
    # Nome do dataframe
    dataframe_name = f'datasets/df_metrics_{model}.csv'
    print(df_metrics)
    df_metrics.to_csv(dataframe_name, index=False)

    # Define o caminho do txt que será gerado de acordo com o cenário escolhido
    # O txt contém a média das métricas de todos os arquivos
    if modo.strip().upper() == 'SA':
        caminho_media_geral = f'flows_SA/Resultados_dia.txt'
    elif modo.strip().upper() == 'HDSO':    
        caminho_media_geral = f'flows_HDSO/Resultados_dia.txt'
    elif modo.strip().upper() == 'SUI': 
        caminho_media_geral = f'resultados_SUI/SUI_resultado_media_geral.txt'
    elif modo.strip().upper() == 'ECC': 
        caminho_media_geral = f'resultados_ECC/ECC_resultado_media_geral.txt'

    # Gera um arquivo txt com a média para o dia (ou a média em relação à quantidade de arquivos flowmon gerados)
    resultado_geral(quantidade_de_arquivos, caminho_media_geral, delay, jitter, pacotes_perdidos, usuarios_nao_atendidos)