# iGO

### Introduction
***
**Time** is the most precious non-material property. People always try to optimize our tasks so that we can have time to do everything. However, there are things that cannot be foreseen, and therefore we cannot make an exhaustive analysis that allows us to save it to the maximum because there are an immensity of factors that influence it. This app has been designed to make life easier for people. Through a conversation with a bot, we are allowed to know the shortest distance between two points in the city of Barcelona taking into account the congestion of the section we have to go through at that time.

### Authorship
***
This work has been prepared by :
- Jose Àngel Mola Audí
- David Benedicto Sedas

### Files
***
The project consists of two _.py_ files:
- **igo.py**: Contains the implementation of all the functions related to the graph, as well as its graphical representation and the propagation of the different congestions in order to create the final resulting graph.
- **bot.py**: Contains all the code that was used to implement the bot.

### Documentation
***
The first file consists of twenty functions, which do the following:
> The functions **exists_graph**, **download_graph**, **save_graph**, **load_graph** and **plot_graph** are in charge of checking if the graph exists, download it, save it, load it and draw it. These are functions that were already given.

The other functions are self-implemented and are as follows:
- **coordStringToPairs**: is responsible for separating the coordinates in pairs **x** and **y** so that they can be processed later.
- **download_highways**: is responsible for downloading the different highways provided to us from the csv file.
- **plot_highways**: is responsible for making a drawing on a map of the different highways obtained.
- **download_congestions**: is responsible for downloading from the file provided by Barcelona City Council, the different congestions in the main sections of the city.
- **plot_congestions**: is responsible for making a drawing on a map of the different highways obtained with the congestion of the different sections on which we have information.
- **calculate_itime**: this function is responsible for calculating a time *itime* that will be used to determine the congestion of the different sections.
- **init_itime**: this function is responsible for initializing all *itime* variables to infinity (usually a large symbolic number). We have done this so that in case we have data, we put an itime in it, but in case it doesn't, it stays at infinity.
- **build_igraph**: this is the key function of the project. It is responsible for spreading the congestion of the sections that are close to the main roads of the city of Barcelona. First of all, we initialize all *itime* to infinity and using a library function, we add a speed attribute to the graph. Then, we traverse the different highways, grab the nearest nodes that have congestion, and propagate them. It returns a graph with the *itime* attribute on which we will look for the shortest path between two nodes.
- **getLatLonFromQuery**: is responsible for returning the value of the latitude and longitude of the name we pass.
- **getNodeIdFromLatLon**: is responsible for returning the node of the latitude and longitude we passed.
- **get_shortest_path_with_ispeeds**: returns the shortest path between two nodes, but in this case, we have passed the place names as a parameter.
- **get_shortest_path_with_ispeeds_lat_lon**: returns the shortest path between two nodes, but in this case, we have passed the coordinates of the place where we are. This feature will be useful for the bot.
- **plot_path**: is responsible for drawing the shortest path between the two requested nodes taking into account the concept *itime*.

And the second file contains everything related to the bot. In that file we will find all the implementations of the functions that allow to make it work all the following commands. That commands are:

- **/start**: It sends a message of welcome.
- **/help**: It explains all you can do with iGo.
- **/author**: It shows the name of authors of the project.
- **/go -destination-**: it plots a map with the shortest path to go from a position to desination.
- **/where**: it shows which is your actual position.
- **/pos -location-**: it changes your actual position to new location.

> We hope our app make easier life's people. We have done the best we've could. Thank you!
