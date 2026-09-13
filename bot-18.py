import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ==============================
# SOZLAMALAR
# ==============================
BOT_TOKEN = "8914759604:AAGwNjkU6HpfnkGfjKwZ4oAJqEmw2GYzcxM"
ADMIN_ID = 6033308194

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ==============================
# DUSEL LED LAMPALAR
# ==============================
PRODUCTS = [
    ("Dusel LED 5W", 0.55),
    ("Dusel LED 7W", 0.65),
    ("Dusel LED 10W", 0.70),
    ("Dusel LED 12W", 0.80),
    ("Dusel LED 15W", 0.95),
    ("Dusel LED 18W", 1.10),
    ("Dusel LED 20W", 1.30),
    ("Dusel LED 30W", 2.10),
    ("Dusel LED 40W", 2.90),
    ("Dusel LED 50W", 3.70),
    ("Dusel LED 60W", 4.30),
    ("Dusel LED 80W", 6.00),
    ("Dusel LED 100W", 8.00),
    ("Dusel LED 150W", 11.00),
    ("Dusel LED 200W", 19.00),
    ("Dusel LED Flame Lamp", 1.90),
    ("Dusel LED C30/E14 5W", 0.60),
    ("Dusel LED C30/E27 5W", 0.60),
    ("Dusel LED C35/E14 7W", 0.65),
    ("Dusel LED C35/E27 7W", 0.65),
    ("Dusel LED C40/E14 9W", 0.70),
    ("Dusel LED C40/E27 9W", 0.70),
    ("Dusel LED G45/E14 5W", 0.65),
    ("Dusel LED B45/E27 5W", 0.65),
]

class RegistrationState(StatesGroup):
    name = State()
    phone = State()

class OrderState(StatesGroup):
    quantity = State()
    name = State()
    phone = State()
    address = State()

carts = {}
selected = {}
users = {}

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Zakaz berish", callback_data="products")],
        [InlineKeyboardButton(text="📋 Savatcha", callback_data="cart")]
    ])

def product_menu():
    rows = []
    for i, (name, price) in enumerate(PRODUCTS):
        rows.append([InlineKeyboardButton(
            text=f"{name} — ${price:.2f}",
            callback_data=f"p:{i}"
        )])
    rows.append([InlineKeyboardButton(text="🛒 Savatcha", callback_data="cart")])
    rows.append([InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in users:
        await state.set_state(RegistrationState.name)
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "🛍 DUSEL 12-DOKON buyurtma botiga xush kelibsiz!\n\n"
            "Bu bot orqali DUSEL mahsulotlarini ko‘rib, zakaz berishingiz mumkin.\n\n"
            "📋 Avval qisqa registratsiyadan o‘tamiz.\n"
            "👤 Ism va familiyangizni yozing:"
        )
        return

    await message.answer(
        "💡 DUSEL 12-DOKON\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=main_menu()
    )

@dp.message(RegistrationState.name)
async def registration_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(RegistrationState.phone)
    await message.answer("📞 Telefon raqamingizni yozing:\nMasalan: +998901234567")

@dp.message(RegistrationState.phone)
async def registration_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    users[user_id] = {
        "name": data["name"],
        "phone": message.text.strip()
    }
    await state.clear()
    await message.answer(
        "✅ Ro‘yxatdan o‘tish tugadi!\n\n"
        "Endi mahsulot tanlab zakaz berishingiz mumkin.",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    await callback.message.edit_text(
        "💡 DUSEL 12-DOKON\n\nKerakli bo‘limni tanlang:",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "products")
async def products(callback: CallbackQuery):
    await callback.message.edit_text(
        "💡 DUSEL LED LAMPALAR\n\nMahsulotni tanlang:",
        reply_markup=product_menu()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("p:"))
async def choose_product(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split(":")[1])
    name, price = PRODUCTS[index]

    selected[callback.from_user.id] = (name, price)
    await state.set_state(OrderState.quantity)

    await callback.message.answer(
        f"💡 {name}\n"
        f"💵 Narxi: ${price:.2f}\n\n"
        "Nechta kerak? Masalan: 5"
    )
    await callback.answer()

@dp.message(OrderState.quantity)
async def quantity(message: Message, state: FSMContext):
    try:
        qty = int(message.text.strip())
        if qty <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❗ Faqat musbat son yozing. Masalan: 5")
        return

    user_id = message.from_user.id
    product = selected.get(user_id)

    if not product:
        await state.clear()
        await message.answer("Mahsulot topilmadi. /start ni bosing.")
        return

    name, price = product
    carts.setdefault(user_id, []).append({
        "name": name,
        "price": price,
        "qty": qty
    })

    await state.clear()

    await message.answer(
        f"✅ Savatchaga qo‘shildi!\n\n"
        f"💡 {name}\n"
        f"🔢 {qty} dona\n"
        f"💵 ${price * qty:.2f}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana mahsulot", callback_data="products")],
            [InlineKeyboardButton(text="🛒 Savatchani ko‘rish", callback_data="cart")]
        ])
    )

