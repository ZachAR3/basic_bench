def migrate_settings(document):
    version = document.get("version", 1)
    result = document
    if version == 1:
        result["display"] = {"theme": result.pop("theme", "system")}
        result["version"] = 2
    elif version == 2:
        display = result.setdefault("display", {})
        display["color_scheme"] = display.pop("theme", "system")
        result["version"] = 3
    elif version != 3:
        raise ValueError(f"unsupported version: {version}")
    return result
