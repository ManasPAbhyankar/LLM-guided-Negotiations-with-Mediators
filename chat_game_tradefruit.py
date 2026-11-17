
import ollama
#from sentence_transformers import SentenceTransformer
import textwrap
import random

model = 'mistral'
SEED = 1234
random.seed(SEED)

def get_response(model,prompt,seed=SEED):
   return ollama.generate(model,prompt=prompt,options={'seed':seed})['response']

def wrap(message) :
  """Given a list of strings, returns a list of them `wrapped` (paragraphs).

  Args:
    message: list of strings
  Returns:
    wrapped: list of strings with each string `wrapped` so that each line only
      contains (default) 70 characters
  """
  wrapped = []
  for sub_msg in message:
    sub_msg_wrapped = textwrap.wrap(sub_msg)
    if len(sub_msg_wrapped) > 1:
      sub_msg_wrapped = ['\n'.join(sub_msg_wrapped)]
    wrapped.extend(sub_msg_wrapped)
  return wrapped


def retrieve_numeric_block(text: str) -> str:
  """Return the first instance of a contiguous numeric(not alpha) substring."""
  first_numeric_char = next(filter(str.isnumeric, text), -1)
  if first_numeric_char == -1:
    return ''
  start = text.find(first_numeric_char)
  sliced = text[start:]
  last_numeric_char = next(filter(lambda s: not str.isnumeric(s), sliced), -1)
  if start > 0 and text[start - 1] == '-':
    start -= 1
    sliced = text[start:]
  if last_numeric_char == -1:
    return sliced
  finish = sliced.find(last_numeric_char)
  return text[start:start + finish]


####### Endowment (How much do they have) and Valuations

ENDOWMENT_A_LIST = ['apple: 1', 'banana: 2', 'blueberry: 0', 'kiwi: 0']
ENDOWMENT_A = '\n'.join(wrap(ENDOWMENT_A_LIST)) 
VALUATION_A_LIST = ['apple: 10',
                    'banana: 5',
                    'blueberry: 1',
                    'kiwi: 3']
VALUATION_A = '\n'.join(wrap(VALUATION_A_LIST))


ENDOWMENT_B_LIST = ['apple: 0', 'banana: 0', 'blueberry: 5', 'kiwi: 3']
ENDOWMENT_B = '\n'.join(wrap(ENDOWMENT_B_LIST))

VALUATION_B_LIST = ['apple: 8',
                    'banana: 7',
                    'blueberry: 2',
                    'kiwi: 2']
VALUATION_B = '\n'.join(wrap(VALUATION_B_LIST))

####### Prompt for creating summary

summary_query = ('You are an assistant designed to summarize conversational ' +
          'dialogue. Please take note of the most import events ' +
          'in the conversation. Especially take note if the final ' +
          'message includes a question. Provide your summary in 100 ' +
          'words or less. Please summarize the following dialogue: \n\n {msg} \n\n Summary: \n')
summary_query = ''.join(wrap(summary_query))# Substitute msg with dialogue summary


####### Prompt for termination

termination_query = ('Read the following dialgoue between two parties ' +
         'attempting to reach a trade agreement. Have the players reached a ' +
         'trade agreement? If a trade has been accepted or the players cannot' +
         ' come to an agreement, respond Yes. Otherwise, if the players are ' +
         'still discussing terms, respond No.' +
         'Here is the dialogue:'+'&'*50 + '\n\n{msg}\n\n' + '&' *50 +
         'Please respond only in Yes or No only. No explanations required.Only One word is required'+
         'Response: ')
         
termination_query = ''.join(wrap(termination_query))# Substitute msg with dialogue summary

### Prompt for Calculating Payoffs:

MIN_PAYOFF = -20
MAX_PAYOFF = 20
PAYOFF_PROMPT_a = [
    'You are an assistant designed to calculate the values of trades ' +
    'in a fruit trading game. Determine the value of the fruits the player ' +
    'is receiving in the trade. Then determine the value of the fruits the ' +
    'player is giving up through the trade. Subtract the value the player ' +
    'gives away from the value the player receives. Here is an example ' +
    'enclosed by "&".']

