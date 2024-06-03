#!/usr/bin/env python3

import sys

# Funktion zur Normalisierung des Stationnamens, indem nicht-alphanumerische Zeichen entfernt und in Kleinbuchstaben umgewandelt werden
def normalize_station_name(name): 
    return ''.join(e for e in name.lower() if e.isalnum()) # Nur alphanumerische Zeichen beibehalten und in Kleinbuchstaben umwandeln
  
# Funktion zum Einlesen des Graphen aus der angegebenen Datei
def read_graph(filename):
    graph = {}  # Dictionary zum Speichern des Graphen
    original_names = {}  # Dictionary zum Speichern der originalen Stationsnamen
    with open(filename, 'r') as file: # Datei öffnen
        for line in file:
            parts = line.strip().split(':')  # Jede Zeile in Teile aufteilen
            line_name = parts[0].strip()  # Den Namen der Linie extrahieren
            segments_costs = parts[1].strip().split('"')[1::2]  # Stationennamen extrahieren (in Anführungszeichen) an ungeraden Positionen
            cost_strings = parts[1].strip().split('"')[2::2]  # Kostensätze extrahieren (in Anführungszeichen) an geraden Positionen
            costs = [int(cost_string.strip().split()[0]) for cost_string in cost_strings if cost_string.strip()]  # Kosten extrahieren und in Integer umwandeln

            # Originalnamen auf normalisierte Namen abbilden
            for i in range(len(segments_costs)): 
                normalized_name = normalize_station_name(segments_costs[i]) 
                original_names[normalized_name] = segments_costs[i] # normalisierter Name als Schlüssel und originaler Name als Wert, vereinfacht die Suche nach originalen Namen

            # Stationennamen normalisieren und den Graphen aufbauen
            segments = [normalize_station_name(name) for name in segments_costs]
            for i in range(len(segments) - 1):
                if segments[i] not in graph:
                    graph[segments[i]] = []
                if segments[i + 1] not in graph:
                    graph[segments[i + 1]] = []
                # Kanten zum Graphen hinzufügen
                graph[segments[i]].append((segments[i + 1], costs[i], line_name))
                graph[segments[i + 1]].append((segments[i], costs[i], line_name))
    return graph, original_names

# Funktion zur Suche des kürzesten Pfads zwischen zwei Stationen mithilfe des Dijkstra-Algorithmus
def dijkstra(graph, start, end):
    shortest_paths = {start: (None, 0)}  # Dictionary zum Speichern der kürzesten Pfade, startkniten als Schlüssel, None als Vorgänger und 0 als Kosten
    current_node = start  # aktueller Knoten wird auf den Startknoten gesetzt
    visited = set()  # Menge zur Speicherung besuchter Knoten
    
    # Schleife bis zum Erreichen des Endknotens
    while current_node != end:
        visited.add(current_node) # aktuellen Knoten als besucht markieren
        destinations = graph[current_node] # Nachbarn des aktuellen Knotens, jeder Schlüssel ist ein Knoten und der Wert ist eine Liste von Tupeln (Nachbarknoten, Kosten, Linie)
        weight_to_current_node = shortest_paths[current_node][1] # Kosten zum aktuellen Knoten

        # Durchlaufen der Nachbarn des aktuellen Knotens
        for next_node, weight, line in destinations:
            weight = weight_to_current_node + weight
            # Wenn der Nachbarknoten noch nicht besucht wurde, wird der kürzeste Pfad aktualisiert
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight) 
            # Wenn der Nachbarknoten bereits besucht wurde, wird der kürzeste Pfad aktualisiert, wenn der neue Pfad kürzer ist
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        # Finden des nächsten unbesuchten Knotens mit der kürzesten Entfernung
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return float("inf"), []

        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Pfad rekonstruieren
    path = []
    total_cost = shortest_paths[end][1] # Gesamtkosten des kürzesten Pfads
    # Pfad von Endknoten zu Startknoten rekonstruieren
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node

    path = path[::-1] # Pfad umdrehen, um von Start zu Endknoten zu gehen
    return total_cost, path

# Funktion zum Finden des Pfads zwischen zwei Stationen im gegebenen Graphen
def find_path(filename_graph, start, end):
    graph, original_names = read_graph(filename_graph)  # Graph einlesen
    start_normalized = normalize_station_name(start) # Startstation normalisieren
    end_normalized = normalize_station_name(end) # Endstation normalisieren
    
    total_cost, path = dijkstra(graph, start_normalized, end_normalized)  # Kürzesten Pfad finden
    if path == []:
        return [f"Kein Pfad gefunden von {start} nach {end}"]

    # Pfaddetails mit Stationsnamen und Kosten zusammenstellen
    path_details = []
    current_line = None
    for i in range(len(path) - 1):
        for v2, c, line in graph[path[i]]:
            if v2 == path[i + 1]:
                if current_line != line:
                    if current_line is not None:
                        path_details.append(f"Umsteigen von {current_line} zu {line} bei {original_names[path[i]]}")
                    current_line = line
                path_details.append(f"{original_names[path[i]]} zu {original_names[path[i + 1]]} über {current_line} (Kosten: {c})")
                break
    path_details.append(f"Gesamtkosten: {total_cost}")
    return path_details

# Hauptfunktion
if __name__ == "__main__":
    # Argumente einlesen, falls mindestens 4 Argumente vorhanden sind wobei sys.argv den Dateinamen, Start- und Endstation enthält
    if len(sys.argv) < 4: 
        print("Usage: find_path filename_graph start end") 
        sys.exit(1)
    filename_graph = sys.argv[1]  # Dateiname des Graphen
    start = ' '.join(sys.argv[2:-1])  # Startstation, Elemente von Index 2 bis zum vorletzten Element zusammenfügen
    end = sys.argv[-1]  # Endstation, Element am letzten Index
    path_details = find_path(filename_graph, start, end)  # Pfaddetails finden
    for detail in path_details:
        print(detail)  # Pfaddetails ausgeben
