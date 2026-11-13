# Save/load, tela cheia e apresentação HD

## Save Game / Load Game

Este cartucho não possui SRAM de progresso. O port salva o estado completo da
partida: personagem, fase, inimigos, áudio, CPU e dados gráficos, incluindo a
continuação do frame e a correção dos sprites.

| Ação | Teclado | DS4 no mapeamento padrão |
| --- | --- | --- |
| Quick Save | F1 | L2 |
| Quick Load | F2 | R2 |
| Lista de cinco slots + Quick Save | F11 | Share + R1 |
| Selecionar slot | Setas | Direcional |
| Salvar o slot selecionado | S | Triângulo |
| Carregar o slot selecionado | X | Círculo |
| Fechar a lista | Esc | X |

O slot rápido é separado dos cinco manuais. Sobrescrever um slot manual ocupado
exige uma segunda confirmação. A lista pausa a simulação e mostra miniaturas.
Os comandos podem ser remapeados no launcher, inclusive quando o DS4Windows
apresenta o controle como Xbox virtual.

No Windows, os arquivos ficam em:

```text
%LOCALAPPDATA%\PowerRangersMovieRecomp\saves\
  slot_01.state ... slot_05.state
  quicksave.state
```

São independentes da pasta de instalação/build. No Linux/macOS, usa-se a pasta
de preferências retornada pelo SDL para `PowerRangersMovieRecomp`. O override
`POWER_RANGERS_USER_DATA` permite uma pasta isolada para testes.

Os arquivos têm CRC32, identidade do jogo, hash da ROM e identificação do
contrato de execução. Saves corrompidos ou incompatíveis são recusados antes de
alterar a máquina. Atualizações do runtime, compilador ou ABI podem invalidar
estados antigos. Saves anteriores a esta integração não têm todos os dados
necessários e não são convertidos. A gravação temporária e substituição atômica
preservam o último arquivo válido se a escrita falhar.
O Quick Save da prévia testada nesta sessão é compatível com a 0.2.0 no mesmo
Windows/MSVC, pois as alterações finais são de apresentação e entrada do host,
sem mudar o formato de execução/PPU. Essa compatibilidade foi validada com uma
cópia do arquivo real, sem alterar o original.

## Visual e tela cheia

- **F6 / Select (Share) do jogador 1:** alternar Original/HD. A troca acontece
  ao soltar um toque isolado no Select; Select+R1/L3/R3 continua reservado aos
  menus, sem alterar o visual. Start mantém somente sua função original.
- **F10:** painel gráfico: Original/HD, filtro, resolução, escala inteira,
  proporção, VSync, tela cheia e pacote HD.
- **Alt+Enter:** alternar janela/tela cheia durante o jogo.
- **Ctrl+L:** abrir o launcher sem encerrar a partida; no controle, Share + L3.
- **F4:** recarregar um pacote de texturas externo.

O jogo abre em **tela cheia**, HD com **Scale2x** e proporção preservada. É
possível mudar para janela durante a partida com Alt+Enter ou F10. O filtro
reconstrói contornos usando as cores originais. **Sharp** mantém bordas mais
nítidas com ajuste de escala, e **Nearest/Original** conserva a aparência dos
pixels. O painel oferece saídas até 3840×2160, sem alterar resolução lógica,
colisões ou velocidade da partida. Fullscreen usa o desktop do monitor.

Desative **Wide Fill / Preencher** para manter a proporção; ativá-lo estica a
imagem. Tela cheia não exige esticamento. As escolhas de vídeo persistem em
`config.ini` junto ao executável. Os saves permanecem na pasta do usuário.
Na próxima inicialização o jogo volta a abrir em tela cheia.

## Pacotes de texturas externos

O modo HD já melhora a apresentação sem pacote. Não inclui uma remasterização
desenhada dos personagens e cenários. A integração permite substituir tiles por
PNGs autorais em resoluções maiores, identificados pelo conteúdo e pela paleta,
sem depender de um endereço VRAM que o jogo reutiliza para outras animações.

O diretório padrão no Windows é:

```text
%LOCALAPPDATA%\PowerRangersMovieRecomp\hd-packs\
```

Escolha outro diretório em `HDPackDir` no `[Graphics]` do `config.ini` se necessário.
Ative **Diagnóstico / IDs** para registrar `ids.jsonl`. Inspecione os IDs com:

```powershell
python tools/hd_pack_tool.py --inspect 'C:/caminho/do/pacote/ids.jsonl'
```

Um exemplo sintético, sem arte extraída do jogo, pode ser gerado com:

```powershell
python tools/hd_pack_tool.py --example 'C:/caminho/do/pacote-exemplo'
```

O exemplo testa o formato e não corresponde a um tile de Power Rangers. Para
substituir arte no jogo, mapeie os IDs observados para PNGs que você tenha criado
ou possa utilizar. Um manifesto mínimo é:

```json
{
  "version": 1,
  "author": "Nome do artista",
  "license": "Licença ou autorização da arte",
  "entries": [
    {"id": "SHA-256 de 64 caracteres do tile observado", "file": "tile.png"}
  ]
}
```

Cada PNG deve ser RGBA, quadrado, com 8, 16, 32 ou 64 pixels. Há limite de 255
entradas por pacote. Alpha zero mantém o original. IDs de animações diferentes
são mapeados separadamente, seguindo o relógio original da partida. A recarga é
transacional: um pacote inválido mantém o anterior em uso.

A substituição preserva a cobertura e a prioridade nativas; efeitos não
suportados, como determinados modos de cor, mosaic e Mode 7, usam o original.
O HUD e os objetos continuam compondo a imagem com as regras da PPU.

## Referência e validação

Integração adaptada do [TMNT IV, revisão d17d051](https://github.com/emanuelcnjunior/TMNT-IV-Turtles-in-Time-PC-Recomp/tree/d17d051ca5ccb8051aa91e812e0ef183c14ff30c):
serialização adicional, slots persistentes, gravação atômica, painel gráfico,
shader de apresentação e loader de pacotes. O framework e o launcher já estão
nos mesmos commits efetivamente fixados por aquele repositório; seu antigo
`framework_pins.txt` não é usado para substituir esses commits.

Os testes usam o runtime real e uma ROM local verificada, comparando 180 frames
futuros após carregar em um processo novo, além de restaurações repetidas e
recusa de corrupção/identidade/schema incorretos. Os testes sintéticos cobrem
filtros na GPU, pacotes, tela cheia/configuração e falhas na gravação atômica.

```powershell
python tools/validate_runtime.py --rom 'C:/caminho/para/sua-ROM-USA.sfc'
```

Logs, estados e capturas ficam em `build/runtime-validation/`, ignorado pelo Git.
O script recompila a entrada jogável ao terminar, inclusive após falha dos testes.
Uma campanha completa, reinício do Windows e todas as combinações de monitor e
controle não fazem parte dessa validação automatizada.
O cenário de dois ports injeta entrada nas duas portas e compara a restauração;
isso não substitui homologar uma partida cooperativa completa com dois controles.
