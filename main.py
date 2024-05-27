#!/usr/bin/env python3
import sys

def normalize_station_name(name):
    return ''.join(e for e in name.lower() if e.isalnum())

def read_graph(filename):
    graph = {}
    original_names = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            line_name = parts[0].strip()
            segments_costs = parts[1].strip().split('"')[1::2]
            cost_strings = parts[1].strip().split('"')[2::2]
            costs = [int(cost_string.strip().split()[0]) for cost_string in cost_strings if cost_string.strip()]

            for i in range(len(segments_costs)):
                normalized_name = normalize_station_name(segments_costs[i])
                original_names[normalized_name] = segments_costs[i]

            segments = [normalize_station_name(name) for name in segments_costs]
            for i in range(len(segments) - 1):
                if segments[i] not in graph:
                    graph[segments[i]] = []
                if segments[i + 1] not in graph:
                    graph[segments[i + 1]] = []
                graph[segments[i]].append((segments[i + 1], costs[i], line_name))
                graph[segments[i + 1]].append((segments[i], costs[i], line_name))
    return graph, original_names

def dijkstra(graph, start, end):
    shortest_paths = {start: (None, 0)}
    current_node = start
    visited = set()
    
    while current_node != end:
        visited.add(current_node)
        destinations = graph[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node, weight, line in destinations:
            weight = weight_to_current_node + weight
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return float("inf"), []

        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    path = []
    total_cost = shortest_paths[end][1]
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node

    path = path[::-1]
    return total_cost, path

def find_path(filename_graph, start, end):
    graph, original_names = read_graph(filename_graph)
    start_normalized = normalize_station_name(start)
    end_normalized = normalize_station_name(end)
    
    total_cost, path = dijkstra(graph, start_normalized, end_normalized)
    if path == []:
        return [f"Kein Pfad gefunden von {start} nach {end}"]

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
    path_details.append(f"Gesamtkosten: {total_cost} Euro")
    path_details.append(f"Gesamtfahrzeit: {total_cost} Minuten")
    return path_details

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: find_path filename_graph start end")
        sys.exit(1)
    filename_graph = sys.argv[1]
    start = ' '.join(sys.argv[2:-1])
    end = sys.argv[-1]
    path_details = find_path(filename_graph, start, end)
    for detail in path_details:
        print(detail)
