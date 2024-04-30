import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Finds the shortest path of (movie_id, person_id) pairs connecting source to target using BFS.

    Args:
        source (str): IMDB id of the source actor.
        target (str): IMDB id of the target actor.

    Returns:
        list of tuples: A list of (movie_id, person_id) pairs from source to target or None if no path is found.
    """
     # Check if source is the same as target
    if source == target:
        # No movies connect the actor to themselves, hence return an empty path
        return []
    
    # Initialize the initial node, the source actor, without parent or action, and add it to the frontier for exploration
    # Inicializa el nodo incial, actor fuente, sin padre ni accion y lo añade a la frontera para explorarlo
    start = Node(source, None, None)
    frontier = QueueFrontier()
    frontier.add(start)

    # Set to track actors that have already been explored
    explored = set()

    # Continue the search as long as there are pending nodes in the frontier 
    while not frontier.empty():
        # Extract the next node to explore from the frontier
        current_node = frontier.remove()
        # Add the current actor to the set of explored
        explored.add(current_node.state)

        # Iterate over each neighbor (movie, actor) of the current actor
        for action, state in neighbors_for_person(current_node.state):
            # Check if the current state is the target actor
            if state == target:
                # Build the path to the target
                path = [(action, state)]
                # Trace back through parent nodes to build the complete path
                while current_node.parent is not None:
                    path.append((current_node.action, current_node.state))
                    current_node = current_node.parent
                path.reverse() # Reverse the path to go from source to target
                return path

            # If the neighbor is not in the frontier and has not been explored, add it for exploration
            if not frontier.contains_state(state) and state not in explored:
                child_node = Node(state, current_node, action)
                frontier.add(child_node)
                
    # If no path is found, return None
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
