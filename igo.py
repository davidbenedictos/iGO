import osmnx as ox
import networkx as nx
import pickle
import collections
import urllib
import csv
from enum import Enum
from staticmap import StaticMap, Line, CircleMarker

PLACE = 'Barcelona, Catalonia'
GRAPH_FILENAME = 'barcelona.graph'
SIZE = 800
HIGHWAYS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv'
CONGESTIONS_URL = 'https://opendata-ajuntament.barcelona.cat/data/dataset/8319c2b1-4c21-4962-9acd-6db4c5ff1148/resource/2d456eb5-4ea6-4f68-9794-2f3f1a58a933/download'

intCongestio = ["SENSE_DADES", "MOLT_FLUID", "FLUID", "DENS", "MOLT_DENS", "CONGESTIO", "TALLAT"]

Highway = collections.namedtuple('Highway', ['way_id', 'description', 'coordinates']) # Tram
Congestion = collections.namedtuple('Congestion', ['way_id', 'estat'])

def exists_graph(GRAPH_FILENAME):
    #Funcion que comprueba si graph_filename existe
    checker = True
    try:
        outfile = open(GRAPH_FILENAME)
    except:
        checker = False
    if(checker):
        return True
    else:
        return False

def download_graph(PLACE):
    G = ox.graph_from_place(PLACE, network_type='drive', simplify=True)
    return G

def save_graph(graph, GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'wb') as file:
        pickle.dump(graph, file)

def load_graph(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'rb') as file:
        graph = pickle.load(file)
    return graph

def plot_graph(GRAPH):
    ox.plot_graph(GRAPH)

def coordStringToPairs(coord_raw):
    splitted = coord_raw.split(",")
    coord_list = []
    for i in range(0, len(splitted,), 2):
      coord_list.append([ float(splitted[i]), float(splitted[i+1])])
    return coord_list

