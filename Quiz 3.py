class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


error_message = "Please Select One Of Available Options!"
score = 0
count = 1
question_count = 10
game_over = False
categories_dict = {
    '18': 'Science_Computers',
    '9': 'General_Knowledge',
    '27': 'Animals',
    '28': 'Vehicles',
    '21': 'Sports'
}
difficulties_dict = {
    '1': 'easy',
    '2': 'medium',
    '3': 'hard'
}


def User_Category():
    # Prints Categories And Prompts User To Choose One Of Them
    while True:
        user_category = input(
            f"{bcolors.OKBLUE}Choose Category{bcolors.ENDC}\n"
            f"{bcolors.FAIL}9{bcolors.ENDC} : {bcolors.OKCYAN}General Knowledge{bcolors.ENDC}\n"
            f"{bcolors.FAIL}18{bcolors.ENDC} : {bcolors.OKCYAN}Science Computers{bcolors.ENDC}\n"
            f"{bcolors.FAIL}21{bcolors.ENDC} : {bcolors.OKCYAN}Sports{bcolors.ENDC}\n"
            f"{bcolors.FAIL}27{bcolors.ENDC} : {bcolors.OKCYAN}Animals{bcolors.ENDC}\n"
            f"{bcolors.FAIL}28{bcolors.ENDC} : {bcolors.OKCYAN}Vehicles{bcolors.ENDC}\n"
            f"{bcolors.OKGREEN}Choice{bcolors.ENDC} : ")
        if user_category in categories_dict.keys():
            return user_category
        else:
            print(f'{bcolors.WARNING}{error_message}{bcolors.ENDC}\n')


def User_Difficulty():
    # Prints Categories And Prompts User To Choose One Of Them
    while True:
        user_difficulty = input(f"{bcolors.OKBLUE}Choose Difficulty{bcolors.ENDC}\n{bcolors.FAIL}1{bcolors.ENDC} : "
                                f"{bcolors.OKGREEN}Easy{bcolors.ENDC}\n{bcolors.FAIL}2{bcolors.ENDC} : "
                                f"{bcolors.WARNING}Medium{bcolors.ENDC}\n{bcolors.FAIL}3{bcolors.ENDC} : "
                                f"{bcolors.FAIL}Hard{bcolors.ENDC}\n"
                                f"{bcolors.OKGREEN}Choice{bcolors.ENDC} : ")
        if user_difficulty in difficulties_dict.keys():
            return user_difficulty
        else:
            print(f'{bcolors.WARNING}{error_message}{bcolors.ENDC}\n')


def Connect_To_DB(db):
    # Connects To Database
    import sqlite3
    return sqlite3.connect(db)


def Create_DB(ch_category):
    # Connects To Database And Creates The Chosen Category Table If It Doesn't Exist Yet
    connect = Connect_To_DB('Questions.db')
    cursor = connect.cursor()
    try:
        cursor.execute(f'''
            CREATE TABLE {ch_category}
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question VARCHAR(1000),
            answer VARCHAR(1000)
            )
        ''')
    except:
        pass
    connect.close()


def Get_Request(u_category, u_difficulty):
    # Connects To API And If Response Wasn't Successful Stops The Code
    import requests
    import json
    api_type = 'multiple'
    api_category = u_category
    api_difficulty = difficulties_dict[u_difficulty]

    chosen_category = categories_dict[api_category]
    Create_DB(chosen_category)
    api_url = f"https://opentdb.com/api.php?amount=10&category={api_category}&difficulty={api_difficulty}&type={api_type}"
    request = requests.get(api_url)
    if request.status_code != 200:
        print("Couldn't Connect To API")
        return
    request_json = request.text
    res = json.loads(request_json)['results']
    res_structured = json.dumps(res, indent=4)
    Write_Latest_Questions(res_structured)
    Game(res, chosen_category)


def Game(res, ch_category):
    # The Game
    import random
    global score
    global count
    global game_over

    for i in res:
        if game_over:
            Game_Over()
            break
        choices_dict = {}
        current_question = i['question']
        current_question_answer = i['correct_answer']
        inserted_questions = Fetch_From_DB('Questions.db', ch_category)
        Insert_Into_DB('Questions.db', ch_category, current_question_answer, inserted_questions, current_question)
        current_question_choices = [k for k in i['incorrect_answers']]

        current_question_choices.append(current_question_answer)
        for l in range(1, len(current_question_choices) + 1):
            random_choice = random.choice(current_question_choices)
            choices_dict[l] = random_choice
            current_question_choices.remove(random_choice)
        Question_Hud(current_question, choices_dict, current_question_answer)
        count += 1
    if not game_over:
        Game_Over()


