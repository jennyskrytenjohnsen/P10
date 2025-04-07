from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import pandas as pd
import matplotlib.pyplot as plt
import threadpoolctl
from umap import UMAP
import plotly.express as px
print("pool version", threadpoolctl.__version__)

#clinical_information_url = "https://api.vitaldb.net/cases"
#df_clinical= pd.read_csv(clinical_information_url)
icustay = pd.read_csv('C:/Users/johns/Documents/10semester/number_of_days_in_ICU.csv')
df_bigtable = pd.read_csv('C:/Users/johns/Documents/10semester/P10/df_so_far_extracted_features.csv')

df_bigtable= df_bigtable.dropna(axis=1)

print('Noscaling shape', df_bigtable.shape)
dimensionalities = df_bigtable.shape[1]
y_target = icustay['icu_days_binary'] #.iloc[df_bigtable.index]

scaler = StandardScaler()
features_scaled = scaler.fit_transform(df_bigtable)
print("scaled shape", features_scaled.shape)


def t_distributed_sne():
    per = 40
    tsne = TSNE(n_components=2, random_state=42, perplexity=per)  
    X_tsne = tsne.fit_transform(features_scaled)
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=y_target, alpha=0.4)
    plt.legend(*scatter.legend_elements(), title="Klasser")
    plt.title(f't-SNE visualisering av features fra Clinical Data with {dimensionalities} features and perpexity {per}')
    plt.xlabel("t-SNE komponent 1")
    plt.ylabel("t-SNE komponent 2")
    plt.show()


def unifrom_map():
    umap_2d = UMAP(n_components=2, init='random', n_jobs=-1)
    proj_2d = umap_2d.fit_transform(features_scaled)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(proj_2d[:, 0], proj_2d[:, 1], c=y_target, alpha=0.4)
    plt.legend(*scatter.legend_elements(), title="Klasser")
    plt.title(f'UMAP visualisation of clinical data using {dimensionalities} features')
    plt.xlabel('UMAP komponent 1')
    plt.ylabel('UMAP komponent 2')
    #plt.colorbar(scatter, label='ICU status')
    plt.show()

unifrom_map()