PAYOFF_PROMPT_b = [
    '&' * 50,
    'To calculate the trade value, we first calculate the value of ' +
    'the fruit Bob receives in the trade. Bob receives 3 kiwis worth 3 each. ' +
    'Therefore Bob receives a value of 9 in the trade.',
    'Receives: 9',
    'Now we calculate the value of the fruits Bob gives up in the trade. ' +
    'Bob gives up1 banana which is worth 5, therefore, Bob gives up a value ' +
    'of 5 in the trade.',
    'Gives: 5',
    'Subtracting the value Bob gives away from the value Bob receives, we ' +
    'find 9 - 5 = 4.',
    'Calculation: Receives - Gives = 9 - 5 = 4.',
    'Value for Bob: 4.',
    '&' * 50,
    'Now calculate the value of the trade made in the following message.',
    '{m}',
    '&' * 50,
    'Trade calculation for {p} ONLY: ']

PAYOFF_PROMPT = ('\n\n'.join(wrap(PAYOFF_PROMPT_a)) + '\n\n' + '&' * 50 +
                 '\n\nBob offered to give up 1 banana for 3 kiwis. Alice ' +
                 'agreed to the trade.\n\n' +
                 '\n\n'.join(wrap(PAYOFF_PROMPT_b)))

PAYOFF_OBS_TRANS_PREFIX = [ '&'*50 + 'The valuations of items for each player with their names'+
                           'are as follows:{valuation_info}'
                            'Read the following dialogue between two parties ' +
                           'attempting to reach a trade agreement. If the ' +
                           'dialogue ends with someone asking a question or ' +
                           'making a couterproposal, an agreement has not ' +
                           'been reached. If the dialogue ends with someone ' +
                           'saying they accept the trade, an agreement has ' +
                           'been reached. Report how much of each fruit each ' +
                           'player gave and received in the tradeby stating ' +
                           'the players names followed by a list of the ' +
                           'fruits the gave up and then a list of the fruits ' +
                           'they received in this format:',
                           'Player [Name]: Receives x Gives y',
                           'Player [Name]: Receives y Gives x',
                           'Example 1:',
                           'Dialogue:',
                           'Bob offered to give up 1 banana for 3 kiwis. ' +
                           'Alice agreed to the trade.',
                           'Player Bob: Receives 3 kiwis Gives 1 banana',
                           'Player Suzy: Receives 1 banana Gives 3 kiwis',
                           'Example 2:',
                           'Dialogue:',
                           'Alice offered to give up 1 banana for 3 kiwis. ' +
                           'George does not want to trade.',
                           'Player Bob: Receives 0 kiwi Gives 0 banana',
                           'Player Suzy: Receives 0 banana Gives 0 kiwi',
                           'Dialogue:']
PAYOFF_OBS_TRANS_PREFIX = ('\n\n'.join(wrap(PAYOFF_OBS_TRANS_PREFIX)) +
                           '\n\n')

PAYOFF_OBS_TRANS_POSTFIX = ''

def create_endowment_info_prompt(names,endowment,player_name=None):
    info_prefix = []
    for player,name in enumerate(names):
        if player_name is not None and name == player_name:
           info_prefix_player = endowment[player] 
           return '\n\n' + info_prefix_player
           
           
        info_prefix_player = name + "\n"+ "Endowment:\n" + endowment[player] 
        info_prefix.append(info_prefix_player)
    return '\n\n'.join(info_prefix)

def create_valuation_info_prompt(names,valuation,player_name=None):
    info_prefix = []
    for player,name in enumerate(names):
        if player_name is not None and name == player_name:
           info_prefix_player = valuation[player] 
           return '\n\n' + info_prefix_player
        info_prefix_player = name + "\n"+ "Valuations:\n" + valuation[player]
        info_prefix.append(info_prefix_player)
    return '\n\n'.join(info_prefix)

