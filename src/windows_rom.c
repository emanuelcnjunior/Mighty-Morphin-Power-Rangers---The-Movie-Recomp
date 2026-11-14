/* Windows retail ROM import, adapted from the TMNT IV installer flow.
 * The shipped binary never trusts filenames and contains no ROM image. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <commdlg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include "game_paths.h"
#include "sha256.h"
#include "atomic_state_file.h"
#include "host_paths.h"
#include "snesrecomp_rom_identity.h"

#ifndef POWER_RANGERS_ROM_SIZE
#error ROM size must come from rom_identity.txt through CMake
#endif
static const wchar_t kTitle[] = L"Mighty Morphin Power Rangers The Movie - PC Recomp";

static unsigned char *ReadVerifiedRom(const wchar_t *path) {
    HANDLE file = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ, NULL,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return NULL;
    LARGE_INTEGER size;
    unsigned char *data = NULL;
    DWORD bytes = 0;
    if (GetFileSizeEx(file, &size) && size.QuadPart == POWER_RANGERS_ROM_SIZE) {
        data = malloc(POWER_RANGERS_ROM_SIZE);
        if (data && (!ReadFile(file, data, POWER_RANGERS_ROM_SIZE, &bytes, NULL) ||
                     bytes != POWER_RANGERS_ROM_SIZE)) {
            free(data); data = NULL;
        }
    }
    CloseHandle(file);
    if (data) {
        unsigned char digest[32];
        char hex[65];
        sha256_compute(data, POWER_RANGERS_ROM_SIZE, digest);
        for (unsigned i = 0; i < 32; ++i) sprintf(hex + 2*i, "%02x", digest[i]);
        if (_stricmp(hex, SNESRECOMP_ROM_EXPECTED_SHA256)) {
            free(data); data = NULL;
        }
    }
    return data;
}

static int Error(const wchar_t *message, int code) {
    MessageBoxW(NULL, message, kTitle, MB_OK | MB_ICONERROR);
    return code;
}

int GameWindowsMain(int argc, char **argv, int (*run)(int, char **)) {
    int count = 0;
    wchar_t **wide_args = CommandLineToArgvW(GetCommandLineW(), &count);
    if (!wide_args) return 1;
    bool validate = count == 3 && !wcscmp(wide_args[1], L"--validate-rom");
    bool importing = count == 3 && !wcscmp(wide_args[1], L"--import-rom");
    if (validate) {
        unsigned char *data = ReadVerifiedRom(wide_args[2]);
        int result = data ? 0 : 2;
        free(data); LocalFree(wide_args);
        return result;
    }
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-h")) {
            LocalFree(wide_args);
            return run(argc, argv);
        }
    }
    if (!GamePrepareUserData()) { LocalFree(wide_args); return 1; }
    char destination[2048], config[2048], exe_dir[2048];
    if (snprintf(destination, sizeof(destination), "%s/%s", GameUserDataRoot(), SNESRECOMP_ROM_FILE) >= sizeof(destination) ||
        snprintf(config, sizeof(config), "%s/config.ini", GameUserDataRoot()) >= sizeof(config)) {
        LocalFree(wide_args); return 1;
    }
    wchar_t wide_destination[2048];
    if (!MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, destination, -1, wide_destination, 2048)) {
        LocalFree(wide_args); return 1;
    }
    unsigned char *cached = importing ? NULL : ReadVerifiedRom(wide_destination);
    bool available = cached != NULL;
    free(cached);
    while (!available) {
        wchar_t selected[2048] = L"";
        if (importing) {
            if (wcscpy_s(selected, 2048, wide_args[2])) { LocalFree(wide_args); return 2; }
        } else {
            OPENFILENAMEW picker = {0};
            picker.lStructSize = sizeof(picker);
            picker.lpstrTitle = L"Selecione sua ROM USA de Mighty Morphin Power Rangers The Movie";
            picker.lpstrFilter = L"ROM SNES (*.sfc;*.smc)\0*.sfc;*.smc\0Todos os arquivos / All files\0*.*\0";
            picker.lpstrFile = selected;
            picker.nMaxFile = 2048;
            picker.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR;
            if (!GetOpenFileNameW(&picker)) { LocalFree(wide_args); return 0; }
        }
        unsigned char *data = ReadVerifiedRom(selected);
        if (!data) {
            if (importing) { LocalFree(wide_args); return 2; }
            Error(L"ROM incompatível ou corrompida. Selecione sua ROM USA original, sem cabeçalho ou patches.\n\nIncompatible ROM. Select the original USA ROM without a copier header or patches.", 2);
            continue;
        }
        available = snes_atomic_state_write(destination, data, POWER_RANGERS_ROM_SIZE);
        free(data);
        if (!available) {
            LocalFree(wide_args);
            return importing ? 3 : Error(L"Não foi possível importar a ROM. / Cannot import the ROM.", 3);
        }
    }
    LocalFree(wide_args);
    if (importing) return 0;
    FILE *settings = fopen(config, "rb");
    if (settings) fclose(settings);
    else if (!snes_atomic_state_write(config, kGameDefaultConfig, strlen(kGameDefaultConfig)))
        return Error(L"Não foi possível criar a configuração. / Cannot create settings.", 1);
    /* Assets are installed beside the executable; writable preferences and
     * saves are absolute paths in the user's data folder. */
    wchar_t wide_exe_dir[2048];
    if (snesrecomp_exe_dir_path("", exe_dir, sizeof(exe_dir)) &&
        MultiByteToWideChar(CP_UTF8, 0, exe_dir, -1, wide_exe_dir, 2048))
        SetCurrentDirectoryW(wide_exe_dir);
    bool explicit_config = false;
    for (int i = 1; i < argc; ++i) if (!strcmp(argv[i], "--config")) explicit_config = true;
    char **args = calloc((size_t)argc + 5, sizeof(*args));
    if (!args) return 1;
    for (int i = 0; i < argc; ++i) args[i] = argv[i];
    int n = argc;
    args[n++] = "--rom"; args[n++] = destination;
    if (!explicit_config) { args[n++] = "--config"; args[n++] = config; }
    int result = run(n, args);
    free(args);
    return result;
}
