LANG_NAMES = {"en": "English 🇬🇧", "ru": "Русский 🇷🇺", "de": "Deutsch 🇩🇪", "fr": "Français 🇫🇷"}
# Тексты сообщений на разных языках
MESSAGES = {
    "welcome": {
        "en": "👋 Hello, {user_name}!\nI am FireFeed - your personal news aggregator.\nUse the menu below to navigate:",
        "ru": "👋 Привет, {user_name}!\nЯ бот FireFeed - твой персональный агрегатор новостей.\nИспользуй меню ниже для навигации:",
        "de": "👋 Hallo, {user_name}!\nIch bin FireFeed - dein persönlicher News-Aggregator.\nVerwende das Menü unten zur Navigation:",
        "fr": "👋 Bonjour, {user_name} !\nJe suis FireFeed - votre agrégateur de nouvelles personnel.\nUtilisez le menu ci-dessous pour naviguer :",
    },
    "menu_settings": {
        "en": "⚙️ Settings",
        "ru": "⚙️ Настройки",
        "de": "⚙️ Einstellungen",
        "fr": "⚙️ Paramètres",
    },
    "menu_help": {"en": "ℹ️ Help", "ru": "ℹ️ Помощь", "de": "ℹ️ Hilfe", "fr": "ℹ️ Aide"},
    "menu_status": {"en": "📊 Status", "ru": "📊 Статус", "de": "📊 Status", "fr": "📊 Statut"},
    "menu_language": {"en": "🌐 Language", "ru": "🌐 Язык", "de": "🌐 Sprache", "fr": "🌐 Langue"},
    "menu_placeholder": {
        "en": "Choose an action...",
        "ru": "Выберите действие...",
        "de": "Wählen Sie eine Aktion...",
        "fr": "Choisissez une action...",
    },
    "settings_loading": {
        "en": "⚙️ Loading settings...",
        "ru": "⚙️ Загружаю настройки...",
        "de": "⚙️ Lade Einstellungen...",
        "fr": "⚙️ Chargement des paramètres...",
    },
    "settings_error": {
        "en": "⚠️ Failed to open settings. Please try again later.",
        "ru": "⚠️ Не удалось открыть настройки. Попробуйте позже.",
        "de": "⚠️ Einstellungen konnten nicht geöffnet werden. Bitte versuchen Sie es später erneut.",
        "fr": "⚠️ Impossible d'ouvrir les paramètres. Veuillez réessayer plus tard.",
    },
    "settings_saved": {
        "en": "✅ Settings saved!",
        "ru": "✅ Настройки сохранены!",
        "de": "✅ Einstellungen gespeichert!",
        "fr": "✅ Paramètres enregistrés !",
    },
    "save_button": {
        "en": "💾 Save",
        "ru": "💾 Сохранить",
        "de": "💾 Speichern",
        "fr": "💾 Enregistrer",
    },
    "settings_title": {
        "en": "⚙️ Choose the categories you are interested in:",
        "ru": "⚙️ Выберите интересующие вас категории:",
        "de": "⚙️ Wählen Sie die Kategorien aus, die Sie interessieren:",
        "fr": "⚙️ Choisissez les catégories qui vous intéressent :",
    },
    "language_select": {
        "en": "🌐 Choose interface language:",
        "ru": "🌐 Выберите язык интерфейса:",
        "de": "🌐 Wählen Sie die Interface-Sprache:",
        "fr": "🌐 Choisissez la langue de l'interface :",
    },
    "language_changed": {
        "en": "✅ Language changed to {language}",
        "ru": "✅ Язык изменен на {language}",
        "de": "✅ Sprache wurde auf {language} geändert",
        "fr": "✅ Langue changée en {language}",
    },
    "help_text": {
        "en": "🤖 <b>FireFeed Bot Help</b>\nI will help you get news according to your subscriptions.\nMain commands:\n⚙️ Settings - configure subscriptions\nℹ️ Help - show this help\n📊 Status - information about your subscriptions\n🌐 Language - change interface language\nAfter setting up subscriptions, you will receive news of selected categories.",
        "ru": "🤖 <b>Справка по боту FireFeed</b>\nЯ помогу вам получать новости по вашим подпискам.\nОсновные команды:\n⚙️ Настройки - настройка подписок\nℹ️ Помощь - показать эту справку\n📊 Статус - информация о ваших подписках\n🌐 Язык - изменить язык интерфейса\nПосле настройки подписок вы будете получать новости выбранных категорий.",
        "de": "🤖 <b>FireFeed Bot Hilfe</b>\nIch werde Ihnen helfen, Nachrichten gemäß Ihren Abonnements zu erhalten.\nHauptbefehle:\n⚙️ Einstellungen - Abonnements konfigurieren\nℹ️ Hilfe - diese Hilfe anzeigen\n📊 Status - Informationen zu Ihren Abonnements\n🌐 Sprache - Interface-Sprache ändern\nNach dem Einrichten von Abonnements erhalten Sie Nachrichten ausgewählter Kategorien.",
        "fr": "🤖 <b>Aide du bot FireFeed</b>\nJe vous aiderai à recevoir des nouvelles selon vos abonnements.\nCommandes principales :\n⚙️ Paramètres - configurer les abonnements\nℹ️ Aide - afficher cette aide\n📊 Statut - informations sur vos abonnements\n🌐 Langue - changer la langue de l'interface\nAprès avoir configuré les abonnements, vous recevrez des nouvelles des catégories sélectionnées.",
    },
    "status_text": {
        "en": "📊 <b>Your current settings:</b>\n🌐 Language: {language}\n📋 Categories: {categories}",
        "ru": "📊 <b>Ваши текущие настройки:</b>\n🌐 Язык: {language}\n📋 Категории: {categories}",
        "de": "📊 <b>Ihre aktuellen Einstellungen:</b>\n🌐 Sprache: {language}\n📋 Kategorien: {categories}",
        "fr": "📊 <b>Vos paramètres actuels :</b>\n🌐 Langue: {language}\n📋 Catégories: {categories}",
    },
    "no_subscriptions": {
        "en": "No subscriptions",
        "ru": "Нет подписок",
        "de": "Keine Abonnements",
        "fr": "Aucun abonnement",
    },
    "bot_active": {
        "en": "Bot is active!",
        "ru": "Бот активен!",
        "de": "Bot ist aktiv!",
        "fr": "Le bot est actif !",
    },
    "button_error": {
        "en": "⚠️ An error occurred. Please try again later.",
        "ru": "⚠️ Произошла ошибка. Попробуйте позже.",
        "de": "⚠️ Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.",
        "fr": "⚠️ Une erreur s'est produite. Veuillez réessayer plus tard.",
    },
}
TRANSLATED_FROM_LABELS = {
    "en": "[AI] Translated from",
    "ru": "[AI] Переведено с",
    "de": "[AI] Übersetzt aus",
    "fr": "[AI] Traduit de",
}
READ_MORE_LABELS = {
    "en": "Read more",
    "ru": "Подробнее",
    "de": "Mehr lesen",
    "fr": "En savoir plus",
}
SOURCE_LABELS = {"en": "Source", "ru": "Источник", "de": "Quelle", "fr": "Source"}
SELECT_CATEGORIES_LABELS = {
    "en": "Choose the categories you are interested in",
    "ru": "Выберите категории, которые вам интересны",
    "de": "Wählen Sie die Kategorien aus, die Sie interessieren",
    "fr": "Choisissez les catégories qui vous intéressent",
}


# Функция для получения сообщения на нужном языке
def get_message(key, lang="en", **kwargs):
    """Возвращает локализованное сообщение"""
    if lang not in MESSAGES.get(key, {}):
        lang = "en"
    message = MESSAGES.get(key, {}).get(lang, "")
    if kwargs:
        message = message.format(**kwargs)
    return message
