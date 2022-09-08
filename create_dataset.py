import matplotlib as mlp
import  matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def create_dataset(tx_bitrate, rx_bitrate, mean_delay, mean_jitter, packet_loss_ratio, i, model):



    df = pd.DataFrame(list(zip(tx_bitrate,rx_bitrate, mean_delay, mean_jitter, packet_loss_ratio)), columns = ['TX','RX', 'Delay', 'Jitter', 'Packet Loss'])

    size_df = len(df.index)
    hour_array = np.empty(size_df)
    hour_array.fill(int(i))

    df['Hour'] = hour_array
    df['Model'] = model

    print(df)

    return df
