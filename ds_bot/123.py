import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import gpt4all
import os
from discord.utils import get
import asyncio


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
model = gpt4all.GPT4All("orca-mini-3b-gguf2-q4_0.gguf", allow_download=False)
bot = commands.Bot(command_prefix="!", intents=intents)

MUSIC_FILE = "music/sound.wav"

REACTION_EMOJIS = ['🤑', '🏳️‍🌈', '🧑🏿‍🦲']

secret_role = "oyak"
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

    if os.path.exists(MUSIC_FILE):
        file_size = os.path.getsize(MUSIC_FILE)
        print(f'📁 Файл {MUSIC_FILE} найден ({file_size} байт)')
    else:
        print(f'❌ Файл {MUSIC_FILE} не найден!')
        print('Создайте WAV файл или используйте create_sound()')


@bot.event
async def on_member_join(member):
    try:
        await member.send(f"{member.name}, принеси мне пару тонн БигМаков!🍔🍔🍔")
        print(f"Sent welcome message to {member.name}")
    except:
        print(f"Could not send welcome message to {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    forbidden_words = ["жипатоп", "жиротоп", "жиоптоп","жипотоп"]

    for word in forbidden_words:
        if word in message.content.lower():
            await message.delete()

            await message.channel.send(
                f"{message.author.mention} ❌ женя гандон(я гиндон жип до)",
                delete_after=35
            )
            break

    await bot.process_commands(message)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    import random

    if random.random() < 0.2:
        emoji = random.choice(REACTION_EMOJIS)
        try:
            await message.add_reaction(emoji)
        except:
            pass

    await bot.process_commands(message)

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention}, ти отримав/ла роль {role.mention}!🎭")
    else:
        await ctx.send(f"Спробуйте ще раз пізніше!👺")

@bot.command(name='dm',aliases=['nc','private'])
@commands.has_permissions(manage_messages=True)
async def dm_command(ctx, member: discord.Member, *, message: str):

    try:
        embed = discord.Embed(
            title="📨 Приватне повідомлення",
            description=message,
            color=discord.Color.blue(),
        )

        embed.add_field(name="Відправник", value=f"{ctx.author.display_name}", inline=True)
        embed.add_field(name="Сервер", value=ctx.guild.name, inline=True)
        embed.set_footer(text=f"ID: {ctx.author.id}")

        await member.send(embed=embed)

        await ctx.send(f"✅ Повідомлення відправлено {member.mention}")

    except discord.Forbidden:
        await ctx.send(f"❌ Не можу відправити повідомлення {member.mention}. У них закриті ДМ.")
    except Exception as e:
        await ctx.send(f"❌ Помилка: {str(e)}")


@dm_command.error
async def dm_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас немає дозволу `Manage Messages`!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Використання: `!dm @користувач текст`")

@bot.command(name='hello', aliases=['привіт', 'вітання', 'hi'])
async def hello_command(ctx):
    greetings = [
        f"OЯК, {ctx.author.name}!",
        f"Привіт, {ctx.author.name}!",
        f"Даров, {ctx.author.name}!"
    ]

    import random
    greeting = random.choice(greetings)

    await ctx.send(greeting)

@bot.command(name='true',aliases=['question','false'])
async def true_command(ctx):
    replies=[
        f'Так, {ctx.author.name}, це правда✅',
        f'50/50, {ctx.author.name}😕',
        f'Ні, {ctx.author.name}, неправильно🚫'
    ]
    import random
    reply = random.choice(replies)

    await ctx.send(reply)

@bot.command(name='ai',aliases=['gpt','reply','ask'])
async def reply(ctx, *, question):
    response = model.generate(question, max_tokens=2000)
    await ctx.send(f"{response}")


@bot.command(name='remove', aliases=['видалити', 'removerole'])
@commands.has_permissions(manage_roles=True)
async def remove_command(ctx, role: discord.Role = None):
    try:
        
        if role is None:
            role = discord.utils.get(ctx.guild.roles, name=secret_role)
            if role is None:
                await ctx.send("❌ Роль 'oyak' не знайдена!")
                return

        
        if role not in ctx.author.roles:
            await ctx.send(f"❌ У вас немає ролі {role.mention}!")
            return

        # Видаляємо роль
        await ctx.author.remove_roles(role)

        await ctx.send(f"✅ Роль {role.mention} успішно видалено!")

    except discord.Forbidden:
        await ctx.send("❌ У мене немає дозволу керувати ролями!")
    except Exception as e:
        await ctx.send(f"❌ Помилка: {str(e)}")