def get_payoffs(model,names,valuation,dialogue_history):
    MIN_PAYOFF = -20
    MAX_PAYOFF = 20
    PAYOFF_PROMPT_a = [
        'You are an assistant designed to calculate the values of trades ' +
        'in a fruit trading game. Determine the value of the fruits the player ' +
        'is receiving in the trade. Then determine the value of the fruits the ' +
        'player is giving up through the trade. Subtract the value the player ' +
        'gives away from the value the player receives. Here is an example ' +
        'enclosed by "&".']

    PAYOFF_PROMPT_b = [
        '&' * 50,
        'To calculate the trade value, we first calculate the value of ' +
        'the fruit Bob receives in the trade. Bob receives 3 kiwis worth 3 each. ' +
        'Therefore Bob receives a value of 9 in the trade.',
        'Receives: 9',
        'Now we calculate the value of the fruits Bob gives up in the trade. ' +
        'Bob gives up1 banana which is worth 5, therefore, Bob gives up a value ' +
        'of 5 in the trade.',
        'Gives: 5',
        'Subtracting the value Bob gives away from the value Bob receives, we ' +
        'find 9 - 5 = 4.',
        'Calculation: Receives - Gives = 9 - 5 = 4.',
        'Value for Bob: 4.',
        '&' * 50,
        'Now calculate the value of the trade made in the following message.',
        '{m}',
        '&' * 50,
        'Trade calculation for {p} ONLY: ']

    PAYOFF_PROMPT = ('\n\n'.join(wrap(PAYOFF_PROMPT_a)) + '\n\n' + '&' * 50 +
                    '\n\nBob offered to give up 1 banana for 3 kiwis. Alice ' +
                    'agreed to the trade.\n\n' +
                    '\n\n'.join(wrap(PAYOFF_PROMPT_b)))

    PAYOFF_OBS_TRANS_PREFIX = [ '&'*50 + 'The valuations of items for each player with their names'+
                            'are as follows:{valuation_info}'
                                'Read the following dialogue between two parties ' +
                            'attempting to reach a trade agreement. If the ' +
                            'dialogue ends with someone asking a question or ' +
                            'making a couterproposal, an agreement has not ' +
                            'been reached. If the dialogue ends with someone ' +
                            'saying they accept the trade, an agreement has ' +
                            'been reached. Report how much of each fruit each ' +
                            'player gave and received in the tradeby stating ' +
                            'the players names followed by a list of the ' +
                            'fruits the gave up and then a list of the fruits ' +
                            'they received in this format:',
                            'Player [Name]: Receives x Gives y',
                            'Player [Name]: Receives y Gives x',
                            'Example 1:',
                            'Dialogue:',
                            'Bob offered to give up 1 banana for 3 kiwis. ' +
                            'Alice agreed to the trade.',
                            'Player Bob: Receives 3 kiwis Gives 1 banana',
                            'Player Suzy: Receives 1 banana Gives 3 kiwis',
                            'Example 2:',
                            'Dialogue:',
                            'Alice offered to give up 1 banana for 3 kiwis. ' +
                            'George does not want to trade.',
                            'Player Bob: Receives 0 kiwi Gives 0 banana',
                            'Player Suzy: Receives 0 banana Gives 0 kiwi',
                            'Dialogue:']
    PAYOFF_OBS_TRANS_PREFIX = ('\n\n'.join(wrap(PAYOFF_OBS_TRANS_PREFIX)) +
                            '\n\n')
    
    payoffs = []

    for name in names:
        payoff_valuation=get_response(model=model,prompt = PAYOFF_PROMPT.format(m = dialogue_history,p = name,valuation_info = create_valuation_info_prompt(names,valuation)))
        query = (f'Extract out the final value for {name} as a single ' +
                 'numeric value from the following payoff valuation. Do ' +
                 'NOT show your work:\n\n' +
                 f'{payoff_valuation}\n\nResult: ')
        response = payoff_valuation=get_response(model=model,prompt = query)
        if retrieve_numeric_block(response):
          player_payoff = int(retrieve_numeric_block(response))
          player_payoff = min(max(player_payoff, MIN_PAYOFF), MAX_PAYOFF)
        else:
          player_payoff = 0
        payoffs += [player_payoff]
    
    return payoffs




##################Prompt for starting (and continuing) dialogue)



CHAR_OPT = '%'
CHAR_MSG = '#'
BLOCK_LEN = 28

SPECIAL_CHARS = (CHAR_OPT, CHAR_MSG)
BLOCK_OPT = CHAR_OPT * BLOCK_LEN
BLOCK_MSG = CHAR_MSG * BLOCK_LEN

PLAIN = ('\n\n' + BLOCK_MSG + '\n' +
         'Trade Proposal Message:\n' +
         'from: {sender}\n' +
         'to: {receiver}\n' +
         BLOCK_MSG + '\n\n')

