import networkx as nx
import pandas as pd
from pyvis.network import Network

# df = pd.read_json ('exemple.json')
# df.to_csv ('Test.csv', index = None)
df = pd.read_csv("my_file.csv")


G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
students = []
masters = [] 
#parcourir le fichier csv
for i in df.index:
    student = df['Target'][i]
    master = df['Source'][i]

    if not(student in students):
        students.append(student)
    if not(master in masters):
        masters.append(master)

for i in df.index:
    student = df['Target'][i]
    master = df['Source'][i]
    masterIsStudent = master in students
    studentIsStudent = student in masters

    G.add_node(df['Source'][i], title=df['Source'][i],group=3 if(masterIsStudent) else 1)
    print(f"add node {master} isBoth : {masterIsStudent}")
    G.add_node(df['Target'][i], title=df['Target'][i],group=3 if(studentIsStudent) else 2)
    print(f"add node {student} isBoth : {studentIsStudent}")

for i in df.index:
    G.add_edge(df['Source'][i], df['Target'][i])


print("No of unique characters:", len(G.nodes))
print("No of connections:", len(G.edges))


# create vis network
net = Network(notebook=True, width=1000, height=600)
net.show_buttons(filter_=['physics'])
# show
G.show("students.html")