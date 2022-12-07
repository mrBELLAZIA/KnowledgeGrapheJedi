import json
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?jedi ?jediLabel ?genderLabel ?actorLabel ?filmLabel ?scoreLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT ?jedi ?gender ?actor ?film ?score WHERE {
      {
        ?jedi p:P106 ?isJedi0.
        ?isJedi0 (ps:P106/(wdt:P279*)) wd:Q51724.
      }
      UNION
      {
        ?jedi p:P463 ?isJedi1.
        ?isJedi1 (ps:P463/(wdt:P279*)) wd:Q51724.
      }
      
      OPTIONAL{?jedi wdt:P21 ?gender.}
                     
      {
        ?jedi p:P175 ?isActor.
        ?isActor (ps:P175/(wdt:P279*)) ?actor.
      }
      
      ?film wdt:P1434 wd:Q19786052.
      ?film wdt:P161 ?actor.
      OPTIONAL{?film wdt:P444 ?score.}
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
for result in results["results"]["bindings"]:
    print(result)
    dict = {}
    dict["Source"] = result["actorLabel"]["value"]
    dict["Target"] = result["filmLabel"]["value"]
    #dict["Target"] = result["scoreLabel"]["value"]
    dict["Type"] = "Undirected"
    dict["weight"] = "2"
    finalJson.append(dict)

with open("exemple.json", "w") as outfile:
    json.dump(finalJson, outfile, indent=4)