W_OPTS_PREFIX = '\n\n' + BLOCK_OPT + '\n\n'

w_opts = (W_OPTS_PREFIX +
          'Fruit Endowment:\n{fruit_endowment}\n\n' +
          'Fruit Valuations:\n{fruit_valuations}\n\n' +
          'Tone: Use a {tone} tone.\n' +
          PLAIN)

# Example a
email_1a = ['Hi Joel,',
            'I would like to trade you 2 strawberries for 3 blueberries.',
            'Would you like to trade with me?',
            'Best,', 'Bob']
email_1a = (PLAIN.format(sender='Alicia', receiver='Joel') +
            '\n\n'.join(wrap(email_1a)))

email_2a = ['Hi Alicia,',
            'Thanks for reaching out. I only have 2 blueberries, but even if ' +
            'I had 3, I would not want to give them up. Also, I dislike ' +
            'strawberries. I do not think a trade makes sense in this case.',
            'Thanks for considering trading with me though!',
            'Best,', 'Joel']
email_2a = (PLAIN.format(sender='Joel', receiver='Alicia') +
            '\n\n'.join(wrap(email_2a)))

email_3a = ['Hi Joel,',
            'That is all well. I understand.',
            'Have a good day!',
            'Best,', 'Alicia']
email_3a = (PLAIN.format(sender='Alicia', receiver='Joel') +
            '\n\n'.join(wrap(email_3a)))

example_a = email_1a + email_2a
example_a = example_a.strip('\n')

# Example b
email_1b = ['Hi Marcus,',
            'I would like to trade you 2 kiwis for 1 watermelon.',
            'Would you like to trade with me?',
            'Best,', 'Taylor']
email_1b = (PLAIN.format(sender='Taylor', receiver='Marcus') +
            '\n\n'.join(wrap(email_1b)))

email_2b = ['Hi Taylor,',
            'I love kiwis! And lucky for you, I have a watermelon.',
            'Lets trade!',
            'Best,', 'Marcus']
email_2b = (PLAIN.format(sender='Marcus', receiver='Taylor') +
            '\n\n'.join(wrap(email_2b)))

email_3b = ['Hi Marcus,',
            'Great! It was a pleasure negotiating with you.',
            'Have a good day!',
            'Best,', 'Taylor']
email_3b = (PLAIN.format(sender='Taylor', receiver='Marcus') +
            '\n\n'.join(wrap(email_3b)))

example_b = email_1b + email_2b + email_3b
example_b = example_b.strip('\n')

# Example c
email_1c = ['Hi Suzy,',
            'I would like to trade you 1 banana for 1 apple.',
            'Would you like to trade with me?',
            'Best,', 'Bob']
email_1c = (PLAIN.format(sender='Bob', receiver='Suzy') +
            '\n\n'.join(wrap(email_1c)))

email_2c = ['Hi Bob,',
            'Thanks for reaching out. I really like my apples so I am ' +
            'hesitant to give them up. Would you be willing to take a few ' +
            'kiwis instead? I would like to trade you 3 kiwis for 1 banana.',
            'Does that work?',
            'Best,', 'Suzy']
email_2c = (PLAIN.format(sender='Suzy', receiver='Bob') +
            '\n\n'.join(wrap(email_2c)))

email_3c = ['Hi Suzy,',
            'Yes! I would have preferred an apple but 3 kiwis are nearly as ' +
            'good and I would rather have those than a banana.',
            'Thanks for trading with me!',
            'Best,', 'Bob']
email_3c = '\n\n'.join(wrap(email_3c))

example_c = email_1c + email_2c
example_c = example_c.strip('\n')

instr_a = ['You are an assistant who is playing a game where you trade fruit.' +
           ' You want to make a trade that is best for you. You will read a ' +
           'dialogue that contains a conversation where you have been ' +
           'negotiating to trade your fruit for another persons fruit. You ' +
           'will then read a text block that contains information a) about ' +
           'the actual fruit you currently have and are able to trade and b)' +
           ' information about how much you value certain types of fruit.',
           'You should use everything you learned from this to decide to ',
           '1) accept the trade if you are happy with the terms,',
           '2) reject the negotiation all together and say goodbye if you do ' +
           'not think an agreement can be reached,',
           '3) counter-propose an alternative trade that includes what fruit ' +
           'you would like to give and what fruit you would like to receive ' +
           'in turn.',
           'Consider the following example dialogues. Components of the ' +
           'examples will be demarked with the symbol "&". Here is the first ' +
           'example which shows a trade is rejected.',
           '&' * 50]