@dp.callback_query(F.data == "cart")
async def cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    items = carts.get(user_id, [])

    if not items:
        await callback.answer("🛒 Savatcha bo‘sh.", show_alert=True)
        return

    text = "🛒 SIZNING ZAKAZINGIZ\n\n"
    total = 0

    for item in items:
        subtotal = item["price"] * item["qty"]
        total += subtotal
        text += (
            f"💡 {item['name']}\n"
            f"   {item['qty']} dona × ${item['price']:.2f} = ${subtotal:.2f}\n\n"
        )

    text += f"━━━━━━━━━━━━\n💰 JAMI: ${total:.2f}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Zakazni yuborish", callback_data="checkout")],
        [InlineKeyboardButton(text="➕ Yana mahsulot", callback_data="products")],
        [InlineKeyboardButton(text="🗑 Tozalash", callback_data="clear")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "clear")
async def clear(callback: CallbackQuery):
    carts.pop(callback.from_user.id, None)
    await callback.message.edit_text(
        "🗑 Savatcha tozalandi.",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    if not carts.get(callback.from_user.id):
        await callback.answer("Savatcha bo‘sh.", show_alert=True)
        return

    await state.set_state(OrderState.name)
    await callback.message.answer("👤 Ismingizni yozing:")
    await callback.answer()

@dp.message(OrderState.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(OrderState.phone)
    await message.answer(
        "📞 Telefon raqamingizni yozing:\n"
        "Masalan: +998901234567"
    )

@dp.message(OrderState.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(OrderState.address)
    await message.answer("📍 Yetkazib berish manzilini yozing:")

@dp.message(OrderState.address)
async def get_address(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(address=message.text.strip())
    data = await state.get_data()

    items = carts.get(user_id, [])
    total = 0
    text = "🆕 YANGI ZAKAZ!\n\n"

    for item in items:
        subtotal = item["price"] * item["qty"]
        total += subtotal
        text += (
            f"💡 {item['name']}\n"
            f"🔢 {item['qty']} dona\n"
            f"💵 ${subtotal:.2f}\n\n"
        )

    text += (
        "━━━━━━━━━━━━\n"
        f"💰 JAMI: ${total:.2f}\n\n"
        f"👤 Mijoz: {data['name']}\n"
        f"📞 Telefon: {data['phone']}\n"
        f"📍 Manzil: {data['address']}\n"
        f"🆔 Telegram ID: {user_id}"
    )

    await bot.send_message(ADMIN_ID, text)

    carts.pop(user_id, None)
    selected.pop(user_id, None)
    await state.clear()

    await message.answer(
        "✅ Zakazingiz qabul qilindi!\n\n"
        "Tez orada siz bilan bog‘lanamiz. Rahmat! 🙏",
        reply_markup=main_menu()
    )

async def main():
    print("🤖 DUSEL 12-DOKON bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
