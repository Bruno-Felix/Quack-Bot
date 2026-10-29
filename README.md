# Quack Bot

### Funcionalidades
- **/hoje**: Comando de listagem das lançamentos de kpop do dia;
- **/semana**: Comando de listagem das lançamentos de kpop da semana;
- **!fifa**: Comando para chamada do pessoal para jogar FIFA;
- **Links sociais**: links crus de X/Twitter, Instagram e TikTok são sanitizados e
  reenviados com embeds aprimorados, alternância de domínio e controles privados.
  Os domínios e alternativas podem ser editados em
  [`src/data/social_links.json`](src/data/social_links.json). Cada entrada aceita
  `source_domains`, `standard`, `alternatives` e `raw_alternatives`, permitindo
  adicionar novos serviços sem alterar o código. Os links corrigidos são enviados
  no formato `[quack!](link_do_video)` e têm os parâmetros de rastreamento
  removidos. Mensagens contendo vários links são processadas integralmente, com
  uma correção independente para cada link;
- **Mencionada**:
   - Medica;
   - Maluca;
   - Quack. 

### Como rodar

#### Instalar dependencias
```
pip install -r requirements.txt
```

#### Rodar o Bot
Para isso é necessário criar um App para teste:
[criar_e_rodar_bot_discord.pdf](https://github.com/user-attachments/files/17167829/criar_e_rodar_bot_discord.pdf)

```
python main.py
```
![image](https://github.com/user-attachments/assets/fbcfd87c-039b-4a59-ac6b-ad354fcaf987)
