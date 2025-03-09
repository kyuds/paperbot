from agent import PaperBot
from errors import BaseError

def main():
    bot = PaperBot("bot")
    recommendations = bot.suggest()
    print("Recommended:")
    for s in recommendations:
        print(s + "\n")
    
    feedback = input("Do you want to give feedback? [yes/no]: ")
    if feedback == "yes":
        contents = input("Please give feedback: ")
        bot.feedback(contents)
    else:
        print("you chose to not give feedback")

if __name__ == "__main__":
    main()
