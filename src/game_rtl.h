#ifndef GAME_RTL_H
#define GAME_RTL_H

#include "common_cpu_infra.h"

/* One frame of Mighty Morphin Power Rangers The Movie. See game_rtl.c â€” this is the port. */
void GameRunOneFrame(void);
void GameDrawPpuFrame(void);
void GameSessionReset(void);

extern const RtlGameInfo kGameInfo;

#endif /* GAME_RTL_H */
