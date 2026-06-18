def load_config(defaults, file_values=None, env_values=None, cli_values=None):
    """Combine configuration mappings without coercing their values."""
    result = {}
    for source in (cli_values, env_values, file_values, defaults):
        if source:
            result.update(source)
    return result
