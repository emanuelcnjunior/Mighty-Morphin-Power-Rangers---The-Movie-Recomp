/* No ROM required. Reproduce next-pose uploads in the bottom forced-blank
 * border, after the current pose has already appeared on the real screen. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "snes/ppu.h"
#include "snes/snes.h"

Snes *g_snes;
int snes_frame_counter;
unsigned char g_snesrecomp_last_hdmaen;
uint16_t WsShadowTile(int l, int x, uint32_t y, uint16_t t) {
  (void)l; (void)x; (void)y; return t;
}
bool WsShadowLayerActive(int l) { (void)l; return false; }
uint32_t WsShadowWorldX(int l) { (void)l; return 0; }
uint32_t WsShadowPresentWorldY(int l, int x) { (void)l; (void)x; return 0; }
uint32_t WsShadowScrollY(int l) { (void)l; return 0; }
void WsShadowOnVramWrite(uint16_t a, uint16_t v) { (void)a; (void)v; }

#define CHECK(t) do { if (!(t)) { \
  fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #t); exit(1); \
} } while (0)

static Snes machine;
static Ppu ppu;

static void display(uint16_t line, uint8_t value) {
  machine.vPos = line;
  ppu_write(&ppu, 0, value);
}

static void pose(uint16_t value) {
  ppu.vram[0x4000] = value;
  ppu.oam[1] = value;
  ppu.highOam[0] = (uint8_t)value;
  ppu.cgram[0x80] = value;
}

static void expect_pose(uint16_t value) {
  CHECK(ppu.vram[0x4000] == value);
  CHECK(ppu.oam[1] == value);
  CHECK(ppu.highOam[0] == (uint8_t)value);
  CHECK(ppu.cgram[0x80] == value);
}

int main(void) {
  g_snes = &machine;
  machine.ppu = &ppu;
  ppu_reset(&ppu);
  ppu_rasterLatchDisplayMemory(true);
  display(225, 0x80);
  pose(0x1111);
  ppu_rasterBegin(&ppu);

  /* Uploads continue beyond line 0 in the blank top border. */
  pose(0x2222);
  display(24, 0x0f);
  /* A later HUD register write must not recapture the next pose. */
  pose(0x3333);
  display(189, 0x0f);
  display(213, 0x80);
  ppu.oamAdr = 0x41;
  machine.vPos = 225;
  ppu_rasterFieldBoundary();

  ppu_rasterRenderBegin(&ppu);
  expect_pose(0x2222);
  ppu_rasterApplyLine(&ppu, 224);
  ppu_rasterRenderEnd(&ppu);
  expect_pose(0x3333);
  CHECK(ppu.oamAdr == 0x41);

  /* Drawing the same field twice is read-only and produces the same pose. */
  ppu_rasterRenderBegin(&ppu);
  expect_pose(0x2222);
  ppu_rasterRenderEnd(&ppu);
  expect_pose(0x3333);

  /* The next field captures its own complete upload. */
  pose(0x4444);
  display(24, 0x0f);
  display(213, 0x80);
  pose(0x5555);
  machine.vPos = 225;
  ppu_rasterFieldBoundary();
  ppu_rasterRenderBegin(&ppu);
  expect_pose(0x4444);
  ppu_rasterRenderEnd(&ppu);
  expect_pose(0x5555);

  /* Debug injection and hosts which did not opt in keep the live memory. */
  g_ppu_scanout_latch_bypass = 1;
  ppu_rasterRenderBegin(&ppu);
  expect_pose(0x5555);
  ppu_rasterRenderEnd(&ppu);
  g_ppu_scanout_latch_bypass = 0;
  ppu_rasterLatchDisplayMemory(false);
  ppu_rasterRenderBegin(&ppu);
  expect_pose(0x5555);
  ppu_rasterRenderEnd(&ppu);
  puts("ppu_display_memory_test: ok");
  return 0;
}
