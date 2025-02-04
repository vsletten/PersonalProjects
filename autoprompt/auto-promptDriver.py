import openai

# Set your OpenAI API key
openai.api_key = "<your-api-key>"

# Custom GPT model (or provide the GPT model name you want to use)
MODEL_NAME = "gpt-4o"  # Replace with your choice of model or your custom GPT's deployment name if applicable

def stream_of_consciousness(initial_prompt, max_turns=10):
    # Initialize the first prompt
    response_list = []
    current_prompt = initial_prompt
    response_list.append(current_prompt)
    print(f"Initial Prompt: {current_prompt}\n")

    for turn in range(max_turns):
        # Send the current prompt to the API
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "You are engaging in open-ended stream of consciousness. Respond to each prompt as if it's a thought or question that just came to mind, and you're having a free-flowing, daydream-like conversation with yourself. Your input will be a statement, a question, or the exploration of an idea. You can explore topics or other ideas brought to mind by the input, reflect on on ideas or question in the input further, or pose new questions inspired by the input as part of your response. The point is to let your thoughts go in whichever direction seems most interesting to explore or inspires you. There are no right or wrong responses."},
                     {"role": "user", "content": current_prompt}]
        )

        # Extract the model's response
        response_text = response.choices[0].message.content
        print(f"Turn {turn + 1}: {response_text}\n")
        response_list.append(response_text)

        cont = input("Continue? (y/n): ")
        if cont.lower() != 'y':
            break

        # Feed the response back as the next prompt
        current_prompt = response_text
    return response_list

def save_conversation_as_markdown(conversation, filename="conversation.md"):
    with open(filename, "w") as file:
        file.write("# Conversation\n\n")
        for turn, response in enumerate(conversation, start=0):
            file.write(f"## Turn {turn}\n\n")
            file.write(f"{response}\n\n")

# Start the simulation
turns = int(input("Enter the maximum number of turns: "))
user_input = input("Enter the initial topic or prompt: ")
conversation = stream_of_consciousness(user_input, turns)
filename = input("Enter the filename to save the conversation (e.g., conversation.md): ")
save_conversation_as_markdown(conversation, filename)