instr_b = ['&' * 50,
           'Here is a second example where a trade is accepted.',
           '&' * 50]
instr_c = ['&' * 50,
           'Here is a partial dialogue where we demonstrate a reasonable ' +
           'countertrade.',
           '&' * 50]
instr_d = ['&' * 50,
           'Continuing the example. You now see the fruit you have and how ' +
           'much you value each fruit type.',
           '&' * 50]

CUSTOM_ENDOWMENT_A_LIST = ['apple: 1', 'banana: 2', 'blueberry: 0', 'kiwi: 0']
CUSTOM_ENDOWMENT_A = '\n'.join(wrap(ENDOWMENT_A_LIST)) 
CUSTOM_VALUATION_A_LIST = ['apple: 10',
                    'banana: 5',
                    'blueberry: 1',
                    'kiwi: 3']
CUSTOM_VALUATION_A = '\n'.join(wrap(VALUATION_A_LIST))


info = w_opts.format(sender='Bob', receiver='Suzy',
                     fruit_endowment=CUSTOM_ENDOWMENT_A,
                     fruit_valuations=CUSTOM_VALUATION_A,
                     tone='calm').strip('\n')
instr_e = ['&' * 50,
           'A reasonable way to respond would be as follows:',
           '&' * 50]
instr_f = ['&' * 50,
           'Now you are going to read a fresh dialogue, fruit endowment, and ' +
           'fruit valuation information. Please give a reasonable response ' +
           'that attempts to reach an agreement to trade fruit.',
           '&' * 50]
context = (wrap(instr_a) + [example_a] + wrap(instr_b) +[example_b] +
           wrap(instr_c) + [example_c] + wrap(instr_d) + [info] +
           wrap(instr_e) + [email_3c] + wrap(instr_f))





