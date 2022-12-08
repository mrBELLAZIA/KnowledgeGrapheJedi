import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from pyvis.network import Network
import networkx as nx

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?item ?itemLabel ?genderLabel ?studentLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT ?item ?gender ?student WHERE {
      ?item p:P106 ?statement0.
      ?statement0 (ps:P106/(wdt:P279*)) wd:Q51724.
      OPTIONAL{?item wdt:P21 ?gender.}
      OPTIONAL{?item wdt:P802 ?student.}
    }
    LIMIT 1000
  }
}"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

## Sparql request ##
results = get_results(endpoint_url, query)
finalJson = []
for result in results["results"]["bindings"]:

    dict = {}
    if "studentLabel" in result:
        dict["Student"] = result["studentLabel"]["value"]
        dict["Master"] = result["itemLabel"]["value"]
        finalJson.append(dict)
####################

## Saving result in csv file ##

df = pd.DataFrame(finalJson)
df.to_csv('students.csv', index=False, header=True)

####################

## Creating graph ##

G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
students = []
masters = [] 

# Saving students and masters
for i in df.index:
    student = df['Student'][i]
    master = df['Master'][i]

    if not(student in students):
        students.append(student)
    if not(master in masters):
        masters.append(master)

# Saving nodes
for i in df.index:
    student = df['Student'][i]
    master = df['Master'][i]

    # Groups (for colors) : 1 = master; 2 = student; 3 = both
    G.add_node(master, title=master,group=3 if(master in students) else 1)
    G.add_node(student, title=student,group=3 if(student in masters) else 2)

for i in df.index:
    G.add_edge(df['Master'][i], df['Student'][i])

####################

# create vis network
net = Network(width=1000, height=600)
net.show_buttons(filter_=['physics'])
# show
G.show("students.html")