@remove_command.error
async def remove_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас немає дозволу `Manage Roles`!")


@bot.command(name='commands', aliases=['команди', 'допомога'])
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 Доступні команди",
        description="Префікс команд: `!`",
        color=discord.Color.brand_red()
    )

    embed.add_field(
        name="👤 Ролі",
        value="• `!assign` - отримати роль oyak\n• `!remove [роль]` - видалити роль\n• `!remove` - видалити роль oyak",
        inline=False
    )

    embed.add_field(
        name="💬 Повідомлення",
        value="• `!dm @користувач текст` - відправити в ДМ\n• `!hello` - привітатися",
        inline=False
    )

    embed.add_field(
        name="🤖 AI",
        value="• `!ai [питання]` - запитати у AI",
        inline=False
    )

    embed.add_field(
        name="🎶Голосовий канал та музика🔊",
        value="• `!play` - програти базовану пісню про Женю\n•`!stop `- зупинити пісню\n•`!join` - просто приєднатись\n•`!leave` - від'єднатись від голосового каналу",
        inline=False
    )

    embed.add_field(
        name="ℹ️ Інше",
        value="• `!commads` - цей список команд\n•Автомодерація: видаляє слова з 'жипатоп'\n•`!true(!false)` - скаже так або ні",
        inline=False
    )

    embed.set_footer(text=f"Запит від {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f'Я приєднався до {channel}, чумаки!🥳')

# сделал прост контрл ц контрл в
@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f"Я від'єднався від {channel}, чумаки😓")


@bot.command()
async def play(ctx):
    """🎵 Проиграть WAV файл"""

    if not ctx.author.voice:
        await ctx.send("🔊 **Зайди в голосовой канал!**")
        return

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client:
        if ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)
        voice = ctx.voice_client
    else:
        try:
            voice = await voice_channel.connect()
            await ctx.send(f"✅ **Подключился к {voice_channel.name}**")
        except Exception as e:
            await ctx.send(f"❌ **Ошибка подключения:** {e}")
            return

    if not os.path.exists(MUSIC_FILE):
        await ctx.send(f"❌ **Файл {MUSIC_FILE} не найден!**")
        return

    if voice.is_playing():
        voice.stop()
        await asyncio.sleep(0.5)

    try:
        await ctx.send("🎶 **Запускаю базовану музичку...**")

        with open(MUSIC_FILE, 'rb') as f:
            audio_data = f.read()

        source = discord.PCMAudio(audio_data)
        voice.play(source)

        await asyncio.sleep(1)

        if voice.is_playing():
            await ctx.send("✅ **Музыка играет!** 🎵")
        else:
            await ctx.send("⚠️ **Пробую другой метод...**")
            await try_wav_method(ctx, voice)

    except Exception as e:
        await ctx.send(f"❌ **Ошибка:** {e}")
        await try_wav_method(ctx, voice)


async def try_wav_method(ctx, voice):
    try:
        import wave

        with wave.open(MUSIC_FILE, 'rb') as wav:
            frames = wav.readframes(wav.getnframes())

            # Создаем AudioSource
            class WAVSource(discord.AudioSource):
                def __init__(self, data):
                    self.data = data
                    self.pos = 0

                def read(self):
                    chunk_size = 3840  # 20ms
                    if self.pos >= len(self.data):
                        return b''
                    chunk = self.data[self.pos:self.pos + chunk_size]
                    self.pos += chunk_size
                    return chunk

            source = WAVSource(frames)
            voice.play(source)

            await asyncio.sleep(1)

            if voice.is_playing():
                await ctx.send("✅ **Воспроизведение работает!**")
            else:
                await ctx.send("❌ **Не удалось воспроизвести**")

    except Exception as e:
        await ctx.send(f"❌ **Ошибка WAV метода:** {e}")


@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ **Остановлено**")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)