def download_highways(HIGHWAYS_URL):
    highways = []
    with urllib.request.urlopen(HIGHWAYS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        reader = csv.reader(lines, delimiter=',', quotechar='"')
        next(reader)  # ignore first line with description
        for line in reader:
            way_id, description, coordinates = line
            Node = Highway(way_id=int(way_id), description=description, coordinates=coordStringToPairs(coordinates))
            highways.append(Node)
    return highways

def plot_highways(highways, fileName = 'highways.png', SIZE = 500):
    m = StaticMap(SIZE, SIZE, 80)
    for _, _, coord_high in highways:
      line = Line(coord_high, color = "red", width = 3)
      m.add_line(line)
    image = m.render(zoom=13)
    image.save(fileName)

def download_congestions(CONGESTIONS_URL):
    congestions = {}
    with urllib.request.urlopen(CONGESTIONS_URL) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
        for line in lines:
            id, intCongestio = line.split("#")[0], int(line.split("#")[2])
            line_cong = Congestion(way_id = id, estat = int(intCongestio))
            #He substituit intToCongestio(intCongestio) per intCongestio sol
            congestions[int(id)] = line_cong
    return congestions


def plot_congestions(highways, congestions, fileName = "congestions.png", SIZE = 500, pointSizeFactor = 2):
  m = StaticMap(SIZE, SIZE, 80)
  for id, _, coord_high in highways:
    line = Line(coord_high, color = "red", width = 3)
    m.add_line(line)
    for coord in coord_high:
      marker = CircleMarker((coord[0], coord[1]), 'blue', pointSizeFactor * congestions[id].estat)
      m.add_marker(marker)
  image = m.render(zoom=13)
  image.save(fileName)

def calculate_itime(length, speed, congestion, coeff = 2):
  return (length / speed) + (length / speed) * (congestion - 1) * coeff

def init_itime(graph):
  for node1, info1 in graph.nodes.items():
    for node2, edge in graph.adj[node1].items():
        edge[0]["itime"] = 1000000000


def build_igraph(graph, highways, congestions):
  init_itime(graph)
  #digraph = ox.utils_graph.get_digraph(graph, weight='length')
  graph = ox.add_edge_speeds(graph)
  for highway in highways:
    if highway.way_id in congestions.keys() and congestions[highway.way_id].estat != 0:
      for i in range(0, len(highway.coordinates) - 1):
        primerExtrem = highway.coordinates[i]
        segonExtrem  = highway.coordinates[i+1]

        NNprimerExtrem = ox.distance.nearest_nodes(graph, primerExtrem[0], primerExtrem[1])
        NNsegonExtrem = ox.distance.nearest_nodes(graph, segonExtrem[0], segonExtrem[1])
        
        #print(graph.nodes[NNsegonExtrem])
        try:
          """
          Importa la direcció del camí!
          """
          #ox.distance.shortest_path(graph, NNsegonExtrem, NNprimerExtrem)
          listaIdNodes = ox.distance.shortest_path(graph, NNprimerExtrem, NNsegonExtrem)
          
          listaIdNodes2 = ox.distance.shortest_path(graph, NNsegonExtrem, NNprimerExtrem)

          #print(listaIdNodes)
          #Iterar sobre el cami per propagar la congestio
          for j in range(0, len(listaIdNodes) - 1):
            primerNode = listaIdNodes[j]
            segonNode = listaIdNodes[j+1]
            graph.adj[primerNode][segonNode][0]["congestio"] = congestions[highway.way_id].estat
            length = float(graph.adj[primerNode][segonNode][0]["length"])
            maxspeed = None
            if type(graph.adj[primerNode][segonNode][0]["maxspeed"] == list):
              maxspeed = float(graph.adj[primerNode][segonNode][0]["maxspeed"][0])
            else:
              maxspeed = float(graph.adj[primerNode][segonNode][0]["maxspeed"])
            graph.adj[primerNode][segonNode][0]["itime"] = calculate_itime(length, maxspeed, congestions[highway.way_id].estat)
              

          for j in range(0, len(listaIdNodes2) - 1):
            primerNode = listaIdNodes2[j]
            segonNode = listaIdNodes2[j+1]
            graph.adj[primerNode][segonNode][0]["congestio"] = congestions[highway.way_id].estat
            length = float(graph.adj[primerNode][segonNode][0]["length"])
            maxspeed = None
            if type(graph.adj[primerNode][segonNode][0]["maxspeed"] == list):
              maxspeed = float(graph.adj[primerNode][segonNode][0]["maxspeed"][0])
            else:
              maxspeed = float(graph.adj[primerNode][segonNode][0]["maxspeed"])
            graph.adj[primerNode][segonNode][0]["itime"] = calculate_itime(length, maxspeed, congestions[highway.way_id].estat)
              


            #print(graph.adj[listaIdNodes[j]][listaIdNodes[j + 1]])

        except AttributeError as e:
          print("ERROR")
          pass
        except Exception as e:
          pass
          #print(e)
          """print(f"Error, no hi ha un cami entre {graph.nodes[NNprimerExtrem]} i {graph.nodes[NNsegonExtrem]}")"""
  return graph


def getLatLonFromQuery(QUERY, prefix = "Barcelona, Catalunya"):
  return ox.geocode(QUERY + ", " + prefix)

def getNodeIdFromLatLon(graph, lat, lon):
  print(graph[ox.distance.nearest_nodes(graph, lon, lat)])
  return ox.distance.nearest_nodes(graph, lon, lat)

def get_shortest_path_with_ispeeds(graph, f, to):
  x1, y1 = getLatLonFromQuery(f)
  node1 = getNodeIdFromLatLon(graph, x1, y1)
  x2, y2 = getLatLonFromQuery(to)
  node2 = getNodeIdFromLatLon(graph, x2, y2)
  length = ox.distance.shortest_path(graph, node1, node2, weight="itime")
  return length

def get_shortest_path_with_ispeeds_lat_lon(graph, lat, lon, to):
  node1 = getNodeIdFromLatLon(graph, lat, lon)
  x2, y2 = getLatLonFromQuery(to)
  node2 = getNodeIdFromLatLon(graph, x2, y2)
  length = ox.distance.shortest_path(graph, node1, node2, weight="itime")
  return length


def printaCami(graph, path, fileName = "shortest_path.png", SIZE = 500):
  m = StaticMap(SIZE, SIZE, 300)
  coord_list = []
  for id in path:
    y = graph[0].loc[id].y
    x = graph[0].loc[id].x
    coord_list.append((x,y))
    marker = CircleMarker((x, y), 'blue', 5)
    m.add_marker(marker)

  line = Line(coord_list, color = "red", width = 3)
  m.add_line(line)
  image = m.render(zoom=13)
  image.save(fileName)

def test():
    # load/download graph (using cache) and plot it on the screen
    if not exists_graph(GRAPH_FILENAME):
        graph = download_graph(PLACE)
        save_graph(graph, GRAPH_FILENAME)
    else:
        graph = load_graph(GRAPH_FILENAME)
    #plot_graph(graph)

    highways = download_highways(HIGHWAYS_URL)
    congestions = download_congestions(CONGESTIONS_URL)

    graph = build_igraph(graph, highways, congestions)
    nou_graph = ox.utils_graph.graph_to_gdfs(graph, nodes = True)
    l = get_shortest_path_with_ispeeds(graph, "Campus Nord", "Sagrada Familia")
    printaCami(nou_graph, l)

    """
    # download highways and plot them into a PNG image
    #plot_highways(highways, 'highways.png', SIZE)

    # download congestions and plot them into a PNG image
    #plot_congestions(highways, congestions, 'congestions.png', SIZE)
    #print(graph)
    # get the 'intelligent graph' version of a graph taking into account the congestions of the highways
    graph = build_igraph(graph, highways, congestions)
    save_graph(graph)
    nou_graph = ox.utils_graph.graph_to_gdfs(graph, nodes = True)
    lat,lon = getLatLonFromQuery("Hospital Clinic")
    print(getNodeIdFromLatLon(graph, lat, lon))
    # get 'intelligent path' between two addresses and plot it into a PNG image
    ipath = get_shortest_path_with_ispeeds(graph, "Badal", "Sants")
    #plot_path(igraph, ipath, SIZE)
    """
test()