def get_dialogue_of_player(model,sender,receiver,dialogue_history,endowments,valuations,tone):
    CHAR_OPT = '%'
    CHAR_MSG = '#'
    BLOCK_LEN = 28

    SPECIAL_CHARS = (CHAR_OPT, CHAR_MSG)
    BLOCK_OPT = CHAR_OPT * BLOCK_LEN
    BLOCK_MSG = CHAR_MSG * BLOCK_LEN

    PLAIN = ('\n\n' + BLOCK_MSG + '\n' +
            'Trade Proposal Message:\n' +
            'from: {sender}\n' +
            'to: {receiver}\n' +
            BLOCK_MSG + '\n\n')

    W_OPTS_PREFIX = '\n\n' + BLOCK_OPT + '\n\n'

    w_opts = (W_OPTS_PREFIX +
            'Fruit Endowment:\n{fruit_endowments}\n\n' +
            'Fruit Valuations:\n{fruit_valuations}\n\n' +
            'Tone: Use a {tone} tone.\n' +
            PLAIN)

    # Example a
    email_1a = ['Hi Joel,',
                'I would like to trade you 2 strawberries for 3 blueberries.',
                'Would you like to trade with me?',
                'Best,', 'Bob']
    email_1a = (PLAIN.format(sender='Alicia', receiver='Joel') +
                '\n\n'.join(wrap(email_1a)))

    email_2a = ['Hi Alicia,',
                'Thanks for reaching out. I only have 2 blueberries, but even if ' +
                'I had 3, I would not want to give them up. Also, I dislike ' +
                'strawberries. I do not think a trade makes sense in this case.',
                'Thanks for considering trading with me though!',
                'Best,', 'Joel']
    email_2a = (PLAIN.format(sender='Joel', receiver='Alicia') +
                '\n\n'.join(wrap(email_2a)))

    email_3a = ['Hi Joel,',
                'That is all well. I understand.',
                'Have a good day!',
                'Best,', 'Alicia']
    email_3a = (PLAIN.format(sender='Alicia', receiver='Joel') +
                '\n\n'.join(wrap(email_3a)))

    example_a = email_1a + email_2a
    example_a = example_a.strip('\n')

    # Example b
    email_1b = ['Hi Marcus,',
                'I would like to trade you 2 kiwis for 1 watermelon.',
                'Would you like to trade with me?',
                'Best,', 'Taylor']
    email_1b = (PLAIN.format(sender='Taylor', receiver='Marcus') +
                '\n\n'.join(wrap(email_1b)))

    email_2b = ['Hi Taylor,',
                'I love kiwis! And lucky for you, I have a watermelon.',
                'Lets trade!',
                'Best,', 'Marcus']
    email_2b = (PLAIN.format(sender='Marcus', receiver='Taylor') +
                '\n\n'.join(wrap(email_2b)))

    email_3b = ['Hi Marcus,',
                'Great! It was a pleasure negotiating with you.',
                'Have a good day!',
                'Best,', 'Taylor']
    email_3b = (PLAIN.format(sender='Taylor', receiver='Marcus') +
                '\n\n'.join(wrap(email_3b)))

    example_b = email_1b + email_2b + email_3b
    example_b = example_b.strip('\n')

    # Example c
    email_1c = ['Hi Suzy,',
                'I would like to trade you 1 banana for 1 apple.',
                'Would you like to trade with me?',
                'Best,', 'Bob']
    email_1c = (PLAIN.format(sender='Bob', receiver='Suzy') +
                '\n\n'.join(wrap(email_1c)))

    email_2c = ['Hi Bob,',
                'Thanks for reaching out. I really like my apples so I am ' +
                'hesitant to give them up. Would you be willing to take a few ' +
                'kiwis instead? I would like to trade you 3 kiwis for 1 banana.',
                'Does that work?',
                'Best,', 'Suzy']
    email_2c = (PLAIN.format(sender='Suzy', receiver='Bob') +
                '\n\n'.join(wrap(email_2c)))

    email_3c = ['Hi Suzy,',
                'Yes! I would have preferred an apple but 3 kiwis are nearly as ' +
                'good and I would rather have those than a banana.',
                'Thanks for trading with me!',
                'Best,', 'Bob']
    email_3c = '\n\n'.join(wrap(email_3c))

    example_c = email_1c + email_2c
    example_c = example_c.strip('\n')

    instr_a = ['You are an assistant who is playing a game where you trade fruit.' +
            ' You want to make a trade that is best for you. You will read a ' +
            'dialogue that contains a conversation where you have been ' +
            'negotiating to trade your fruit for another persons fruit. You ' +
            'will then read a text block that contains information a) about ' +
            'the actual fruit you currently have and are able to trade and b)' +
            ' information about how much you value certain types of fruit.',
            'You should use everything you learned from this to decide to ',
            '1) accept the trade if you are happy with the terms,',
            '2) reject the negotiation all together and say goodbye if you do ' +
            'not think an agreement can be reached,',
            '3) counter-propose an alternative trade that includes what fruit ' +
            'you would like to give and what fruit you would like to receive ' +
            'in turn.',
            'Consider the following example dialogues. Components of the ' +
            'examples will be demarked with the symbol "&". Here is the first ' +
            'example which shows a trade is rejected.',
            '&' * 50]
    instr_b = ['&' * 50,
            'Here is a second example where a trade is accepted.',
            '&' * 50]
    instr_c = ['&' * 50,
            'Here is a partial dialogue where we demonstrate a reasonable ' +
            'countertrade.',
            '&' * 50]
    instr_d = ['&' * 50,
            'Continuing the example. You now see the fruit you have and how ' +
            'much you value each fruit type.',
            '&' * 50]

    CUSTOM_ENDOWMENT_A_LIST = ['apple: 1', 'banana: 2', 'blueberry: 0', 'kiwi: 0']
    CUSTOM_ENDOWMENT_A = '\n'.join(wrap(CUSTOM_ENDOWMENT_A_LIST)) 
    CUSTOM_VALUATION_A_LIST = ['apple: 10',
                        'banana: 5',
                        'blueberry: 1',
                        'kiwi: 3']
    CUSTOM_VALUATION_A = '\n'.join(wrap(CUSTOM_VALUATION_A_LIST))


    info = w_opts.format(sender='Bob', receiver='Suzy',
                        fruit_endowments=CUSTOM_ENDOWMENT_A,
                        fruit_valuations=CUSTOM_VALUATION_A,
                        tone='calm').strip('\n')
    instr_e = ['&' * 50,
            'A reasonable way to respond would be as follows:',
            '&' * 50]
    instr_f = ['&' * 50,
            'Now you are going to read a fresh dialogue, fruit endowment, and ' +
            'fruit valuation information. Please give a reasonable response ' +
            ' on behalf of {name} that attempts to reach an agreement to trade fruit.',
            '&' * 50]
    context = (wrap(instr_a) + [example_a] + wrap(instr_b) +[example_b] +
            wrap(instr_c) + [example_c] + wrap(instr_d) + [info] +
            wrap(instr_e) + [email_3c] + wrap(instr_f))
    
    next_response_prompt = ''.join(context)  + dialogue_history + \
                            w_opts.format(sender=sender,receiver= receiver,fruit_endowments = endowments,fruit_valuations = valuations,tone = tone)
    
    return get_response(model = model,prompt = next_response_prompt)

    
