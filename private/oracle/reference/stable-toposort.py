def stable_toposort(graph):
    """graph maps a node to an iterable of its dependencies."""
    node_order = []
    seen = set()
    normalized = {}
    for node, dependencies in graph.items():
        if node not in seen:
            seen.add(node)
            node_order.append(node)
        unique_dependencies = []
        for dependency in dependencies:
            if dependency not in seen:
                seen.add(dependency)
                node_order.append(dependency)
            if dependency not in unique_dependencies:
                unique_dependencies.append(dependency)
        normalized[node] = unique_dependencies
    for node in node_order:
        normalized.setdefault(node, [])

    incoming = {node: len(normalized[node]) for node in node_order}
    dependents = {node: [] for node in node_order}
    for node in node_order:
        for dependency in normalized[node]:
            dependents[dependency].append(node)

    ready = [node for node in node_order if incoming[node] == 0]
    result = []
    while ready:
        node = ready.pop(0)
        result.append(node)
        for dependent in dependents[node]:
            incoming[dependent] -= 1
            if incoming[dependent] == 0:
                ready.append(dependent)
    if len(result) != len(node_order):
        raise ValueError("dependency cycle")
    return result
