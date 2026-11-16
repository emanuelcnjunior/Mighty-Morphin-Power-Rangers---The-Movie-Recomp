# Relatório de testes — v0.2.1 Windows x64

Data: 2026-11-16

## Artefato verificado

- ZIP: `Power-Rangers-The-Movie-PC-v0.2.1-Windows-x64.zip`
- Tamanho: 4.585.854 bytes
- SHA-256: `56d1963b0713188b60cd1586715547f75f4251df4dd5890a1787ebdfae9466d8`
- Executável interno: 11.610.624 bytes; SHA-256
  `b7f89cf372dd38addf1809a8f82ab29a4dad9d149f6c4f98474264071318b4a5`

## Resultados desta reconstrução

| Verificação | Resultado |
| --- | --- |
| Empacotamento `installer/build.ps1 -SkipBuild` | Passou |
| Nome explícito `Windows-x64` | Passou |
| EXE e `recomplauncher.json` na raiz | Passou |
| DLLs, recursos, licenças e manifesto | Passou |
| Deny-list de ROM, saves e dados pessoais | Passou |
| Parse JSON de `recomplauncher.json` | Passou |
| Cobertura do manifesto | Passou: 36 arquivos de payload |
| CTest da suíte `tests/` | Passou: 4 de 4 |
| CTest em `build` e `build-installer` | Nenhum teste adicional registrado |
| Validador oficial/schema em Python | Passou |
| Testes de validação/importação de ROM | Passou: 12 de 12 |
| Smoke legado de instalação/reinstalação | Passou: 7 verificações |

O ZIP, seu manifesto e todos os hashes foram revalidados nesta reconstrução.
Nenhuma ROM, save ou configuração pessoal foi encontrada no payload.

## Validação manual obrigatória no RecompLauncher

1. Abra Settings > Developers, habilite Developer Tools e escolha Add a build.
2. Selecione o ZIP Windows x64.
3. Confirme que Easy Setup reconhece o perfil e solicita a ROM.
4. Importe a ROM USA original, sem cabeçalho, e confirme a validação.
5. Inicie o jogo e confira vídeo e áudio.
6. Confira teclado/controle; crie, carregue e liste saves.
7. Reinstale a build e confirme a preservação de saves, controles e preferências.
8. Registre versão do launcher, sistema, logs e resultado de cada passo.

Não há aprovação do RecompLauncher declarada: o teste real no aplicativo ainda
está pendente.
