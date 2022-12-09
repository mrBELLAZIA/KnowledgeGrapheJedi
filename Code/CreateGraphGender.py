import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from pyvis.network import Network

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?jediLabel ?genderLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
 	SELECT ?jedi ?gender WHERE {

  	{?jedi p:P106 ?isJedi0.
    	?isJedi0 (ps:P106/(wdt:P279*)) wd:Q51724.}
  	UNION
  	{?jedi p:P463 ?isJedi1.
    	?isJedi1 (ps:P463/(wdt:P279*)) wd:Q51724.}
 	 
  	?jedi wdt:P21 ?gender.
    }
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
for result in results["results"]["bindings"]:
    dict = {}
    if(("jediLabel" in result) & ("genderLabel" in result)):
      # Remove rows with no label (resulting label is Q + id)
      if(not(re.search("^Q[0-9]+$", result["jediLabel"]["value"]))):
        dict["Jedi"] = result["jediLabel"]["value"]
        dict["Gender"] = result["genderLabel"]["value"]
        finalJson.append(dict)

## Saving result in csv file ##

df = pd.DataFrame(finalJson)
df.to_csv('genders.csv', index=False, header=True)

####################

## Creating graph ##

G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
genders = []

# Saving nodes
for i in df.index:
    jedi = df['Jedi'][i]
    gender = df['Gender'][i]

    # removing row if no gender found
    if not(gender in genders):
      genders.append(gender)
      G.add_node(gender, title=gender,group=genders.index(gender))
    
    # Groups (for colors) : according to gender index
    G.add_node(jedi, title=jedi,group=genders.index(gender))
    G.add_edge(jedi, gender)

####################

# create vis network
net = Network(width=1000, height=600)
net.show_buttons(filter_=['physics'])
# build html view page
G.show("genders.html")
