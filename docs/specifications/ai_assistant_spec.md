# Technical Specification: Islamic AI Assistant
# Техническое Задание: Исламский ИИ-Помощник

## 1. Overview / Обзор
**English:**
Implementation of an AI-powered assistant within the Telegram bot using the DeepSeek API. The module focuses on providing Islamic knowledge in a polite, scholarly persona. It features a rich UI with banner images, quick-reply suggestions, and structured markdown responses.
**Russian:**
Реализация ИИ-помощника внутри Telegram бота с использованием API DeepSeek. Модуль фокусируется на предоставлении исламских знаний от лица вежливого ученого. Особенности: богатый UI с баннерами, кнопки быстрых ответов и структурированные ответы в Markdown.

---

## 2. Configuration / Конфигурация
**Location:** `bot/core/config.py` & `.env`

**Requirements:**
1.  Add `DEEPSEEK_API_KEY` (str) to `Settings`.
2.  Add `DEEPSEEK_BASE_URL` (str, default: `https://api.deepseek.com`).
3.  Add `DEEPSEEK_MODEL` (str, default: `deepseek-chat`).

---

## 3. Architecture components / Компоненты архитектуры

### 3.1 Service Layer / Сервисный слой
**File:** `bot/services/ai_service.py` (New File)

**Class `AIService`:**
* **Methods:**
    * `get_answer(user_question: str) -> str`: Sends request to DeepSeek API.
* **System Prompt (Crucial):**
    * The system prompt must define the persona: "You are a wise, polite Islamic assistant based on Quran and Sunnah..."
    * Instructions for formatting: Use Markdown, bold key points, quote sources in blockquotes (`>`), end with "Allah knows best".
* **Implementation:** Use `aiohttp` (already in dependencies) or `openai` SDK if available.

### 3.2 FSM / Машина состояний
**File:** `bot/states/ai_assistant.py` (New File)

**Class `AIAssistantState`:**
* `waiting_for_question`: Active when user is in the chat loop.

### 3.3 Keyboards / Клавиатуры
**File:** `bot/keyboards/inline/ai_assistant.py` (New File)
* `main_menu_kb`: Buttons [💬 ОБЩЕНИЕ] and [🎨 Создание изображений].
* `chat_actions_kb`: Buttons under AI response: [🔄 New Question], [📤 Share].

**File:** `bot/keyboards/reply/ai_assistant.py` (New File)
* `quick_questions_kb`: Reply buttons for the chat mode (e.g., "📜 Explain Surah Al-Fatiha", "🤲 Dua for today").

---

## 4. UI/UX Flow / Поток Пользователя

### 4.1 Entry Point / Точка входа
* **Trigger:** Button "🤖 Исламский помощник" in Main Menu.
* **Action:**
    * Send a **Banner Image** (URL or local file path to a placeholder image).
    * Caption: Title + Quran Quote ("Allah is with the patient" 2:153) + Description.
    * Inline Keyboard: [💬 Chat], [🎨 Art (Coming Soon)].

### 4.2 Chat Mode / Режим Чата
* **Trigger:** User clicks [💬 Chat].
* **Action:**
    * Set State: `waiting_for_question`.
    * Send text: "Ask me anything..."
    * Show **Reply Keyboard** with quick suggestions.
* **User Input:** Text message.
* **Bot Response:**
    * Send "Typing..." action.
    * Call `AIService`.
    * Reply with structured Markdown text.
    * Attach Inline Keyboard: [🔄 Clear/New] (resets state loop), [📤 Share] (optional).

### 4.3 Image Generation Stub / Заглушка Генерации
* **Trigger:** User clicks [🎨 Art].
* **Action:**
    * Send a "Teaser" image (example of future capability).
    * Caption: "This feature is coming soon. We are preparing the brushes... 🖌️".
    * Answer CallbackQuery (alert=False).

---

## 5. Implementation Steps / Этапы Реализации
1.  **Config:** Update `config.py`.
2.  **Service:** Implement `AIService` with robust prompts.
3.  **States & Keyboards:** Create FSM and Keyboard files.
4.  **Handlers:**
    * Create `bot/handlers/sections/ai_assistant.py`.
    * Implement Main Menu entry, Chat logic, and Image stub.
5.  **Router:** Register new router in `bot/handlers/__init__.py`.
6.  **Assets:** Ensure placeholder images are defined in constants or variables.
