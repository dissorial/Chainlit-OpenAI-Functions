FUNCTIONS_SCHEMA = [
    {
        "name": "get_search_results",
        "description": "Used to get search results when the user asks for it",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                }
            },
        },
    },
    {
        "name": "get_current_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "longitude": {
                    "type": "number",
                    "description": "The approximate longitude of the location",
                },
                "latitude": {
                    "type": "number",
                    "description": "The approximate latitude of the location",
                },
            },
            "required": ["longitude", "latitude"],
        },
    },
    # other functions
]
