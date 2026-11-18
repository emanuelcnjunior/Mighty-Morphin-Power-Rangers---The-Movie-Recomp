# Distribuição Windows x64

O ZIP `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip` é a única distribuição
pública para Windows x64. O fluxo normal não gera nem publica instaladores
`.exe`. Os arquivos antigos do Inno Setup permanecem no código-fonte somente
para manutenção histórica.

O ZIP inclui o executável jogável, o ícone do Ranger Branco, recursos
do launcher, licenças e o runtime Visual C++. Não inclui a ROM, saves, código
gerado, ferramentas de desenvolvimento ou o cache `rom.cfg` desta máquina.
O usuário não precisa instalar Python, Rust, CMake ou Visual Studio para jogar.

## Extrair e jogar

1. Baixe `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip` na Release.
2. Extraia o ZIP para uma pasta gravável; não execute o jogo de dentro do arquivo.
3. Abra `MightyMorphinPowerRangersTheMovieSNESRecomp.exe`.
4. Selecione sua ROM **USA original**, sem cabeçalho de copiador e sem patches.
   O nome e a extensão podem ser diferentes: o conteúdo é validado por SHA-256.
5. Quando o launcher abrir, selecione **Play**. Se cancelar a seleção da ROM, o programa encerra.

A ROM compatível possui 1.572.864 bytes e SHA-256:

```text
c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039
```

A ROM verificada é importada com nome padronizado para:

```text
%LOCALAPPDATA%\PowerRangersMovieRecomp\
```

Saves ficam na subpasta `saves`, pacotes de texturas em `hd-packs` e o
`config.ini` fica nessa mesma pasta de dados. Remover ou atualizar a pasta
extraída preserva ROM, configurações e saves.
Ao abrir o executável novamente, o launcher usa a cópia importada. Se ela
estiver ausente ou inválida, o programa pede a seleção da ROM. Pelo
RecompLauncher, o Easy Setup importa a ROM e o botão Play usa a cópia validada.

## Controles principais

- **F1 / L2:** salvar rápido. **F2 / R2:** carregar rápido.
- **F11 / Share+R1:** lista de saves.
- **F6:** Original/HD. **F10:** painel gráfico.
- **Alt+Enter:** janela/tela cheia. O jogo abre em tela cheia por padrão.

O usuário relatou que o atalho Select não alternou o modo HD nesta máquina.
Use F6 ou F10; a distribuição não depende desse atalho. O HD atual suaviza os
pixels e suporta pacotes externos; não inclui arte redesenhada do jogo.

## Gerar a distribuição ZIP

Requer o ambiente de desenvolvimento do projeto, uma ROM local para gerar o
código e Visual C++ x64. Inno Setup não é necessário.

```powershell
powershell -ExecutionPolicy Bypass -File installer/build.ps1
```

O script cria um build separado `build-installer`, seleciona explicitamente a
entrada retail e verifica dependências. O payload vem de uma lista de recursos
conhecidos; a validação recusa ROMs, saves, cache e arquivos de desenvolvimento.
O hash, tamanho e nome esperados da ROM vêm de `rom_identity.txt`.
O instalador não executa o jogo, scripts ou downloads durante a instalação;
a importação ocorre no primeiro uso. O módulo de download/rebuild do setup
pack não é ligado ao executável retail.

O fluxo normal gera somente:

```text
dist/Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip
dist/Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip.sha256
dist/SHA256SUMS.txt
```

O `.ico` usado pelo executável está em
`installer/assets/white-ranger.ico`. Fontes da arte em
`installer/assets/ICON-SOURCE.md`.

## Testes

O gate do executável oferece `--validate-rom` e `--import-rom` não interativos.
O primeiro não cria dados de usuário; o segundo só importa bytes verificados.
São retornados 0 em sucesso, 2 para ROM inválida e 3 para falha de gravação.

```powershell
python installer/test-rom.py --exe build-installer/Release/MightyMorphinPowerRangersTheMovieSNESRecomp.exe --rom 'C:/caminho/sua-ROM-USA.sfc'
powershell -ExecutionPolicy Bypass -File installer/test-install.ps1 -Rom 'C:/caminho/sua-ROM-USA.sfc'
```

O teste de instalação usa uma pasta privada sob `build-installer`, redireciona
os dados com `POWER_RANGERS_USER_DATA`, verifica atalhos reais e desinstala o
teste no final. Ele recusa executar se já existirem instalação ou atalhos com
os mesmos nomes, para não sobrescrevê-los. A ROM e os saves normais do usuário
não são modificados. Logs, fixtures e capturas ficam em diretórios ignorados.

`installer/power-rangers.iss` e `installer/test-install.ps1` permanecem somente
para manutenção histórica do fluxo Inno e não são chamados por `build.ps1`.
O script `scripts/package_release.sh` é um fluxo separado de desenvolvimento
para antigos setup packs que recompilam localmente; ele não gera a distribuição
Windows x64 publicada.