def Question_Hud(cr_question, choices, cr_question_answer):
    # Prints Question Hud
    global game_over
    global score
    while True:
        print(f"\n{bcolors.OKBLUE}Question{bcolors.ENDC}: {bcolors.FAIL}{count}{bcolors.ENDC}/"
              f"{bcolors.FAIL}{question_count}{bcolors.ENDC} {bcolors.OKBLUE}Score{bcolors.ENDC}: "
              f"{bcolors.OKCYAN}{score}{bcolors.ENDC}\n{bcolors.OKBLUE}Question{bcolors.ENDC} : "
              f"{bcolors.OKBLUE}{cr_question}{bcolors.ENDC}")
        user_answer = Answer_Choices(choices)
        if user_answer == 0:
            game_over = True
            break
        if user_answer in choices.keys():
            if choices[int(user_answer)] == cr_question_answer:
                score += 1
                print(f'{bcolors.OKGREEN}Correct!{bcolors.ENDC}\n')
            else:
                print(f'{bcolors.FAIL}Incorrect{bcolors.ENDC}\n')
            break
        else:
            print(f'{bcolors.WARNING}{error_message}{bcolors.ENDC}\n')


def Fetch_From_DB(db, ch_category):
    # Fetches Information From Database
    connect = Connect_To_DB(db)
    cursor = connect.cursor()
    command = cursor.execute(f'SELECT question FROM {ch_category}').fetchall()
    connect.close()
    return command


def Insert_Into_DB(db, ch_category, cr_answer, ins_questions, cr_question):
    # Inserts Into Database If The Question Is Not Already In There
    connect = Connect_To_DB(db)
    cursor = connect.cursor()
    if (cr_question,) not in [i for i in ins_questions]:
        cursor.execute(f'INSERT INTO {ch_category} (question, answer) VALUES (?, ?)', (cr_question, cr_answer))
        connect.commit()
    connect.close()


def Answer_Choices(choices):
    # Prints Answer Choices And Prompts User To Select One Of Them
    while True:
        try:
            user_answer = int(input(
                f'{bcolors.FAIL}1{bcolors.ENDC} : {bcolors.OKCYAN}{choices[1]}{bcolors.ENDC}\n'
                f'{bcolors.FAIL}2{bcolors.ENDC} : {bcolors.OKCYAN}{choices[2]}{bcolors.ENDC}\n'
                f'{bcolors.FAIL}3{bcolors.ENDC} : {bcolors.OKCYAN}{choices[3]}{bcolors.ENDC}\n'
                f'{bcolors.FAIL}4{bcolors.ENDC} : {bcolors.OKCYAN}{choices[4]}{bcolors.ENDC}\n'
                f'{bcolors.FAIL}0{bcolors.ENDC} : {bcolors.FAIL}End The Game{bcolors.ENDC}\n'
                f'{bcolors.OKGREEN}Choice{bcolors.ENDC} : '))
            if type(user_answer) is int:
                return user_answer
        except:
            print(f'{bcolors.WARNING}Please Enter A Number{bcolors.WARNING}\n')


def Write_Latest_Questions(json_file):
    # Writes Latest Fetched Questions Into Json File
    file = open('latest_questions.json', 'w')
    file.write(json_file)
    print(f'{bcolors.OKGREEN}Latest Questions Have Been Saved In A Json File!{bcolors.ENDC}')
    file.close()


def Game_Over():
    # Prints Game Over Text
    print(f'{bcolors.FAIL}Game Over!{bcolors.ENDC}\n'
          f'{bcolors.OKGREEN}Final Score{bcolors.ENDC} : {bcolors.OKGREEN}{score}{bcolors.ENDC}')


def Start_game():
    # Starts The Game
    user_category = User_Category()
    user_difficulty = User_Difficulty()
    Get_Request(user_category, user_difficulty)


Start_game()
