# Instalador Windows

O instalador inclui o executável jogável, o ícone do Ranger Vermelho, recursos
do launcher, licenças e o runtime Visual C++. Não inclui a ROM, saves, código
gerado, ferramentas de desenvolvimento ou o cache `rom.cfg` desta máquina.
O usuário não precisa instalar Python, Rust, CMake ou Visual Studio para jogar.

## Instalar e jogar

1. Execute `Power-Rangers-The-Movie-PC-Setup-v0.2.0.exe`.
2. Escolha sua ROM **USA original**, sem cabeçalho de copiador e sem patches.
   O nome e a extensão podem ser diferentes: o conteúdo é validado por SHA-256.
3. Mantenha marcada a opção de atalho na Área de Trabalho se desejar.
4. Ao terminar, abra o jogo pelo atalho com o ícone do Ranger Vermelho.

A ROM compatível possui 1.572.864 bytes e SHA-256:

```text
c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039
```

O programa é instalado por usuário em:

```text
%LOCALAPPDATA%\Programs\PowerRangersMovieRecomp\
```

A ROM verificada é importada com nome padronizado para:

```text
%LOCALAPPDATA%\PowerRangersMovieRecomp\
```

Saves ficam na subpasta `saves`, pacotes de texturas em `hd-packs` e o
`config.ini` da edição instalada fica nessa mesma pasta de dados. Desinstalar
remove o programa e seus atalhos, preservando ROM, configurações e saves.
Na próxima execução, o programa verifica a cópia importada; se estiver ausente
ou inválida, pede novamente uma ROM compatível.

## Controles principais

- **F1 / L2:** salvar rápido. **F2 / R2:** carregar rápido.
- **F11 / Share+R1:** lista de saves.
- **F6:** Original/HD. **F10:** painel gráfico.
- **Alt+Enter:** janela/tela cheia. O jogo abre em tela cheia por padrão.

O usuário relatou que o atalho Select não alternou o modo HD nesta máquina.
Use F6 ou F10; o instalador não depende desse atalho. O HD atual suaviza os
pixels e suporta pacotes externos; não inclui arte redesenhada do jogo.

## Gerar o instalador

Requer o ambiente de desenvolvimento do projeto, uma ROM local para gerar o
código, Visual C++ x64 e Inno Setup. A ferramenta Inno pode ser mantida em
`.deps/inno/compiler/ISCC.exe` em modo portátil ou informada com `-Iscc`.

```powershell
powershell -ExecutionPolicy Bypass -File installer/build.ps1
```

O script cria um build separado `build-installer`, seleciona explicitamente a
entrada retail e verifica dependências. O payload vem de uma lista de recursos
conhecidos; a validação recusa ROMs, saves, cache e arquivos de desenvolvimento.
O hash, tamanho e nome esperados da ROM vêm de `rom_identity.txt`.

Saídas:

```text
dist/Power-Rangers-The-Movie-PC-Setup-v0.2.0.exe
dist/Power-Rangers-The-Movie-PC-Setup-v0.2.0.exe.sha256
```

O `.ico` usado pelo executável, instalador e atalhos está em
`installer/assets/power-rangers.ico`. Fonte e prompt da arte em
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

O script `scripts/package_release.sh` permanece como fluxo separado para packs
de desenvolvimento/setup que recompilam localmente; não gera este instalador.
