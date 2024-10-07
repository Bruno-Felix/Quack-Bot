import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	print(response.json())
	
output = query({
	"inputs": "srdonabenta: <:BuchinhoCheio:1224805937567629423>bot_da_xiaorina: não sei usar o bot <:Deadge:1156423675239735327>bot_da_xiaorina: uéQuack Bot#7075: srdonabenta: https://open.spotify.com/intl-pt/album/7iidKsHRHGmJ1tAMz8tvZo?si=AuU0BYnuQuKjnEiqKpQNoQQuack Bot#7075: Quack Bot#7075: MALUCA mencionada!!srdonabenta: maluca",
})

@bot.tree.command(name='openia', description='Veja quando o mercado irá fechar')
async def openia(interaction: discord.Interaction):
    await interaction.response.defer()
    
    channel = bot.get_channel(1122561281392644098)
    if channel:
        messages = [message async for message in channel.history(limit=10)]
        
        total_msgs = ''
        for message in messages:
            if not message.author == bot.user:
                total_msgs += f'{message.author}: {message.content}'
        
        print(total_msgs)
    else:
        print("Canal não encontrado.")

    embed = discord.Embed(
        title=f'Mercado da ª rodada',
        color=0xccff66
    )

    embed.set_author(name=interaction.user.name,
                     icon_url=interaction.user.avatar)

    await interaction.followup.send(embed=embed)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    