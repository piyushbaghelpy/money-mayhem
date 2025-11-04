# 🎮 Money Mayhem - Fun Quiz Game

A fun, engaging quiz game built with Streamlit and Groq AI!
I built a fun quiz game using Streamlit and AI that generates unique questions every time. It features a power-up system, loan mechanics, and persistent stats. I integrated Groq's API for AI-generated questions and implemented probability-based game mechanics for consistent gameplay.

## 📁 Project Structure

```
quiz_game/
├── app_final.py          # Main game 
├── utils/
│   ├── __init__.py
│   └── groq_api.py       # AI integration 
├── requirements.txt      # Dependencies
├── .env                  #  API key
└── README.md             # This file
```

## ✨ Features

### Game Modes
- 🎲 **Would You Rather** - Thought-provoking moral dilemmas and fun hypotheticals
- ✨ **Custom Topic** - Generate questions about ANY topic you want

### Core Mechanics
- 💰 Start with $100
- 🎯 Answer 10 questions (4 options each)
- 📊 Best choices = more money, poor choices = lose money
- 🎈 Win with positive money / ❄️ Lose if bankrupt

### Power-Up System (Probability-Based)
- 💰 **Money Boost** (20% chance) - Next question gets 2x money
- ⏭️ **Skip** (15% chance) - Skip any question
- 🛡️ **Shield** (16% chance) - Auto-saves from bankruptcy
- 👿 **Curse** (9% chance) - Adds 2-5 extra questions

### Other Features
- 💳 Loan system (10% interest per question)
- 📈 Multipliers (1.5x, 2x, 2.5x, 3x on some options)
- 🔔 Toast notifications for all important events
- ⬅️ Back button to return to menu
- 📊 Persistent bankruptcy tracking

### **Technologies:**
- **Streamlit** - Python web framework for rapid UI development
- **Groq API** - AI-powered question generation
- **Python** - Backend logic and game mechanics

### **Key Technical Features:**

1. **Session State Management**
   ```python
   st.session_state.money = 100
   st.session_state.power_ups = {"skip": 0, "shield": 0, ...}
   ```

2. **AI Integration**
   ```python
   questions = generate_questions(category, 10, question_type)
   for question in questions:
       random.shuffle(question['options'])
   ```

3. **Probability-Based Power-Ups**
   ```python
   if random.random() < 0.20:  # 20% chance
       st.session_state.power_ups["money_multiplier"] += 1
   ```

4. **Game Logic**
   ```python
   base = option.get('money_change', 0)
   multiplier = option.get('multiplier', 1.0)
   actual = int(base * multiplier * active_multiplier)
   ```



## 📝 Example "Would You Rather" Questions

- "Would you rather know the date of your death or the cause of your death?"
- "Would you rather have the ability to read minds but never turn it off, or teleport but arrive naked?"
- "Would you rather live in a world where everyone can hear your thoughts, or you can hear everyone's?"
- "Would you rather have unlimited money but never eat your favorite food again, or be poor but eat whatever you want?"
- "Would you rather always know when someone is lying or always get away with lying?"

## 🎓 This project demonstrates:
- Web app development with Streamlit
- API integration with external services
- State management in web apps
- Game mechanics and probability
- Clean code architecture
- User experience design