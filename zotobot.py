# zoto_bot.py

import logging
from telegram import Update, ReplyKeyboardMarkup # Ajout de ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random

# 1. Configuration du Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Définition du Token
TOKEN = "7646946178:AAETp1SU29Mz3g-cy2dD508A6IN0QiIbiv0"

# 3. Structure des Données (questions_by_level)
questions_by_level = {
    "mg": {  # Langue malgache
        "zazavao": [
            {
                "question": "Telo ireo fahalalana fototra...",
                "answer": "Fahafantarana ny tompo sy ny mpaminany ary ny finoana",
                "encouragements": ["Tohizo fa tsara"],
                "feedbackWrong": "Fahafantarana ny tompo..."
            },
            # ... autres questions pour 'zazavao'
        ],
        "antonony": [
            {
                "question": "Ny «LA ILAHA ILLALLAH » dia midika hoe...",
                "answer": "Tsy misy andriamanitra afa-tsy Allah.",
                "encouragements": ["Tohizo fa tsara."],
                "feedbackWrong": "Tsy misy andriamanitra afa-tsy Allah."
            },
            # ... autres questions pour 'antonony'
        ],
        "henjana": [
            {
                "question": "Ny ibada (na fanompoana) dia fomba...",
                "answer": "Eny",
                "encouragements": ["Tehaka ren-tany aman-danitra ho anao..."],
                "feedbackWrong": "Eny, ibada ny fanajana ray aman-dreny..."
            },
            # ... autres questions pour 'henjana'
        ]
    },
    "ar": {  # Langue arabe
        "zazavao": [
            {
                "question": "هناك ثلاثة أصول يجب على المسلم معرفتها، وهي: معرفة العبد ربه...",
                "answer": "معرفة العبد ربه ومعرفة نبيه ومعرفة دينه",
                "encouragements": ["أحسنت"],
                "feedbackWrong": "معرفة العبد ربه ومعرفة نبيه ومعرفة دينه"
            },
            # ... autres questions pour 'zazavao' en arabe
        ],
        "antonony": [
            {
                "question": "معنى كلمة (لا إله إلا الله) هو أنَّ لا معبود بحق سوى الله...",
                "answer": "لا معبود بحق سوى",
                "encouragements": ["ممتاز"],
                "feedbackWrong": "هداك الله ! معنى كلمة (لا إله إلا الله) هو أنَّ لا معبود بحق سوى الله"
            },
        ],
        "henjana":[
            {
                "question": "العبادة هي اسم جامع لكل ما يحبه الله ويرضاه من الأقوال والأفعال الظاهرة والباطنة...",
                "answer": "نعم",
                "encouragements": ["ممتاز . نعم، بر الوالدين يعد من العبادات لأن الله يحبه وأمر به"],
                "feedbackWrong": "نعم، بر الوالدين يعد من العبادات لأن الله يحبه وأمر به"
            },
        ]

    }
}

# 4. État du Jeu par Utilisateur
user_states = {}  # user_id: {"language": "mg", "level": "zazavao", "question_index": 0}

# 5. Fonctions de Gestion des Commandes
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text("Assalamou anlaykoum! Bienvenue sur Zoto Bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays available commands."""
    help_text = "Available commands:\n/start - Start the bot."
    await update.message.reply_text(help_text)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the language for the user."""
    user_id = update.effective_user.id
    language = update.message.text[1:]

    if language not in ["mg", "ar"]:
        await update.message.reply_text("Tsy mazava ilay izy. Fiteny malagasy sa arabo  ? |  لغة ملاغاشية أم عربية ؟")
        return

    keyboard = [["/zazavao", "/antonony", "/henjana"]] # Clavier personnalisé
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    user_states[user_id] = {"language": language, "level": None, "question_index": 0}

    if language == "mg":
        await update.message.reply_text("Nisafidy fiteny malagasy ianao !  Aiza amin'ireto sokajy telo ireto indray àry no misy anao :", reply_markup=reply_markup)
    elif language == "ar":
        await update.message.reply_text("لقد اخترت اللغة العربية!  اختر مستواك:", reply_markup=reply_markup)

async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets the level for the user."""
    user_id = update.effective_user.id
    level = update.message.text[1:]

    if user_id not in user_states or user_states[user_id]["language"] is None:
        await update.message.reply_text("Voalohany, mila misafidy fiteny aloha ianao.")
        return

    language = user_states[user_id]["language"]

    if level not in ["zazavao", "antonony", "henjana"]:
        await update.message.reply_text("Tsy mazava ilay izy.  'zazavao' sa 'antonony' sa 'henjana'  ?")
        return

    user_states[user_id]["level"] = level
    user_states[user_id]["question_index"] = 0

    if language == "mg":
        await update.message.reply_text(f"Okay, lesona ho an'ireo {level} no atao !")
    elif language == "ar":
        await update.message.reply_text(f"حسنًا، سنبدأ دروس {level}!")

    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the current question to the user."""
    user_id = update.effective_user.id
    language = user_states[user_id]["language"]
    level = user_states[user_id]["level"]
    question_index = user_states[user_id]["question_index"]

    questions = questions_by_level[language][level]
    if question_index < len(questions):
        question_text = questions[question_index]["question"]
        await update.message.reply_text(question_text)
    else:
        await update.message.reply_text(
            "Tapitra ny lesona ! Allah anie hampitombo ny fahalalako sy ny fahalalanao 🤲.  انتهت الدروس! زادني الله وإياك علمًا 🤲"
        )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the user's answer to the current question."""
    user_id = update.effective_user.id

    if user_id not in user_states or user_states[user_id]["language"] is None or user_states[user_id]["level"] is None:
        await update.message.reply_text("Mila manomboka amin'ny /start aloha ianao  الرجاء البدء بـ /start أولاً.")
        return

    language = user_states[user_id]["language"]
    level = user_states[user_id]["level"]
    question_index = user_states[user_id]["question_index"]
    user_answer = update.message.text.lower()

    questions = questions_by_level[language][level]
    if question_index < len(questions):
        correct_answer = questions[question_index]["answer"].lower()

        if user_answer == correct_answer:
            encouragement = random.choice(questions[question_index]["encouragements"])
            await update.message.reply_text(encouragement)
            user_states[user_id]["question_index"] += 1
            await send_question(update, context)
        else:
            feedback_wrong = questions[question_index]["feedbackWrong"]
            await update.message.reply_text(f"Diso ☹️. {feedback_wrong}  خطأ 😕. {feedback_wrong}")
            user_states[user_id]["question_index"] += 1
            await send_question(update, context)
        # Gestion fin de série de question
    else:
        await update.message.reply_text(
            "Tapitra ny lesona ! Allah anie hampitombo ny fahalalako sy ny fahalalanao 🤲.  انتهت الدروس! زادني الله وإياك علمًا 🤲"
        )

# 6. Fonction principale (main) et handlers
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mg", set_language))
    application.add_handler(CommandHandler("ar", set_language))
    application.add_handler(CommandHandler("zazavao", set_level))
    application.add_handler(CommandHandler("antonony", set_level))
    application.add_handler(CommandHandler("henjana", set_level))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    application.run_polling()

if __name__ == '__main__':
    main()
