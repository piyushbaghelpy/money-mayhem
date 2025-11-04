import streamlit as st
import random
import time
from dotenv import load_dotenv
from utils.groq_api import generate_questions

load_dotenv()


st.set_page_config(page_title="Money Mayhem - Fun Quiz Game", layout="wide")

# Initialize game
def init_game(category, question_type="financial"):
    """Start new game"""
    # Force clear all old game data to prevent repetition
    keys_to_clear = ['questions', 'current_question_index', 'money', 'loan_taken', 
                     'loan_amount', 'power_ups', 'next_question_multiplier']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.game_started = True
    st.session_state.money = 100
    st.session_state.current_question_index = 0
    st.session_state.total_questions = 10
    st.session_state.loan_taken = False
    st.session_state.loan_amount = 0
    st.session_state.game_over = False
    st.session_state.questions_answered = 0
    st.session_state.category = category
    st.session_state.question_type = question_type
    
    # Power-ups
    st.session_state.power_ups = {
        "money_multiplier": 0,
        "skip_question": 0,
        "bankrupt_shield": 0,
        "curse": 0
    }
    st.session_state.next_question_multiplier = 1.0
    
    st.session_state.show_feedback = False
    st.session_state.feedback_message = ""
    st.session_state.feedback_type = "info"
    st.session_state.feedback_time = 0
    
    # Generate questions (more than 10 to handle curses)
    try:
        with st.spinner(f"🤖 Generating {question_type} quiz questions..."):
            questions = generate_questions(category, 20, question_type)  # this generate 20 for curse buffer
            # Randomize options
            for question in questions:
                random.shuffle(question['options'])
            st.session_state.questions = questions
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check your GROQ_API_KEY in .env file")
        st.session_state.game_started = False

def reset_to_landing():
    """Go back to landing page without resetting bankruptcy count"""
    bankruptcy = st.session_state.get('total_bankruptcies', 0)
    # Clear everything including questions to prevent repetition
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.total_bankruptcies = bankruptcy
    st.session_state.game_started = False
    st.session_state.bankruptcy_counted = False

# Initialize total bankruptcies tracker
if "total_bankruptcies" not in st.session_state:
    st.session_state.total_bankruptcies = 0

if "game_started" not in st.session_state:
    st.session_state.game_started = False

