#pragma once
#include <stdbool.h>

bool GamePrepareUserData(void);
void GameConfigurePresentation(void);
const char *GameUserDataRoot(void);
extern const char kGameDefaultConfig[];
