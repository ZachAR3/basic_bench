def stable_toposort(graph):
    """graph maps a node to an iterable of its dependencies."""
    incoming = {node: len(dependencies) for node, dependencies in graph.items()}
    for dependencies in graph.values():
        for dependency in dependencies:
            incoming.setdefault(dependency, 0)
    ready = {node for node, count in incoming.items() if count == 0}
    result = []
    while ready:
        node = ready.pop()
        result.append(node)
        for candidate, dependencies in graph.items():
            if node in dependencies:
                incoming[candidate] -= 1
                if incoming[candidate] == 0:
                    ready.add(candidate)
    return result
