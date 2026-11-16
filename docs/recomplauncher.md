# RecompLauncher

## Distribuição recomendada

Use `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip` como distribuição
exclusiva no RecompLauncher. O sufixo explícito identifica plataforma e
arquitetura. Instaladores `.exe` não são gerados nem publicados pelo fluxo
normal; os arquivos Inno Setup permanecem somente para manutenção histórica.

O pacote Windows jogável inclui `recomplauncher.json` ao lado do executável.
`installer/build.ps1` gera somente o ZIP portátil, seu `.sha256` e
`SHA256SUMS.txt`, usando staging sem ROM, configurações pessoais ou saves.

O perfil usa um input de arquivo `.sfc`/`.smc` e reaproveita `--import-rom`
como preparação silenciosa. Esse comando verifica tamanho e SHA-256 antes
de copiar a ROM para `%LOCALAPPDATA%/PowerRangersMovieRecomp`. Não abre janela
nem precisa de compilação. Play passa `--no-launcher`, já existente no host.
Nenhum código do jogo foi alterado; a abertura normal mantém seu seletor.

Áudio, volume e V-Sync editam somente suas chaves em `config.ini`. Na primeira
criação, o perfil fornece os mesmos defaults de `kGameDefaultConfig`, evitando
que um INI parcial perca o perfil gráfico do jogo. A opção de janela não é
exposta porque `GameConfigurePresentation` força fullscreen em cada abertura.
O backup aponta somente para `saves`, sem incluir a ROM importada.

O formato `inputs` é usado porque o schema fornecido não oferece um `game.kind`
para ROMs de SNES. Não misturamos `game.dumps` com esse input: a compatibilidade
dessa combinação não está documentada. A identidade conhecida está em
`rom_identity.txt`: USA, 1572864 bytes, CRC32 e3ef6201. A validação efetiva continua
no importador SHA-256; não alegamos o badge de dump verificado do launcher.
O importador existente não imprime progresso intermediário para essa cópia curta.

Os antigos setup packs de `scripts/package_release.sh` precisam do assistente
de geração local. `package_launcher_profile.py` substitui o perfil no ZIP por
um perfil mínimo que abre esse assistente; esses pacotes não anunciam setup
silencioso nem as opções da edição retail. Não há AppImage neste projeto.

## Verificação manual no launcher

1. Em Settings > Developers, habilite Developer Tools e escolha Add a build.
2. Selecione `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip`.
3. Confirme que o perfil é aceito e que Easy Setup solicita a ROM sem erro.
4. Importe sua ROM USA original e sem cabeçalho; confirme a validação.
5. Pressione Play e verifique vídeo e áudio.
6. Verifique teclado/controle e crie, carregue e liste saves.
7. Reinstale a mesma build e confirme que configuração, controles e saves
   foram preservados.

Registre a versão do RecompLauncher, sistema, resultado de cada passo e logs.
Teste também uma ROM inválida: a preparação deve falhar com código 2. Não
declare aprovação antes de concluir esse teste real.

## Empacotar e publicar a release Windows

A versão em `VERSION` é `0.2.1`. A validação de schema e os testes automatizados
não equivalem à análise final da equipe do RecompLauncher.

1. Revise e versione os arquivos desta integração. As alterações locais já
   existentes em `snesrecomp` são independentes: revise-as antes de decidir o
   commit/pin que será distribuído. Não adicione ROMs, `src/gen` ou assets extraídos.
