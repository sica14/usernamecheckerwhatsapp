# WhatsApp Username Checker

Verifica automaticamente se usernames do WhatsApp estão disponíveis ou não.

---

## O que você precisa instalar (faça na ordem)

### Passo 1 — Instalar Python
1. Acesse **https://python.org/downloads** e baixe a versão mais recente
2. Abra o instalador
3. **IMPORTANTE:** marque a caixa **"Add Python to PATH"** antes de clicar em Install
4. Clique em **Install Now** e aguarde

---

### Passo 2 — Instalar Node.js
1. Acesse **https://nodejs.org** e baixe a versão **LTS**
2. Execute o instalador e clique em Next até finalizar

---

### Passo 3 — Instalar Android Studio (emulador)
1. Acesse **https://developer.android.com/studio** e baixe o Android Studio
2. Execute o instalador, clique em Next em tudo
3. Abra o Android Studio após instalar

---

### Passo 4 — Criar o emulador Android
1. No Android Studio, vá em **Tools → Device Manager**
2. Clique em **"+"** ou **"Create Device"**
3. Selecione **Pixel 6** → clique em Next
4. Na lista de sistemas, clique na aba **"Recommended"** e baixe o **Android 13 (API 33)** clicando no ícone de download ao lado
5. Selecione ele → Next → Finish
6. Clique no botão ▶ (play) para iniciar o emulador e aguarde o Android aparecer

---

### Passo 5 — Instalar WhatsApp no emulador
> O emulador não tem Play Store, então precisamos instalar o APK manualmente.

1. Acesse **https://www.apkmirror.com** e pesquise por **WhatsApp**
2. Clique na versão mais recente → role a página e procure uma variante do tipo **APK** (não APKM nem Bundle) — escolha a **arm64-v8a** ou **universal**
3. Baixe o arquivo `.apk`
4. **Arraste o arquivo `.apk` direto para dentro da janela do emulador** — o Android vai instalar automaticamente

---

### Passo 6 — Fazer login no WhatsApp no emulador
1. Abra o WhatsApp no emulador
2. Digite o seu número de celular (com DDD e código do país, ex: +55 11 99999-9999)
3. Você vai receber o código de verificação por SMS **no seu celular de verdade**
4. Digite esse código no emulador
5. Conclua o cadastro (nome, foto — não importa)

---

### Passo 7 — Instalar Appium
1. Abra o **Prompt de Comando** (tecla Windows → digite "cmd" → Enter)
2. Cole o seguinte e pressione Enter:
   ```
   npm install -g appium
   ```
3. Aguarde terminar, depois cole isso e pressione Enter:
   ```
   appium driver install uiautomator2
   ```

---

### Passo 8 — Instalar dependências do Python
1. Ainda no Prompt de Comando, navegue até a pasta do programa:
   ```
   cd "caminho\para\a\pasta\whatsapp-username-checker"
   ```
   *(clique com o botão direito na pasta, "Copiar como caminho" e cole aqui)*
2. Execute:
   ```
   python -m pip install -r requirements.txt
   ```

---

## Como usar o programa

### Antes de cada uso:
- Abra o **Android Studio** e inicie o emulador (botão ▶ no Device Manager)
- Certifique-se que o WhatsApp está aberto no emulador e você está logado

### Adicionando os usernames para verificar:
1. Abra o arquivo **`usernames.txt`** com o Bloco de Notas
2. Coloque um username por linha
3. Salve o arquivo

### Rodando o programa:
1. **Dê dois cliques no arquivo `iniciar.bat`**
2. Uma janela preta vai abrir com o Appium rodando
3. Outra janela vai pedir para você navegar até a tela de username no WhatsApp:
   - No emulador: abra o WhatsApp → toque nos **3 pontinhos** → **Configurações** → toque no seu **nome/foto no topo** → role para baixo e toque em **Nome de usuário**
   - Certifique-se que o campo de texto está visível na tela
4. Volte para a janela preta do programa e pressione **Enter**
5. O programa vai verificar todos os usernames automaticamente

### Ver os resultados:
- Abra o arquivo **`results.csv`** com Excel ou Google Planilhas
- A coluna `status` vai mostrar:
  - `available` = username **disponível** ✓
  - `taken` = username **já está em uso**
  - `invalid` = username inválido (muito curto, caractere inválido, etc.)
  - `error` = não foi possível verificar

---

## Dicas importantes

- **Se o programa parar no meio:** é só rodar o `iniciar.bat` de novo — ele continua de onde parou automaticamente
- **Usernames válidos:** entre 6 e 25 caracteres, apenas letras, números e underline (_)
- **Não acelere demais:** o programa já tem pausas automáticas para evitar bloqueio do WhatsApp

- ---

## Usar dois emuladores ao mesmo tempo (mais rápido)

Rodar com 2 emuladores divide a lista ao meio e termina em metade do tempo.

**O que é necessário:**
- Dois emuladores criados e rodando no Android Studio
- WhatsApp instalado e logado em cada um — com **números de telefone diferentes** (não dá usar o mesmo número nos dois)

**Como configurar o segundo emulador:**
1. No Android Studio → **Tools → Device Manager → "+"**
2. Crie outro Pixel 6 com Android 13 igual ao primeiro
3. Inicie ele clicando no ▶
4. Instale o WhatsApp (arraste o `.apk`) e faça login com um número diferente

**Como verificar os nomes dos emuladores:**
1. Abra o Prompt de Comando e digite:
   ```
   adb devices
   ```
2. Vai aparecer algo como:
   ```
   emulator-5554   device
   emulator-5556   device
   ```

**Como rodar com dois emuladores:**
1. Abra o Prompt de Comando na pasta do programa
2. Inicie o Appium primeiro:
   ```
   set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk && appium
   ```
3. Abra outro Prompt de Comando na mesma pasta e rode:
   ```
   python parallel_runner.py --workers 2 --devices emulator-5554 emulator-5556
   ```
4. Navegue até a tela de username nos **dois emuladores** quando pedido
5. Os resultados vão para o mesmo `results.csv` automaticamente

| Quantidade de emuladores | Tempo estimado para 46.000 nicks |
|---|---|
| 1 emulador | ~26 horas |
| 2 emuladores | ~13 horas |
| 3 emuladores | ~9 horas |
| 4 emuladores | ~6 horas |

