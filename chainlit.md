# Streaming chatbot with OpenAI functions

This chatbot utilizes OpenAI's function calling feature to invoke appropriate functions based on user input and stream the response back.

On top of the standard chat interface, the UI exposes the particular function called along with its arguments, as well as the response from the function.

**The current configuration defines two OpenAI functions that can be called**:
- `get_current_weather`: returns the current weather for a given location. Example input: `What's the weather like in New York?`
  - Note that the API returns temperature in Celsius by default. The time zone is set for Europe/Berlin, but this can be changed in `openai_functions.py`

- `get_search_results`: A langchain agent that uses SERP API as a tool to search the web. Example input: `Search the web for the best restaurants in Berlin`