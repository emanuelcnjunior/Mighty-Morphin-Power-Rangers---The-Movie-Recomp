# Mighty Morphin Power Rangers: The Movie — PC Recomp (v0.2.2-dev.1)

Compilação de desenvolvimento da branch `dev` (`a8d7202`) para Windows x64 contendo o novo Launcher customizado, suporte completo a cheats e ferramentas de validação.

---

### Novidades e Melhorias desta Versão (`dev`)

- **Novo Launcher Customizado (`Launcher.exe`)**:
  - Interface moderna com tema escuro, logo oficial e navegação por abas.
  - Abas dedicadas: **Controles**, **Cheats** (com seleção visual e contadores ativos), **Vídeo & Áudio**.
  - Suporte bilíngue integrado em tempo de execução: **Português (Brasil)** e **English**.
  - Validação e detecção automática da ROM original de SNES (USA).
  - Scripts diretos de inicialização rápida: `Jogar.bat` e `Play.bat`.

- **Catálogo de 40 Cheats Integrado**:
  - Arquivo `config/power_rangers_the_movie_usa.cht` com 40 códigos SNES Game Genie e Pro Action Replay (PAR).
  - Descrições bilíngues (PT/EN) e marcação de exclusividade mútua (ex: seleção de Ranger, vidas infinitas, energia infinita, invencibilidade, pulo alto, pulo lunar, armas no máximo, etc.).
  - Arquivo original mantido em `config/mighty-morphin-power-rangers-the-movie-usa.cht`.

- **Ferramentas de Validação e Diagnóstico (`tools/`)**:
  - `tools/cheat_tool.py`: Decodificador de Game Genie / PAR, validação e aplicação.
  - `tools/rom_tool.py`: Verificação de integridade da ROM USA (1.572.864 bytes, SHA-256 `c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039`).
  - `tools/run_diagnostic.py`: Geração de pacote sanitizado de diagnóstico para abertura de issues.
  - Suíte de 10 testes unitários automatizados em `tests/` e workflow de CI em `.github/workflows/tooling.yml`.

- **Executável Recompilado x64**:
  - Binário compilado `MightyMorphinPowerRangersTheMovieSNESRecomp.exe` incluído no pacote portátil.

---

### Instruções de Instalação e Execução

1. Baixe e extraia o pacote ZIP em uma pasta gravável do seu computador.
2. Forneça a sua própria ROM original descompactada de Super Nintendo (USA, 1.572.864 bytes) no diretório do jogo ou selecione via Launcher.
3. Execute `Launcher.exe` (ou dê dois cliques em `Jogar.bat` / `Play.bat`).

---

### Integridade dos Arquivos (Checksums)

- **Arquivo**: `Power-Rangers-The-Movie-PC-v0.2.2-dev.1-Windows-x64.zip`
- **SHA-256**: `c53d9bef6de708d084328f4d3eb4c8339c6c353ddf3d3e181d4bb15472b1e4a7`
- **Arquivo**: `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip`
- **SHA-256**: `c53d9bef6de708d084328f4d3eb4c8339c6c353ddf3d3e181d4bb15472b1e4a7`
