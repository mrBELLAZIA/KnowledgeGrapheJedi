import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from pyvis.network import Network
import json

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?jedi ?jediLabel ?actorLabel ?filmLabel ?scoreLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT ?jedi ?actor ?film ?score WHERE {
      
      #Get Jedis (member_of or occupation of Jedi)
      {?jedi p:P106 ?isJedi0.
        ?isJedi0 (ps:P106/(wdt:P279*)) wd:Q51724.} 
      UNION 
      {?jedi p:P463 ?isJedi1.
        ?isJedi1 (ps:P463/(wdt:P279*)) wd:Q51724.}

      #Get actors linked to Jedi
      {?jedi p:P175 ?isActor.
        ?isActor (ps:P175/(wdt:P279*)) ?actor.}
      
      #Get films linked to actor...
      {?film p:P161 ?isFilm.
        ?isFilm (ps:P161/(wdt:P279*)) ?actor.}
      
      #... that are in the StarWars fictional universe
      {?film p:P1434 ?isInFiction.
        ?isInFiction (ps:P1434/(wdt:P279*)) wd:Q19786052.}
      
      #Get the film rating if exists
      OPTIONAL
      {?film wdt:P444 ?score.}
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

def processrating(row):
    row.scoreLabel = row.scoreLabel.replace('%','') #On del le %
    row.scoreLabel = row.scoreLabel.replace(',','.') #On remplace la virgule par un point pour le cast en flottant
    rate = row.scoreLabel.split('/') #Si on tombe sur un / on recup le nominateur et le denominaeur
    if len(rate) > 1: #Si la note est une fraction 
        row.scoreLabel = 100 * float(rate[0])/float(rate[1]) #On calcul le pourcentage
    else: #Sinon on a déjà un pourcentage
        row.scoreLabel = float(rate[0])
    return row


results = get_results(endpoint_url, query)

with open("sample.json", "w") as outfile:
    json.dump(results["results"]["bindings"], outfile, indent=4)

finalJson = []
for result in results["results"]["bindings"]:
  if "scoreLabel" in result:
    dict = {}
    dict["jediLabel"] = result["jediLabel"]["value"]
    dict["filmLabel"] = result["filmLabel"]["value"]
    dict["scoreLabel"] = result["scoreLabel"]["value"]
    dict["actorLabel"] = result["actorLabel"]["value"]
    finalJson.append(dict)

df = pd.DataFrame(finalJson)
# df = pd.read_csv(results, sep=",", header=None)
df = df.dropna()
#df = df.drop(['jedi'], axis=1) #on a pas besoin de cette colonne
df = df.apply(processrating, axis=1) #on normalise les notes

df = df.groupby(['jediLabel', 'actorLabel', 'filmLabel']).median() #On fait la medianne des notes d'un même film pour un même acteur
df = df.reset_index()
print(df.head())
df.to_csv('actorfilm.csv', index=True, header=True)


G = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
#parcourir le fichier csv

for i, row in df.iterrows():
  G.add_node(df['jediLabel'][i], title=df['jediLabel'][i],group=1, color="#OOOOOO")
  G.add_node(df['actorLabel'][i], title=df['actorLabel'][i],group=2,color="#00FF00")
  G.add_node(str(df['scoreLabel'][i]), title=str(df['scoreLabel'][i]),group=3,color="red")
  G.add_node(str(df['filmLabel'][i]), title=str(df['filmLabel'][i]),group=4,color="red")

for i in df.index:
  G.add_edge(df['jediLabel'][i], df['actorLabel'][i], value=str(df['scoreLabel'][i]))
  G.add_edge(df['actorLabel'][i], str(df['filmLabel'][i]), value=1)
  G.add_edge(df['filmLabel'][i], str(df['scoreLabel'][i]), value=1)

# create vis network
net = Network(notebook=True, width=1000, height=600)
net.show_buttons(filter_=['physics'])
# load the networkx graph
print(type(G))
# show
G.show("actorfilm.html")
