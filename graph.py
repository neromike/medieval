import pygame
import heapq

class Graph:
    def __init__(self):
        self.nodes = {}  # key: node id, value: position
        self.edges = {}  # key: node id, value: list of tuples (neighbor_id, cost)

    def add_node(self, node_id, position):
        self.nodes[node_id] = position
        self.edges[node_id] = []

    def add_bidirectional_edge(self, from_node, to_node, cost):
        self.edges[from_node].append((to_node, cost))
        self.edges[to_node].append((from_node, cost))

def distance(pos1, pos2):
    return (pos1 - pos2).length()

def heuristic(a, b, nodes):
    return (nodes[a] - nodes[b]).length()

def astar_search(start, goal, graph):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor, cost in graph.edges[current]:
            new_cost = cost_so_far[current] + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor, graph.nodes)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

def get_node_id(name_or_id, node_ids):
    if isinstance(name_or_id, str):
        return node_ids[name_or_id]
    else:
        return name_or_id
