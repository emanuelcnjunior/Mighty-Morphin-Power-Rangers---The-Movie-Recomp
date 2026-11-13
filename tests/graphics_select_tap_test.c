#include "graphics_select_tap.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); return 1; } } while(0)
int main(void) {
    GraphicsSelectTap tap = {0};
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(GraphicsSelectTap_Update(&tap,false,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,false));
    /* Select+R1, Select+L3/R3 and any later modifier must not toggle HD. */
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,true,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,true,false));
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,false));
    /* Closing a modal while Select is held must not fire on its release. */
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,true));
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(!GraphicsSelectTap_Update(&tap,false,false,true));
    /* The next independent tap works normally. */
    CHECK(!GraphicsSelectTap_Update(&tap,true,false,false));
    CHECK(GraphicsSelectTap_Update(&tap,false,false,false));
    puts("PASS: Select tap, hold, release, chord suppression and modal cancellation");
    return 0;
}