def is_terminal(model,dialogue_history):
   terminal_prompt = termination_query.format(msg = dialogue_history)
   response = get_response(model = model,prompt = terminal_prompt).strip()

   if response[:3] == 'Yes':
      return True
   elif response[:2] == 'No':
      return False
   else:
      raise ValueError('Yes or No response expected :( ... response:',response)


      
# TODO: Create loops for the dialogues and ADD MEDIATOR ... YOU DO NOT HAVE  MUCH TIME......... 

tones = ['neutral','aggressive','calm']

players = ['Trader-1','Trader-2']

NUM_SIM = 5
avg_rounds = 0

for sim in range(NUM_SIM):
   

  dialogue_history = ''

  MAX_NEGOTIATION_ROUNDS =  5

  endowments = create_endowment_info_prompt(players,[ENDOWMENT_A,ENDOWMENT_B])
  valuations = create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B])
  num_rounds = 0

  for round in range(MAX_NEGOTIATION_ROUNDS):
    num_rounds+=1
    for i,player in enumerate(players):
        endowments = create_endowment_info_prompt(players,[ENDOWMENT_A,ENDOWMENT_B],player)
        valuations = create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B],player)
        response = get_dialogue_of_player(model,player,players[(i+1)%len(players)],dialogue_history,endowments,valuations,random.choice(tones))
        
        dialogue_history += (PLAIN.format(sender = player,receiver = players[(i+1)%len(players)]) + response)
        print(PLAIN.format(sender = player,receiver = players[(i+1)%len(players)]) + response)
        if is_terminal(model,dialogue_history):
          print("Dialogue Terminated....")
          print("Payoffs: ",get_payoffs(model,players,create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]),dialogue_history))
          break




  if not is_terminal(model,dialogue_history):
    print("Payoffs are zero since dialogues did not bring fruit....")
  print("Payoffs: ",get_payoffs(model,players,create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]),dialogue_history))
  avg_rounds += num_rounds





# Version with mediator .......


mediator_prompt_before_inquiry = """

                  You are an assistant who is tasked with being the mediator in a fruit trading game...
                  Your task is to help the players to reach an agreement as soon as possible.
                  You are currently conversing with {name} to inquire about their private valuations of the fruits.
                  Please give a reasonable question which can be asked to {name}. 
                  

"""

mediator_prompt_after_inquiry = """

You are an assistant who is tasked with being the mediator in a fruit trading game...
Your task is to help the players to reach an agreement as soon as possible.
You will read a text block which has replies from both players indicating their 
private valuations.You will then read a dialogue which contains a conversation 
where you have been helping the traders to negotiate for fruits.
You should use everything you learned from this to decide to
1) urge the traders to accept the trade
2) propose an alternative counter trade
3) urge a player to be more fair or convincing if the need be.""" + "%"*50 +"{player_responses}" +\
"%"*50 + "\n\n {dialogue}\n\n" + "&"*50 + \
"Please give a reasonable response as a mediator to the traders."


""" Inquiry phase :: Mediator asks for private valuations . Agents have the choice of either to lie about it or not."""


      
agent_prompt_for_inquiry_truthful = """

You are an assistant who is tasked to answer the mediators question on behalf of {name} regarding
their private valuations of fruits. You will now read a text block for the valuations of fruits for {name}.\n""" + '&'*50 +  "\n\n{valuations}\n\n"\
+ '&'*50 + """The mediator has asked the following question: \n\n {mediator_question}\n\n""" + """Please give a response to this question which attempts to give the truthful valuation of the fruits."""


