# LLM-guided-Negotiations-with-Mediators

This is an implementation of a mediator guided LLM negotiation as part of a minor research project for E2 335 - Topics in Artificial Intelligence. The goal was to explore how does the introduction of a meditor in an LLM negotiation affects the number of rounds required.
A more detailed description is [here](./LLM_Negotiations_with_mediator_Final_report.pdf)

## INSTRUCTIONS FOR RUNNING THIS FILE

- 1. Install ollama from ollama website https://ollama.com/download . This is required to pull model and run the server.

- 2. Install ollama python library via "pip install ollama"

- 3. Open a separate terminal, and execute `ollama pull mistral` to pull the mistral-7B instruct model.

- 4. In the second terminal, type `ollama serve` and press enter, which starts the ollama server .

- 5. This file can now be executed by navigating to its folder and calling `python chat_game_tradefruit.py`
