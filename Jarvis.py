
import os
from openai import OpenAI

print("=" * 35)
print("       JARVIS AI")
print("  Assalomu alaykum, aka!")
print("=" * 35)

api_key = os.getenv("OPENAI_API_KEY", "").strip()

if not api_key:
    api_key = input("OpenAI API kalitini kiriting: ").strip()

if not api_key:
    print("API kaliti kiritilmadi.")
    raise SystemExit

client = OpenAI(api_key=api_key)

messages = [
    {
        "role": "system",
        "content": (
            "Sen JARVIS nomli aqlli shaxsiy yordamchisan. "
            "Foydalanuvchiga hurmat bilan aka deb murojaat qil. "
            "Asosan o'zbek tilida javob ber. "
            "Hisob-kitob, texnologiya va kundalik vazifalarda yordam ber."
        )
    }
]

print("\nJARVIS tayyor!")
print("Savol yozing. Chiqish uchun stop deb yozing.")

while True:
    try:
        question = input("\nSiz: ").strip()

        if question.lower() == "stop":
            print("JARVIS: Xayr, aka!")
            break

        if not question:
            continue

        messages.append({
            "role": "user",
            "content": question
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600
        )

        answer = response.choices[0].message.content or ""
        print("\nJARVIS:", answer)

        messages.append({
            "role": "assistant",
            "content": answer
        })

        # Suhbat tarixini me'yorida saqlash
        if len(messages) > 21:
            messages = [messages[0]] + messages[-20:]

    except KeyboardInterrupt:
        print("\nJARVIS: Xayr, aka!")
        break

    except Exception as error:
        print("\nJARVIS xatosi:", error)

        if messages and messages[-1]["role"] == "user":
            messages.pop()
          