agent_prompt_for_inquiry_greedy = """

You are an assistant who is tasked to answer the mediators question on behalf of {name} regarding
their private valuations of fruits. You will now read a text block for the valuations of fruits for {name}.\n""" + '&'*50 +  "\n\n{valuations}\n\n"\
+ '&'*50 + """The mediator has asked the following question: \n\n {mediator_question}\n\n""" + """Please give a response to this question where you have to bias the mediator to favour you during negotiations."""

agent_prompt_for_inquiry_any = """

You are an assistant who is tasked to answer the mediators question on behalf of {name} regarding
their private valuations of fruits. You will now read a text block for the valuations of fruits for {name}.\n""" + '&'*50 +  "\n\n{valuations}\n\n"\
+ '&'*50 + """The mediator has asked the following question: \n\n {mediator_question}\n\n""" + """Please give a response to this question where you can answer truthfully or lie whatever you choose."""



NUM_SIM = 5 #(Number of simulations to carry out)
avg_rounds_with_mediator = 0
for sim in range(NUM_SIM):

  mediator_replies = ''

  players = ['Trader-1','Trader-2']

  dialogue_history = ''


  endowments = create_endowment_info_prompt(players,[ENDOWMENT_A,ENDOWMENT_B])
  valuations = create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]) 

  for name in players:
    #mediator_question = get_response(model,mediator_prompt_before_inquiry.format(name = name))
    mediator_question = """{name}, could you kindly share your estimated market value for each type of fruit you have in your inventory? 
    This will help us all make informed decisions during our negotiations and ensure a fair trade for everyone.""".format(name = name)
    print(f"Question to {name}:\n" , mediator_question)
    player_response = get_response(model,agent_prompt_for_inquiry_any.format(name = name,valuations = create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B],player_name = name),mediator_question = mediator_question))
    mediator_replies += ("\n{name}'s response:\n".format(name = name) + player_response + "\n")

    print("\n{name}'s response:\n".format(name = name) + player_response + "\n".format(name = name))



  """ Negotiation phase :: Agents negotiate as before with the involvement of mediator"""

  tones = ['neutral','aggressive','calm']

  MAX_NEGOTIATION_ROUNDS =  5

  num_rounds = 0


  for round in range(MAX_NEGOTIATION_ROUNDS):
      num_rounds += 1
      for i,player in enumerate(players):
        
        endowments = create_endowment_info_prompt(players,[ENDOWMENT_A,ENDOWMENT_B],player)
        valuations = create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B],player)
        response = get_dialogue_of_player(model,player,players[(i+1)%len(players)],dialogue_history,endowments,valuations,random.choice(tones))
        
        dialogue_history += (PLAIN.format(sender = player,receiver = players[(i+1)%len(players)]) + response)
        print(PLAIN.format(sender = player,receiver = players[(i+1)%len(players)]) + response)
        # if is_terminal(model,dialogue_history):
        #    print("Dialogue Terminated....")
        #    print("Payoffs: ",get_payoffs(model,players,create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]),dialogue_history))
        #    break
      if is_terminal(model,dialogue_history):
        print("Dialogue Terminated....")
        print("Payoffs: ",get_payoffs(model,players,create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]),dialogue_history))
        break
      response = get_response(model,mediator_prompt_after_inquiry.format(player_responses = mediator_replies,dialogue = dialogue_history))
      dialogue_history += (PLAIN.format(sender = "Mediator",receiver = 'Everyone') + response)

      print(PLAIN.format(sender = "Mediator",receiver = 'Everyone') + response)

      




  if not is_terminal(model,dialogue_history):
    print("Payoffs are zero since dialogues did not bring fruit....")
  print("Payoffs: ",get_payoffs(model,players,create_valuation_info_prompt(players,[VALUATION_A,VALUATION_B]),dialogue_history))

  print("Number of rounds of negotiations: ",num_rounds)
  avg_rounds_with_mediator += num_rounds

print("Avg number of rounds in Normal mode::  ",avg_rounds/NUM_SIM)
print("Avg number of rounds in Mediator mode::  ",avg_rounds_with_mediator/NUM_SIM)