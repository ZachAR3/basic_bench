def load_config(defaults, file_values=None, env_values=None, cli_values=None):
    """Combine configuration mappings without coercing their values."""
    result = {}
    for source in (defaults, file_values, env_values, cli_values):
        if source is not None:
            result.update(source)
    return result