2. Gere o código localmente usando sua própria ROM, conforme o README, e execute:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File installer/build.ps1
   ```

   Requer MSVC/Visual Studio 2022, CMake e as dependências do projeto. O script
   compila a edição retail e gera somente o ZIP
   `dist/Power-Rangers-The-Movie-PC-v<VERSION>-Windows-x64.zip`, seu `.sha256`
   e `dist/SHA256SUMS.txt`.
   `-SkipBuild` serve apenas quando o Release já foi compilado e conferido.
3. Baixe o guia oficial para `build/recomplauncher-agent.md`, instale `jsonschema`
   em um ambiente Python e valide o pacote (substitua a versão no caminho):

   ```powershell
   python scripts/validate_recomplauncher.py --guide build/recomplauncher-agent.md --zip dist/Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip
   python installer/test-rom.py --exe build-installer/Release/MightyMorphinPowerRangersTheMovieSNESRecomp.exe --rom 'C:/caminho/sua-ROM-USA.sfc'
   ```

4. Extraia o ZIP numa pasta limpa e faça a verificação manual no RecompLauncher
   descrita acima. Teste também a abertura direta do executável.
   Confira que importar novamente preserva saves, controles e preferências.
   O ZIP deve ter `recomplauncher.json` e o EXE diretamente na raiz.
5. Crie uma release GitHub com tag igual a `v<VERSION>` e notas explicando Easy
   Setup, ROM USA obrigatória, opções disponíveis e limitações. Anexe o ZIP,
   seu `.sha256` e `SHA256SUMS.txt`. Nunca anexe o instalador. Marque versões de teste como
   pré-release. Não publique a pasta de staging ou os fixtures de teste.
6. Se o projeto continuar fora do catálogo, envie o repositório em
   https://recomplauncher.com/submit?platform=pc e informe o uso de `inputs`,
   `prepare` e settings INI. Depois de listado, atualize o badge para a página
   atribuída. Uma conta em https://recomplauncher.com/dev permite reivindicar
   o projeto e administrar sua página.

O schema valida os campos, mas não prova que a versão instalada do aplicativo
executa o fluxo completo. O teste no Developer tab é obrigatório antes de
anunciar compatibilidade testada de ponta a ponta. O perfil oferece setup,
opções e preparação; não anuncia o nível 3 completo com badge de dump verificado.

## Resultado da revisão local

- Guia oficial baixado novamente e comparado: sem mudanças no conteúdo.
- Perfil validado contra o JSON Schema draft-07 embutido no guia; defaults
  comparados com `kGameDefaultConfig`, sem `always` para forçar preferências.
- Build Windows Release concluído. ZIP v0.2.1 gerado localmente;
  ZIP conferido quanto ao perfil na raiz, executável, ROM conhecida e dados pessoais.
- Os 12 casos de `installer/test-rom.py` passaram: ROM válida e renomeada,
  Unicode, corrupção, região sintética incompatível, tamanho inválido,
  cabeçalho, truncamento, ausência, importação, preservação e falha de escrita.
- Importação, reimportação e rejeição preservaram byte a byte os fixtures
  isolados de save state, controles e preferências gráficas. Isso verifica
  preservação dos arquivos, não a restauração de um save em gameplay.
- Smoke test anterior abriu uma janela e encerrou com código zero tanto sem
  argumentos quanto com `--no-launcher`. Nenhuma alteração de runtime foi feita.
- Transformação do perfil de setup pack testada com ZIP sintético e schema;
  o setup pack completo multiplataforma não foi reconstruído nesta revisão.
- O fluxo legado de instalação também foi auditado antes de ser retirado da
  distribuição pública. O fluxo dentro do aplicativo RecompLauncher ainda
  precisa de validação manual pela equipe.

## Melhorias pendentes

- ROM em ZIP e ROM com cabeçalho de copiador: permitir importação sem extração
  manual, mantendo a verificação da imagem normalizada (médio).
- `portable.txt`: manter dados ao lado do executável quando solicitado (médio).
- Linux/Steam Deck e macOS jogáveis: hoje o caminho retail validado é Windows;
  portar o importador e validar distribuição e dependências (grande).
- Defaults originais: o jogo usa perfil gráfico melhorado e força fullscreen;
  oferecer escolha persistente e respeitar `RECOMPLAUNCHER_MODE` (médio).
- Prompts pelo `RECOMPLAUNCHER_PAD` e fluxo inteiro com controle, incluindo
  seleção inicial de ROM: validar e completar a experiência de sofá (médio).
- Logs: o host produz relatórios JSON; acrescentar `.log` com rotação e declarar
  sua pasta para facilitar diagnósticos no launcher (pequeno).
- INI comentado com todas as opções: documentar os defaults para edição manual
  previsível (pequeno).
- Recomp Achievements: integrar conquistas, Beaten/Mastered e leaderboards
  via https://github.com/elripalda/RecompAchievements (grande).
- Releases: publicar ZIPs versionados com notas e validar cada plataforma;
  criar o arquivo local não publica uma release (pequeno).

O perfil não foi testado dentro do aplicativo RecompLauncher nesta sessão.
O override de desenvolvimento `POWER_RANGERS_USER_DATA` não é descrito no perfil:
remova-o do ambiente ao testar os caminhos padrão do launcher.
