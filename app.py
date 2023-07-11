import openai
import os
import chainlit as cl
from dotenv import load_dotenv
import ast
from openai_function_schemas import FUNCTIONS_SCHEMA
from openai_functions import FUNCTIONS_MAPPING

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo-0613"
MODEL_TEMPERATURE = 0.3
FUNCTION_CALL = "auto"


async def process_new_delta(
    new_delta, openai_message, content_ui_message, function_ui_message
):
    if "role" in new_delta:
        openai_message["role"] = new_delta["role"]
    if "content" in new_delta:
        new_content = new_delta.get("content") or ""
        openai_message["content"] += new_content
        await content_ui_message.stream_token(new_content)
    if "function_call" in new_delta:
        if "name" in new_delta["function_call"]:
            openai_message["function_call"] = {
                "name": new_delta["function_call"]["name"]
            }
            await content_ui_message.send()
            function_ui_message = cl.Message(
                author=new_delta["function_call"]["name"],
                content="",
                indent=1,
                language="json",
            )
            await function_ui_message.stream_token(new_delta["function_call"]["name"])

        if "arguments" in new_delta["function_call"]:
            if "arguments" not in openai_message["function_call"]:
                openai_message["function_call"]["arguments"] = ""
            openai_message["function_call"]["arguments"] += new_delta["function_call"][
                "arguments"
            ]
            await function_ui_message.stream_token(
                new_delta["function_call"]["arguments"]
            )
    return openai_message, content_ui_message, function_ui_message


async def get_model_response(message_history):
    try:
        return await openai.ChatCompletion.acreate(
            model=MODEL_NAME,
            messages=message_history,
            functions=FUNCTIONS_SCHEMA,
            function_call=FUNCTION_CALL,
            temperature=MODEL_TEMPERATURE,
            stream=True,
        )
    except Exception as e:
        print(f"Error getting model response: {e}")
        return None


async def process_function_call(function_name, arguments, message_history):
    if function_name in FUNCTIONS_MAPPING:
        function_response = FUNCTIONS_MAPPING[function_name](**arguments)
        message_history.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        await send_response(function_name, function_response)
    else:
        print(f"Unknown function: {function_name}")


async def send_response(function_name, function_response):
    await cl.Message(
        author=function_name,
        content=str(function_response),
        language="json",
        indent=1,
    ).send()


async def send_user_message(message):
    await cl.Message(
        author=message["role"],
        content=message["content"],
    ).send()


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful AI assistant"}],
    )


@cl.on_message
async def run_conversation(user_message: str):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": user_message})

    cur_iter = 0
    MAX_ITER = 5

    while cur_iter < MAX_ITER:
        openai_message = {"role": "", "content": ""}
        function_ui_message = None
        content_ui_message = cl.Message(content="")

        # Stream the responses from OpenAI
        model_response = await get_model_response(message_history)
        async for stream_resp in model_response:
            if "choices" not in stream_resp:
                print(f"No choices in response: {stream_resp}")
                return

            new_delta = stream_resp.choices[0]["delta"]
            (
                openai_message,
                content_ui_message,
                function_ui_message,
            ) = await process_new_delta(
                new_delta, openai_message, content_ui_message, function_ui_message
            )

        # Append message to history
        message_history.append(openai_message)
        if function_ui_message is not None:
            await function_ui_message.send()

        # Function call
        if openai_message.get("function_call"):
            function_name = openai_message.get("function_call").get("name")
            arguments = ast.literal_eval(
                openai_message.get("function_call").get("arguments")
            )

            await process_function_call(function_name, arguments, message_history)

            function_response = message_history[-1]
            # await cl.Message(
            #     author=function_name,
            #     content=str(function_response),
            #     language="json",
            #     indent=1,
            # ).send()

            cur_iter += 1
        else:
            break
