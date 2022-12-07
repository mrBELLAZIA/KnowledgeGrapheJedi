import json
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


results = get_results(endpoint_url, query)
finalJson = []
print(results)
for result in results["results"]["bindings"]:

    dict = {}
    print(result)
    if "studentLabel" in result:
        dict["Target"] = result["studentLabel"]["value"]
        dict["Source"] = result["itemLabel"]["value"]
        dict["Type"] = "Undirected"
        dict["weight"] = "2"
        finalJson.append(dict)

# with open("exemple.json", "w") as outfile:
#     json.dump(finalJson, outfile, indent=4)


df = pd.DataFrame(finalJson)
df.to_csv('my_file.csv', index=False, header=True)

#network from csv
G = nx.from_pandas_edgelist(df,
                            source='Source',
                            target='Target',
                            edge_attr='weight')

net = Network(notebook=True, width=1000, height=600)
net.show_buttons(filter_=['physics'])
net.from_nx(G)
net.show("examplev3.html")
