import json
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?item ?itemLabel ?genderLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT DISTINCT ?item ?gender WHERE {
      ?item p:P106 ?isJedi.
      ?isJedi (ps:P106/(wdt:P279*)) wd:Q51724.
      OPTIONAL{?item wdt:P21 ?gender.}
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
    dict = {}
    dict["Source"] = result["itemLabel"]["value"]
    dict["Target"] = result["genderLabel"]["value"]
    dict["Type"] = "Undirected"
    dict["weight"] = "2"
    finalJson.append(dict)

with open("exemple.json", "w") as outfile:
    json.dump(finalJson, outfile, indent=4)
