import copy
import string
import numpy as np
import matplotlib.pyplot as plt

### General functions
def image_size(image_name):
  height, width = image_name.shape
  print(f"The height of the image is {height}, and the width is {width}")

def check_integrity(image_name, row_val=0):
  idx = np.where(image_name[row_val] < 0)[0][0]
  if idx == (image_name.shape[1] - 1) :
    print(f"Column correctly positioned")
  else:
    print(f"Column error index: {idx}")
  return idx


def shift_image(original_name, shift_value, row = None):
  image_name = original_name.copy()
  if row is None:
    size = image_name.shape
    for i in range(size[0]):
      image_name[i] = np.roll(image_name[i], -1*(shift_value + 1))
    print(f"Shift complete {shift_value} index for all rows.")
  else:
    image_rolled = np.roll(image_name[row], -1*(shift_value + 1))
    image_name[row] = image_rolled
    print(f"Shift complete {shift_value} index for {row} row.")
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

def cipher(text, shift):
  alphabet = string.ascii_lowercase
  shift_alphabet = alphabet[shift:] + alphabet[:shift]
  table = str.maketrans(alphabet, shift_alphabet)
  return text.translate(table)

def decipher_game(game):
  command = ""
  counter = 0
  test_cipher = game.get_code()
  while not (command.lower() == "exit"or command.lower=="q"):
    command = input(">> ")
    if "exit" in command:
      continue
    if "reset" in command:
      test_cipher = game.get_code()
      counter = 0
      print("phrase reset. Words unlocked.")
    args = command.split()
    if args[0] == "cipher":
      shift = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
      lock = True if len(args) > 2  and args[2] == "lock" else False
      words = test_cipher.split()
      decipher_words = words.copy()
      for i in range(counter, len(words)):
        decipher_words[i] = cipher(words[i], 26 - shift)
      if lock and counter < len(words):
        words[counter] = decipher_words[counter]
        test_cipher = " ".join(words)
        print(f"locked word {counter}")
        print(test_cipher)
        counter += 1
      elif lock and counter >= len(words):
        print("All words are locked")
        print(test_cipher)
      else:
        print("This is the code:")
        print(" ".join(decipher_words))
    elif args[0] == "passphrase":
      if test_cipher == game.get_passphrase():
        print("Data deciphered.")
        return False, game.get_data() - 106
      else:
        print("wrong, reset and try again.")
  return game.get_cipher(), game.get_data()

# game functions

class chapter:
  ''' This holds the scenario information
  '''

  def __init__(self, filename):
    self.chapter_info = np.load(filename+".npy")
    self.path = self.chapter_info[0]
    self.image = self.load(self.path)
    self.shift = self.chapter_info[1] if self.chapter_info[1] == 'random' else int(self.chapter_info[1])
    self.rows = self.chapter_info[2]
    if self.rows == "cipher":
      self.damaged_data = self.chapter_info[3]
      self.phrase = self.chapter_info[4]
      self.passphrase = self.chapter_info[5]

  def load(self, path):
    return np.load(path)
  

class Game:
    ''' This holds the game data 
    '''
    def __init__(self, received_data, proof_image, cipher = False, phrase = None, passphrase = None):
      self.data = received_data
      self.solution = proof_image
      self.cipher = cipher
      if self.cipher:
        self.phrase = phrase
        self.passphrase = passphrase

    def get_data(self):
      return self.data
    
    def get_solution(self):
      return self.solution
    
    def get_passphrase(self):
      if self.cipher:
        return self.phrase
      else:
        return None

    def get_code(self):
      if self.cipher:
        return self.passphrase
      else:
        return None
    
    def get_cipher(self):
      return self.cipher
    
    def show_image(self):
      plt.imshow(self.data)

