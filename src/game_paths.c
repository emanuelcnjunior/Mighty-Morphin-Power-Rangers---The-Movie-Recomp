/* User-owned saves and external artwork survive replacement of the build. */
#include "game_paths.h"
#include "common_rtl.h"
#include "desktop/config.h"
#include "desktop/sdl_compat.h"
#include "host_paths.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#ifdef HIBYTE
#undef HIBYTE
#endif
#include <windows.h>
#else
#include <sys/stat.h>
#include <errno.h>
#endif

static char s_pack_dir[512];
static char s_user_dir[1024];

const char kGameDefaultConfig[] =
    "[General]\nAutosave = 0\n"
    "[Graphics]\nGraphicsProfileVersion = 4\nGraphicsMode = 1\n"
    "GraphicsFilter = 1\nNewRenderer = 1\nNoSpriteLimits = 1\n"
    "Fullscreen = 1\nWindowScale = 3\nIgnoreAspectRatio = 0\n"
    "DisplayAspect = 0\nIntegerScale = 0\nVSync = 1\n"
    "[Sound]\nEnableAudio = 1\nVolume = 100\n"
    "[KeyMap]\nQuickSave = F1\nQuickLoad = F2\nSaveStateMenu = F11\n"
    "GraphicsToggle = F6\nGraphicsMenu = F10\nHDReload = F4\nOpenLauncher = Ctrl+l\n"
    "[GamepadMap]\nEnableGamepad1 = true\nEnableGamepad2 = true\n";

const char *GameUserDataRoot(void) { return s_user_dir; }

static bool ensure_directory(const char *path) {
#ifdef _WIN32
    wchar_t wide[1024];
    if (!MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, path, -1, wide, 1024))
        return false;
    if (CreateDirectoryW(wide, NULL)) return true;
    DWORD attributes = GetFileAttributesW(wide);
    return attributes != INVALID_FILE_ATTRIBUTES &&
           (attributes & FILE_ATTRIBUTE_DIRECTORY) != 0;
#else
    if (mkdir(path, 0700) == 0) return true;
    struct stat info;
    return errno == EEXIST && stat(path, &info) == 0 && S_ISDIR(info.st_mode);
#endif
}

bool GamePrepareUserData(void) {
    const char *override = getenv("POWER_RANGERS_USER_DATA");
    char *pref = NULL;
    const char *root = override && *override ? override : NULL;
#ifdef _WIN32
    char local[1024];
    if (!root) {
        wchar_t wide[1024];
        DWORD length = GetEnvironmentVariableW(L"LOCALAPPDATA", wide, 1024);
        if (length && length < 980 &&
            wcscat_s(wide, 1024, L"\\PowerRangersMovieRecomp") == 0 &&
            WideCharToMultiByte(CP_UTF8, 0, wide, -1, local, sizeof(local), NULL, NULL))
            root = local;
    }
#else
    if (!root) root = pref = SDL_GetPrefPath(NULL, "PowerRangersMovieRecomp");
#endif
    char absolute[1024];
    char saves[1024];
    bool ok = root && *root && snesrecomp_abspath(root, absolute, sizeof(absolute));
    root = absolute;
    ok = ok && ensure_directory(root);
    int save_len = ok ? snprintf(saves, sizeof(saves), "%s/saves", root) : -1;
    int pack_len = ok ? snprintf(s_pack_dir, sizeof(s_pack_dir), "%s/hd-packs", root) : -1;
    ok = ok && save_len > 0 && (size_t)save_len < sizeof(saves) &&
         pack_len > 0 && (size_t)pack_len < sizeof(s_pack_dir) &&
         ensure_directory(saves) && ensure_directory(s_pack_dir);
    if (ok) {
        snprintf(s_user_dir, sizeof(s_user_dir), "%s", root);
        RtlSetSaveRoot(saves);
        RtlSetQuickSaveRoot(saves);
        fprintf(stderr, "[Power Rangers] Saves: %s\n", saves);
    } else {
        fprintf(stderr, "Cannot prepare the Power Rangers user-data directory.\n");
    }
    SDL_free(pref);
    return ok;
}

void GameConfigurePresentation(void) {
    /* Start fullscreen even when upgrading an existing windowed config.
     * Alt+Enter and F10 can still switch to a window during the session. */
    g_config.fullscreen = 1;
    g_config.graphics_select_toggle = true;
    g_config_dirty = true;
    /* The shared HD pack loader still has a TMNT-specific historical default.
     * Supply this title's own directory without replacing a user-selected pack. */
    if (!g_config.hdpack_dir[0]) {
        snprintf(g_config.hdpack_dir, sizeof(g_config.hdpack_dir), "%s", s_pack_dir);
        g_config_dirty = true;
    }
}
