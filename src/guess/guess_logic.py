from .users import get_user, create_user, update_new_is_correct_today, increase_attempts_the_day, increase_total_attempts
from .guess_idols import get_idol_guess_for_name

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
            from src.commands.guess import Guess
            hints = []

            hints.append("Você já usou todas as suas tentativas hoje!")
            hints.append(f"O nome do idol era ||{Guess.idol_of_the_day['name']} - {Guess.idol_of_the_day['group']}||!")

            return "\n".join(hints)
    else:
        return "🎉 Você já acertou hoje!"

def check_guess(user_data, idol_tried_name):
    from src.commands.guess import Guess

    hints = []

    user_data = get_user(user_data[0])

    hints.append(f"Você ainda tem {Guess.max_attempts_in_a_day - user_data[4]} tentativas.\n")

    idol_tried = get_idol_guess_for_name(idol_tried_name)

    if not idol_tried:
        hints.append('Idol não encontrado!!')
        return "\n".join(hints)

    print(user_data, idol_tried['name'].lower(), Guess.idol_of_the_day['name'].lower())

    if idol_tried['name'].lower() != Guess.idol_of_the_day['name'].lower():
        if idol_tried["height"] > Guess.idol_of_the_day["height"]:
            hints.append("📏 O idol do dia é mais baixo ❌.")
        elif idol_tried["height"] < Guess.idol_of_the_day["height"]:
            hints.append("📏 O idol do dia é mais alto ❌.")
        else:
            hints.append("📏 O idol do dia tem a mesma altura ✅.")

        if idol_tried["birthYear"] > Guess.idol_of_the_day["birthYear"]:
            hints.append("🎂 O idol do dia é mais velho ❌.")
        elif idol_tried["birthYear"] < Guess.idol_of_the_day["birthYear"]:
            hints.append("🎂 O idol do dia é mais novo ❌.")
        else:
            hints.append("🎂 O idol do dia tem a mesma idade ✅.")

        if idol_tried["nationality"] == Guess.idol_of_the_day["nationality"]:
            hints.append("🌍 O idol do dia é do mesmo país ✅.")
        else:
            hints.append("🌍 O idol do dia é de um país diferente ❌.")

        if idol_tried["group"] == Guess.idol_of_the_day["group"]:
            hints.append("🎤 O idol do dia é do mesmo grupo ✅.")
        else:
            hints.append("🎤 O idol do dia é de outro grupo ❌.")

        if idol_tried["company"] == Guess.idol_of_the_day["company"]:
            hints.append("🏢 O idol do dia é da mesma empresa ✅.")
        else:
            hints.append("🏢 O idol do dia é de outra empresa ❌.")

        return "\n".join(hints)
    else:
        update_new_is_correct_today(user_data)

        return "🎉 Parabéns! Você acertou!!"
        