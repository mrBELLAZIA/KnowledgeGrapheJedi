import networkx as nx
import pandas as pd
from pyvis.network import Network

# df = pd.read_json ('exemple.json')
# df.to_csv ('Test.csv', index = None)
df = pd.read_csv("out.csv")


G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
#parcourir le fichier csv
for i in df.index:
    G.add_node(df['jediLabel'][i], title=df['jediLabel'][i],group=1, color="#OOOOOO")
    G.add_node(df['actorLabel'][i], title=df['actorLabel'][i],group=2,color="#00FF00")
    G.add_node(str(df['scoreLabel'][i]), title=str(df['scoreLabel'][i]),group=3,color="red")

for i in df.index:
    G.add_edge(df['jediLabel'][i], df['actorLabel'][i], value=str(df['scoreLabel'][i]))
    G.add_edge(df['jediLabel'][i], df['actorLabel'][i], value=1,color="red")
    G.add_edge(df['actorLabel'][i], str(df['scoreLabel'][i]), value=1)
    G.add_edge(str(df['scoreLabel'][i]), df['jediLabel'][i], value=1)


print("No of unique characters:", len(G.nodes))
print("No of connections:", len(G.edges))


# create vis network
net = Network(notebook=True, width=1000, height=600)
net.show_buttons(filter_=['physics'])
# load the networkx graph
print(type(G))
# show
G.show("examplev2.html")