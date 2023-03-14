import numpy as np
import matplotlib.pyplot as plt

### General functions
def image_size(image_name):
  height, width = image_name.shape
  print(f"The height of the image is {height}, and the width is {width}")

def check_integrity(image_name, row_val=0):
  idx = np.where(image_name[row_val] < 0)[0][0]
  print(f"Column error index: {idx}")

def shift_image(image_name, shift_value):
  size = image_name.shape
  image_flat = image_name.flatten()
  image_rolled = np.roll(image_flat, -1*(shift_value + 1))
  image_name = image_rolled.reshape(size)
  print(f"Shift complete")
  return image_name

def data_correct(image_name, proof):
  check = np.array_equal(image_name, proof)
  if check:
    print("Congrats you corrected the data.")
  else:
    print("The data is corrupted.")
  return check

def plot_image(image):
  plt.imshow(image)

# game functions

class chapter:
  ''' This holds the scenario information
  '''

  def __init__(self, filename):
    self.chapter_info = np.load(filename+".npy")
    self.path = self.chapter_info[0]
    self.image = self.load(self.path)
    self.shift = int(self.chapter_info[1])
    self.rows = self.chapter_info[2]

  def load(self, path):
    return np.load(path)
  

class Game:
    ''' This holds the game data 
    '''
    def __init__(self, received_data, proof_image):
      self.data = received_data
      self.solution = proof_image

    def get_data(self):
      return self.data
    
    def get_solution(self):
      return self.solution
    
    def show_image(self):
      plt.imshow(self.data)

def setup_chapter(chapter):
  image = chapter.image
  shift = chapter.shift
  height, width = image.shape
  corrupt_data = np.full(height, -1)
  solution_image = np.column_stack((image, corrupt_data))
  new_width = width + 1
  damaged_image = np.roll(solution_image.flatten(), shift).reshape(height, new_width)
  return Game(damaged_image, solution_image)

class Parser:
  ''' The parser interprets the instructions to terminal
  '''
  def __init__(self, Game):
    # A list of all of the commands that the player has issued.
    self.command_history = []
    # A pointer to the game.
    self.game = Game
    self.data_manipulation = Game.get_data()

  def get_player_intent(self, command):
    command = command.lower()
    if "reset" in command:
      return "reset"
    elif "size" in command:
      return "size"
    elif "check" in command:
      return "check"
    elif "shift" in command:
      return "shift"
    elif "correct" in command:
      return "correct"
    else:
      return "NaC"


  def parse_command(self, command):
    # add this command to the history
    self.command_history.append(command)

    # By default, none of the intents end the game. The following are ways this
    # flag can be changed to True.
    end_game = False

    # Intents are functions that can be executed
    intent = self.get_player_intent(command)
    if intent == "reset":
      self.reset()
    elif intent == "size":
      image_size(self.data_manipulation)
    elif intent == "check":
      self.integrity(command)
    elif intent == "shift":
      self.shift_func(command)
    elif intent == "correct":
      end_game = self.proof_data()
    else:
      print("I'm not sure what you want to do.")
    return end_game

  def reset(self):
    self.data_manipulation = self.game.get_data()
    print("Data has been reseted")
    
  def proof_data(self):
    end_game = data_correct(self.data_manipulation, self.game.get_solution())
    return end_game
  
  def integrity(self, command):
    command = command.lower()
    args = command.split()
    height, width = self.data_manipulation.shape
    if len(args)==1:
      check_integrity(self.data_manipulation)
    else:
      arg1, arg2 = self.arg_parser(args)
      if  len(args)==2 and 0 <= arg1 < height:
        check_integrity(self.data_manipulation, arg1)
      elif len(args)==3 and 0 <= arg2 < height:
        check_integrity(self.data_manipulation, arg2)
      else:
        print("Check integrity of data: are your arguments correct?")

  def shift_func(self, command):
    command = command.lower()
    args = command.split()
    if len(args) < 2:
      print("There is no shift value")
      return
    arg1, arg2 = self.arg_parser(args)
    if arg1 != 0:
      # print("arg1 used")
      self.data_manipulation = shift_image(self.data_manipulation, arg1)
    elif arg2 != 0:
      # print("arg2 used")
      self.data_manipulation = shift_image(self.data_manipulation, arg2)
    else:
      print("The data was not shifted")
    
  def arg_parser(self, args):
    if len(args)>=2:
        arg1 = args[1]
        if arg1.isdigit():
          arg1 = int(arg1)
        else:
          arg1 = 0
        arg2 = 0
    if len(args)>=3:
      arg2 = args[2]
      if arg2.isdigit():
        arg2 = int(arg2)
      else:
        arg2 = 0 
    return arg1, arg2

def game_loop(game):
  parser = Parser(game)
  command = ""
  while not (command.lower() == "exit" or command.lower == "q"):
    print("Please give me an instruction:")
    command = input(">")
    end_game = parser.parse_command(command)
    if end_game:
      return parser.data_manipulation 