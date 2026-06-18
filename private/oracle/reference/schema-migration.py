from copy import deepcopy


def migrate_settings(document):
    result = deepcopy(document)
    version = result.get("version", 1)
    if version not in (1, 2, 3):
        raise ValueError(f"unsupported version: {version}")
    while version < 3:
        if version == 1:
            result["display"] = {"theme": result.pop("theme", "system")}
            version = 2
            result["version"] = version
        elif version == 2:
            display = result.setdefault("display", {})
            display["color_scheme"] = display.pop("theme", "system")
            version = 3
            result["version"] = version
    return result