def setup_chapter(chapter):
  image = chapter.image
  height, width = image.shape
  corrupt_data = np.full(height, -1)
  solution_image = np.column_stack((image, corrupt_data))

  if chapter.rows != "cipher":
    new_width = width + 1
    damaged_image = solution_image.copy()
    rows = height
    if chapter.shift != 'random':
      shift = np.full(rows, chapter.shift)
    else:
      if chapter.rows == 'all':
        shift = np.full(rows, np.random.randint(0,width, 1))
      else:
        shift = np.random.randint(0,width, height)
        rows = len(shift)
    for i in range(rows):
        damaged_image[i] = np.roll(solution_image[i], shift[i])
    return Game(damaged_image, solution_image)
  elif chapter.rows == "cipher":
    damaged_image = np.load(chapter.damaged_data)
    phrase = chapter.phrase
    passphrase = chapter.passphrase
    return Game(damaged_image, solution_image, cipher=True, phrase = phrase, passphrase=passphrase)

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
    elif "loop" in command:
      return "loop"
    elif "tandem" in command:
      return "tandem"
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

  def instructions_selector(self,intent, command):
    end_game = False

    if intent == "tandem":
      end_game = self.tandem(command)
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
    elif intent == "loop":
      end_game = self.loop(command)
    else:
      end_game = self.instructions_selector(intent, command)
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
    if type(arg1)==int and type(arg2)==int is not None:
      # print("arg1 used")
      self.data_manipulation = shift_image(self.data_manipulation, arg1, row=arg2)
    elif arg2 is None and arg1 is not None:
      # print("arg2 used")
      self.data_manipulation = shift_image(self.data_manipulation, arg1)
    else:
      print("The data was not shifted")
    
  def arg_parser(self, args):
    arg1 = args[1]
    arg2 = None
    if arg1.isdigit():
      arg1 = int(arg1)
    else:
      arg1 = None
    if len(args) > 2:
      arg2 = args[2]
      if arg2.isdigit():
        arg2 = int(arg2)
    return arg1, arg2
  
  def loop(self, command):
    
    command = command.lower()
    args = command.split()
    if args[0] != "loop":
      print("The loop instruction is not used correctly, try again.")
    else:
      subargs = args[1:]
      func1 = self.get_player_intent(" ".join(subargs))
      result = False
      if len(subargs) == 2:
        if subargs[1].isdigit(): 
          rep = subargs[1]
        else:
          rep = 0
          print("Mistake: number of loops unknown")  
        for i in range(int(rep)):
          result = self.instructions_selector(func1, func1 + " " + str(i))
      elif func1 == "tandem":
        params = []
        k = 1
        while k < (len(subargs)):
          intent = self.get_player_intent(subargs[k])
          k+=1
          if intent == "NaC":
            continue
          else:
            params.append(intent) 
          if len(params) == 2:
            break
          
        rep = '0'
        for i in subargs:
          if i.isdigit():
            rep = i
            break
        for i in range(int(rep)):
          result = self.instructions_selector(func1, func1 + " " + params[0] + " " + str(i) + " " +params[1] + " row") 
      
      return result
    return False

  
  def tandem(self, command):
    '''
    the tandem function allows to concatenate instructions. It is considered only 1 instruction.
    '''
    command = command.lower()
    args =  command.split()
    if args[0] != "tandem":
      print("The tandem instruction is not used correctly, check your order.")
      return
    else:
      subargs = args[1:5]
      if len(subargs) >= 3:
        if subargs[1].isdigit():
          buffer = self.tandem_parser(subargs[0], subargs[1])
          if len(subargs)>3 and subargs[3] == "row":
            self.tandem_parser(subargs[2], buffer, subargs[1])
          else:
            self.tandem_parser(subargs[2], buffer)
          if subargs[2] == "correct":
            return np.array_equal(self.data_manipulation, self.game.get_solution())
        else:
          subargs.pop(1)
      
      if len(subargs) == 2:
        if subargs[0] == "shift":
          print("shift instruction needs a shift value")
          return
        else:
          buffer = self.tandem_parser(subargs[0])
          self.tandem_parser(subargs[1], buffer)
          if subargs[1] == "correct":
            return np.array_equal(self.data_manipulation, self.game.get_solution())
      
    return False


  def tandem_parser(self, arg, arg2 = '0', arg3 = None):
    save_val = 0
    if arg == "size":
      image_size(self.data_manipulation)
    elif arg == "check":
      save_val = check_integrity(self.data_manipulation, int(arg2))
    elif arg == "shift":
      if arg3 is None:
        self.shift_func(arg + " " + arg2)
      else:
        self.shift_func(arg + " " + arg2 + " " + arg3)
    elif arg == "correct":
      self.proof_data()
    return str(save_val)
        



def game_loop(game):
  internal_game = copy.deepcopy(game)
  if internal_game.get_cipher():
    print("The data is ciphered, deciphering is needed first.")
    internal_game.cipher, internal_game.data = decipher_game(internal_game)
    if internal_game.get_cipher():
      print("Data still not deciphered. Exiting.")
      return

  parser = Parser(internal_game)
  command = ""
  while not (command.lower() == "exit" or command.lower == "q"):
    print("Please give me an instruction:")
    command = input(">")
    end_game = parser.parse_command(command)
    if end_game:
      break
  
  return parser.data_manipulation 
