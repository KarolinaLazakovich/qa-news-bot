# QA News Digest Bot

Ежедневный Telegram-дайджест новостей по мобильному тестированию, ИИ в QA и конференциям.

**Расписание:** по будням в 08:00 по Минску (можно изменить в `.github/workflows/daily-digest.yml`).

## Структура дайджеста

- 📱 Мобильное тестирование
- 🤖 ИИ в тестировании
- 🔧 QA & Автоматизация
- 🎓 Конференции и обучение (поиск в интернете через Claude)

---

## Быстрый старт

### 1. Создай Telegram-бота

1. Напиши [@BotFather](https://t.me/BotFather) в Telegram
2. `/newbot` → задай имя и username
3. Сохрани **токен** вида `123456:ABCdef...`

### 2. Узнай свой Chat ID

Отправь боту любое сообщение, затем открой в браузере:
```
https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates
```
В ответе найди `"chat":{"id": 123456789}` — это твой Chat ID.

### 3. Добавь секреты в GitHub

Перейди в Settings → Secrets and variables → Actions и добавь:

| Secret | Значение |
|--------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен от BotFather |
| `TELEGRAM_CHAT_ID` | Твой числовой Chat ID |

### 4. Активируй Actions

Если GitHub Actions неактивен в репо, перейди в вкладку Actions и нажми "I understand my workflows, go ahead and enable them".

---

## Ручной запуск

Перейди в Actions → QA News Digest → Run workflow для немедленного запуска.

---

## Локальный запуск

```bash
cd qa-news-bot
pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="123456:ABCdef..."
export TELEGRAM_CHAT_ID="123456789"

cd bot
python main.py
```

---

## Изменить время отправки

Открой `.github/workflows/daily-digest.yml`, найди строку `cron`:
```yaml
- cron: '0 5 * * 1-5'  # UTC
```

Примеры (Минск = UTC+3):
- 08:00 → `'0 5 * * 1-5'`
- 09:00 → `'0 6 * * 1-5'`
- Каждый день (включая выходные) → `'0 5 * * *'`

---

## Добавить источники

Отредактируй `sources.yaml` — добавь RSS-ленты в нужную категорию:
- `mobile_testing`
- `qa_general`
- `ai_testing`
