from random import randint

from .users import get_user, create_user, update_new_is_correct_today, increase_attempts_the_day, increase_total_attempts, daily_guess_reset
from static.guess_idols import guess_idols_list, idols_dict_list

def get_groups_by_company():
    groups_list = {}

    for idol in guess_idols_list:
        company = idol["company"]
        group = idol["group"]

        if idol['company'] not in groups_list:
            groups_list[company] = set()

        groups_list[company].add(group)
    
    return {company: groups for company, groups in groups_list.items()}

def get_random_idol_id():
    return randint(0, len(guess_idols_list) - 1)

def get_random_idol():
    idol = get_idol_guess_for_id(get_random_idol_id())

    if idol['type'] == 'Boy':
        idol = get_idol_guess_for_id(get_random_idol_id())
    
    print(idol)

    return idol

async def select_idol_guess_for_today():
    from commands.guess import Guess

    Guess.idol_of_the_day = get_random_idol()
    daily_guess_reset()

def get_idol_guess_for_id(id_list):
    idol = guess_idols_list[id_list]

    if idol:
        return idol

def get_idol_guess_for_name(name):
    name = name.lower()
    idol = next((idol for idol_name, idol in idols_dict_list.items() if idol_name.lower() == name), None)
    
    return idol

def user_guess_action(user_id, idol_tried_name):
    user_data = get_user(user_id)

    if not user_data:
        user_data = create_user(user_id)

    if not user_data[5] == 1:
        increase_total_attempts(user_data)

        new_attempts_the_day = increase_attempts_the_day(user_data)

        if new_attempts_the_day:
            return check_guess(user_data, idol_tried_name)
        else:
            from commands.guess import Guess
            
            hints = []

            hints.append("Você já usou todas as suas tentativas hoje!")
            hints.append(f"O nome do idol era ||{Guess.idol_of_the_day['name']} - {Guess.idol_of_the_day['group']}||!")

            return "\n".join(hints)
    else:
        return 1

def check_guess(user_data, idol_tried_name):
    from commands.guess import Guess

    hints = []

    user_data = get_user(user_data[0])

    hints.append(f"Você errou, mas ainda tem **{Guess.max_attempts_in_a_day - user_data[4]} tentativas**.")

    idol_tried = get_idol_guess_for_name(idol_tried_name)

    if not idol_tried:
        hints.append('Idol não encontrado!!')
        return "\n".join(hints)

    print(user_data, idol_tried['name'].lower(), Guess.idol_of_the_day['name'].lower())

    hints.append(f"Tentou **{idol_tried['name']}**, mas o idol do dia é:\n")

    if idol_tried['name'].lower() != Guess.idol_of_the_day['name'].lower():
        if idol_tried['height'] == 0:
            hints.append(f"📏\tIdol ainda sem altura declarada ⚠️")
        elif idol_tried['height'] > Guess.idol_of_the_day['height']:
            hints.append(f"📏\tMais baixo que {idol_tried['height']} cm ❌")
        elif idol_tried['height'] < Guess.idol_of_the_day['height']:
            hints.append(f"📏\tMais alto que {idol_tried['height']} cm ❌")
        else:
            hints.append("📏\tTem a mesma altura ✅")

        if idol_tried['birthYear'] > Guess.idol_of_the_day['birthYear']:
            hints.append(f"🎂\tNasceu antes de {idol_tried['birthYear']} ❌")
        elif idol_tried['birthYear'] < Guess.idol_of_the_day['birthYear']:
            hints.append(f"🎂\tNasceu depois de {idol_tried['birthYear']} ❌")
        else:
            hints.append("🎂\tTem a mesma idade ✅")

        if idol_tried['nationality'] == Guess.idol_of_the_day['nationality']:
            hints.append(f"🌍\tNacionalidade é {idol_tried['nationality']} ✅")
        else:
            hints.append(f"🌍\tNacionalidade não é {idol_tried['nationality']} ❌")

        if idol_tried['group'] == Guess.idol_of_the_day['group']:
            hints.append(f"👥\tÉ do grupo {idol_tried['group']} ✅")
        else:
            hints.append(f"👥\tNão é do grupo {idol_tried['group']} ❌")

        if idol_tried['company'] == Guess.idol_of_the_day['company']:
            hints.append(f"🏢\tÉ da empresa {idol_tried['company']} ✅")
        else:
            hints.append(f"🏢\tNão é da empresa {idol_tried['company']} ❌")

        return "\n".join(hints)
    else:
        update_new_is_correct_today(user_data)

        return 2
        