# LANDING PAGE
if not st.session_state.game_started:
    st.title("🎮 Money Mayhem - Fun Quiz Game")
    st.markdown("### Welcome! Test your decision-making skills in this fun quiz game!")
    st.write("Answer 10 questions, collect power-ups, and try to get the highest score!")
    
    if st.session_state.total_bankruptcies > 0:
        st.info(f"📊 Total Bankruptcies: {st.session_state.total_bankruptcies}")
    
    st.markdown("---")
    st.subheader("🎯 Choose Your Quiz Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎲 Would You Rather")
        st.write("Fun hypothetical scenarios and tough choices!")
        if st.button("Start Would You Rather", use_container_width=True, key="wyr"):
            
            if 'questions' in st.session_state:
                del st.session_state['questions']
            init_game("fun hypothetical scenarios and would you rather questions", "would_you_rather")
            st.rerun()
    
    with col2:
        st.markdown("### ✨ Custom Topic")
        custom_category = st.text_input("Enter any topic (e.g., 'superheroes', 'space exploration', 'harry potter')")
        if st.button("Start Custom Quiz", use_container_width=True, key="custom") and custom_category:
            # Clear any cached questions before starting
            if 'questions' in st.session_state:
                del st.session_state['questions']
            init_game(custom_category, "custom")
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    **🎮 How to Play:**
    - Start with $100
    - Answer 10 questions (4 options each)
    - Best choices = more money 💰
    - Poor choices = lose money ❌
    - Collect power-ups: 💰 Boost, ⏭️ Skip, 🛡️ Shield
    - Avoid 👿 Curses (add extra questions!)
    - Take loans if needed (10% interest/question)
    - Win by having money at the end!
    """)

# MAIN GAME
else:
    st.title("🎮 Money Mayhem Quiz")
    
    # Create layout: Left sidebar for power-ups, main area for game
    left_sidebar = st.sidebar
    
    with left_sidebar:
        st.markdown("## 💰 Your Status")
        
        # Money display (large) - show both money and loan
        net_money = st.session_state.money - st.session_state.loan_amount
        
        st.metric("💵 Current Money", f"${st.session_state.money}")
        if st.session_state.loan_taken:
            st.metric("💳 Loan Debt", f"-${st.session_state.loan_amount}", delta="Debt")
            if net_money >= 0:
                st.metric("📊 Net Total", f"${net_money}", delta="Positive")
            else:
                st.metric("📊 Net Total", f"${net_money}", delta="Negative", delta_color="inverse")
        else:
            st.metric("📊 Net Total", f"${net_money}")
        
        st.markdown("---")
        
        # Power-ups
        st.markdown("### 🎁 Power-Ups")
        
        # Money Multiplier (show if next question will have boost)
        if st.session_state.next_question_multiplier > 1.0:
            st.success(f"💰 Money Boost: Active")
            st.caption("Next question gets 2x money!")
        else:
            st.info("💰 Money Boost: 0")
        
        # Skip
        if st.session_state.power_ups["skip_question"] > 0:
            st.success(f"⏭️ Skip: {st.session_state.power_ups['skip_question']}")
        else:
            st.info("⏭️ Skip: 0")
        
        # Shield
        if st.session_state.power_ups["bankrupt_shield"] > 0:
            st.success(f"🛡️ Shield: {st.session_state.power_ups['bankrupt_shield']}")
            st.caption("Sets negative money to $0")
        else:
            st.info("🛡️ Shield: 0")
        
        # Curse
        if st.session_state.power_ups["curse"] > 0:
            st.warning(f"👿 Curse: {st.session_state.power_ups['curse']}")
            st.caption(f"+{st.session_state.power_ups['curse']} extra questions")
        
        st.markdown("---")
        
        # Loan info
        if st.session_state.loan_taken:
            st.error(f"💳 Loan: ${st.session_state.loan_amount}")
            st.caption("10% interest per question")
            
            # Repayment
            if st.session_state.money > 0:
                repay = st.number_input("Repay amount", 0, min(st.session_state.money, st.session_state.loan_amount), 0, 10)
                if st.button("💵 Repay Loan") and repay > 0:
                    st.session_state.money -= repay
                    st.session_state.loan_amount -= repay
                    if st.session_state.loan_amount <= 0:
                        st.session_state.loan_taken = False
                        st.session_state.loan_amount = 0
                        st.toast("🎉 Loan fully repaid!", icon="✅")
                    else:
                        st.toast(f"Repaid ${repay}", icon="💵")
                    st.rerun()
        else:
            questions_left = st.session_state.total_questions - st.session_state.current_question_index
            if net_money < 0 and questions_left >= 2:
                st.warning("💸 Need money?")
                st.toast("⚠️ You're running out of money! Consider taking a loan.", icon="💳")
                loan_amt = st.number_input("Loan amount", 10, 500, 100, 10)
                if st.button("💳 Take Loan"):
                    st.session_state.money += loan_amt
                    st.session_state.loan_amount = loan_amt
                    st.session_state.loan_taken = True
                    st.toast(f"Loan approved: ${loan_amt}", icon="✅")
                    st.rerun()
            elif net_money < 0 and questions_left < 2:
                st.error("⚠️ Cannot take loan!")
                st.caption("Need at least 2 questions remaining")
        
        st.markdown("---")
        
        # Back button
        if st.button("⬅️ Back to Menu", use_container_width=True):
            reset_to_landing()
            st.rerun()
    
    # Main game area
    st.markdown("---")
    
    # Progress
    progress = min(st.session_state.current_question_index, st.session_state.total_questions) / st.session_state.total_questions
    st.progress(progress, text=f"Progress: {st.session_state.current_question_index}/{st.session_state.total_questions}")
    
    st.markdown("---")
    
    # GAME OVER
    if st.session_state.game_over or st.session_state.current_question_index >= st.session_state.total_questions:
        final_net = st.session_state.money - st.session_state.loan_amount
        
        # Check if already counted bankruptcy
        if not st.session_state.get('bankruptcy_counted', False):
            if st.session_state.game_over or final_net < 0:
                st.session_state.total_bankruptcies += 1
                st.session_state.bankruptcy_counted = True
        
        # Loan warning if unpaid
        if st.session_state.loan_taken and st.session_state.loan_amount > 0:
            st.warning(f"⚠️ Unpaid Loan: ${st.session_state.loan_amount}")
        
        # Win/Loss determination
        if st.session_state.game_over or final_net < 0:
            st.error("💔 Game Over - You Lost!")
            st.snow()
        else:
            st.success("🎉 Congratulations - You Win!")
            st.balloons()
        
        st.markdown("### 📊 Final Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Money Earned", f"${st.session_state.money}")
            if st.session_state.loan_taken:
                st.metric("Loan Debt", f"-${st.session_state.loan_amount}")
            st.metric("Net Total", f"${final_net}", delta="Win" if final_net >= 0 else "Loss")
        with col2:
            st.metric("Questions Answered", st.session_state.questions_answered)
        with col3:
            st.metric("Total Bankruptcies", st.session_state.total_bankruptcies)
        
        if st.button("🔄 Play Again", use_container_width=True):
            reset_to_landing()
            st.rerun()
    
    # ACTIVE QUESTION
    else:
        if st.session_state.current_question_index < len(st.session_state.questions):
            current_q = st.session_state.questions[st.session_state.current_question_index]
            
            st.markdown(f"### ❓ {current_q['question']}")
            
            # Active multiplier warning
            if st.session_state.next_question_multiplier > 1.0:
                st.warning(f"🔥 MONEY BOOST ACTIVE: This question gets {st.session_state.next_question_multiplier}x money!")
            
            st.write("")
            
            # Skip button
            if st.session_state.power_ups["skip_question"] > 0:
                if st.button("⏭️ Use Skip (Skip this question)", type="secondary"):
                    st.session_state.power_ups["skip_question"] -= 1
                    st.session_state.current_question_index += 1
                    st.info("⏭️ Question skipped!")
                    st.toast("Question skipped!", icon="⏭️")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
            
            # 4 Options
            col1, col2 = st.columns(2)
            for idx, option in enumerate(current_q['options']):
                with col1 if idx % 2 == 0 else col2:
                    if st.button(option['text'], key=f"opt_{idx}", use_container_width=True):
                        # Calculate money
                        base = option.get('money_change', 0)
                        mult = option.get('multiplier', 1.0)
                        active_mult = st.session_state.next_question_multiplier
                        total_mult = mult * active_mult
                        actual = int(base * total_mult)
                        
                        st.session_state.money += actual
                        st.session_state.questions_answered += 1
                        
                        # Show feedback
                        # Money change box with multiplier info
                        if actual > 0:
                            if total_mult != 1.0:
                                st.success(f"🎉 Congrats! You got {total_mult}x multiplier on this question! +${actual}")
                            else:
                                st.success(f"✅ +${actual}")
                        elif actual < 0:
                            if total_mult != 1.0:
                                st.error(f"⚠️ {total_mult}x multiplier applied! ${actual}")
                            else:
                                st.error(f"❌ ${actual}")
                        
                        # Loan interest
                        if st.session_state.loan_taken:
                            interest = int(st.session_state.loan_amount * 0.10)
                            st.session_state.loan_amount += interest
                            st.warning(f"💳 Loan interest: +${interest}")
                        
                        # Reset multiplier
                        st.session_state.next_question_multiplier = 1.0
                        
                        # Probability-based power-ups (independent of API)
                        # Only give money boost if not already active
                        if random.random() < 0.09 and st.session_state.next_question_multiplier == 1.0:
                            st.session_state.next_question_multiplier = 2.0
                            st.success("🎁 POWER-UP: Money Multiplier! Next question gets 2x money!")
                            st.toast("💰 Money Boost Collected!", icon="🎉")
                        
                        
                        if random.random() < 0.08:
                            st.session_state.power_ups["skip_question"] += 1
                            st.success("🎁 POWER-UP: Got Skip token!")
                            st.toast("⏭️ Skip Token Acquired!", icon="⭐")
                        
                        # Shield: ~5% chance (max 1 per game) - Very rare!
                        if random.random() < 0.05 and st.session_state.power_ups["bankrupt_shield"] == 0:
                            st.session_state.power_ups["bankrupt_shield"] = 1
                            # Don't show success box immediately, only in sidebar
                            st.toast("🛡️ Rare Shield Acquired! Check sidebar!", icon="🔥")
                        
                       
                        if random.random() < 0.02:
                            curse_amt = random.choice([2, 3])
                            st.session_state.power_ups["curse"] += 1
                            st.session_state.total_questions += curse_amt
                            st.error(f"👿 CURSE: +{curse_amt} extra questions added!")
                            st.toast("👿 Cursed!", icon="⚠️")
                        
                        # Check bankruptcy
                        net = st.session_state.money - st.session_state.loan_amount
                        left = st.session_state.total_questions - (st.session_state.current_question_index + 1)
                        
                        if net < 0 and st.session_state.power_ups["bankrupt_shield"] > 0:
                            st.session_state.power_ups["bankrupt_shield"] -= 1
                            
                            amount_needed = abs(net)
                            st.session_state.money += amount_needed
                            st.success(f"🛡️ SHIELD USED! Protected from negative money. Money set to $0")
                            st.toast("🛡️ Shield activated! Net money set to $0", icon="🔥")
                            net = st.session_state.money - st.session_state.loan_amount
                        
                        if net < 0 and left == 0:
                            st.session_state.game_over = True
                            st.error("🚨 BANKRUPTCY!")
                        
                        st.session_state.current_question_index += 1
                        
                        time.sleep(4) 
                        st.rerun()
        else:
            st.error("No more questions available")
