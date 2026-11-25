using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Windows.Forms;

[assembly: System.Reflection.AssemblyTitle("Mighty Morphin Power Rangers: The Movie Launcher")]
[assembly: System.Reflection.AssemblyVersion("0.2.1.0")]
[assembly: System.Reflection.AssemblyFileVersion("0.2.1.0")]

internal sealed class Launcher : Form
{
    private static readonly string Folder = AppDomain.CurrentDomain.BaseDirectory;
    private const string RomExpectedHash = "c706b70097c679f6f0ced6f77a30620807d0b2555fc3c683c0ec2fc791176039";
    private const long RomExpectedSize = 1572864; // 12 Mbits

    private static string UserDataFolder
    {
        get
        {
            string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string path = Path.Combine(local, "PowerRangersMovieRecomp");
            if (!Directory.Exists(path))
            {
                try { Directory.CreateDirectory(path); } catch { }
            }
            return path;
        }
    }

    private static string ConfigFile
    {
        get { return Path.Combine(UserDataFolder, "config.ini"); }
    }

    private static string LauncherIni
    {
        get { return Path.Combine(Folder, "launcher.ini"); }
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern uint GetPrivateProfileString(string section, string key, string fallback,
        StringBuilder result, uint size, string path);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool WritePrivateProfileString(string section, string key, string value, string path);

    private static string ReadIni(string file, string section, string key, string fallback)
    {
        var sb = new StringBuilder(4096);
        GetPrivateProfileString(section, key, fallback, sb, (uint)sb.Capacity, file);
        string res = sb.ToString();
        int comment = res.IndexOf(';');
        if (comment >= 0) res = res.Substring(0, comment);
        return res.Trim();
    }

    private static void SaveIni(string file, string section, string key, string value)
    {
        WritePrivateProfileString(section, key, value, file);
    }

    // Modern sleek color palette inspired by Power Rangers
    private static readonly Color Night = Color.FromArgb(16, 18, 24);
    private static readonly Color Surface = Color.FromArgb(26, 30, 40);
    private static readonly Color SurfaceLight = Color.FromArgb(36, 42, 56);
    private static readonly Color Ink = Color.FromArgb(242, 245, 250);
    private static readonly Color Muted = Color.FromArgb(154, 166, 182);
    private static readonly Color RangerRed = Color.FromArgb(214, 40, 40);
    private static readonly Color RangerGold = Color.FromArgb(232, 179, 67);
    private static readonly Color RangerBlue = Color.FromArgb(0, 120, 212);

    private static readonly string[] Actions = {
        "Ataque / Attack (Y)",
        "Pulo / Jump (B)",
        "Especial / Special (A)",
        "Poder Ranger / Ranger Power (X)",
        "Trocar Plano / Switch Plane (L)",
        "Trocar Plano / Switch Plane (R)"
    };

    private static readonly string[] PadButtons = {
        "Quadrado / Square (Y)",
        "Cruz / Cross (B)",
        "Círculo / Circle (A)",
        "Triângulo / Triangle (X)",
        "L1 / LB",
        "R1 / RB",
        "L2 / LT",
        "R2 / RT"
    };

    private static readonly int[] DefaultBindings = { 0, 1, 2, 3, 4, 5 };
    private readonly ComboBox[] bindings = new ComboBox[6];

    // Cheats catalog (40 items)
    private static readonly string[] CheatTitles = {
        "Energia Infinita · P1",
        "Invencibilidade · P1",
        "Barra Especial Infinita · P1",
        "Vidas Infinitas · P1",
        "Modificador de Personagem · P1",
        "Saúde Infinita P1 (Alternativo)",
        "Tempo Infinito · P1",
        "Começar com Muita Energia (1ª vida)",
        "Começar com Pouca Energia (1ª vida)",
        "Força de Vida Quase Infinita",
        "Pouca Energia após 1ª vida",
        "Mais Energia após 1ª vida",
        "Começar com 9 Continues",
        "Sem Continues",
        "Começar com Mega Pontuação",
        "Começar com 9 Vidas",
        "Começar com 5 Vidas",
        "Começar com 1 Vida",
        "Continues Infinitos (Modo 1P)",
        "Continues Infinitos (Modo 2P)",
        "Caixa Grande Dá Poder Máximo",
        "Duração Prolongada do Ranger Power-Up",
        "Vidas Infinitas (Alternativo)",
        "Energia Infinita (Alternativo)",
        "Invencibilidade (Alternativo)",
        "Derrotar Inimigos com Um Golpe (One Hit Kill)",
        "Invencibilidade na Fase do Snowboard",
        "Imune a Esmagamento (Can't Get Stomped)",
        "Tempo Infinito de Fuga",
        "Resgate Rápido",
        "Ativar Modo de Teste (Test Mode)",
        "Atingir Inimigos de Qualquer Lugar (Hit Anywhere)",
        "Invencibilidade Alternativa 2",
        "Coletar Itens de Qualquer Lugar",
        "Energia Infinita · P2",
        "Barra Especial Infinita · P2",
        "Energia Z",
        "Energia E",
        "Bombas Infinitas ao Coletar",
        "Tempo Infinito (Alternativo)"
    };

    private static readonly int[][] ExclusiveGroups = {
        new int[] { 15, 16, 17 }, // 9 lives, 5 lives, 1 life
        new int[] { 7, 8 },       // Max energy, little energy (1st life)
        new int[] { 10, 11 },     // Little energy, more energy (after 1st life)
        new int[] { 12, 13 },     // 9 continues, no continues
        new int[] { 18, 19 }      // 1P continues, 2P continues
    };

    private readonly CheckBox[] cheatBoxes = new CheckBox[40];
    private readonly TextBox romBox = new TextBox();
    private readonly CheckBox fullscreenBox = new CheckBox();
    private readonly CheckBox scale2xBox = new CheckBox();
    private readonly CheckBox vsyncBox = new CheckBox();
    private readonly CheckBox aspectBox = new CheckBox();
    private readonly TrackBar volumeBar = new TrackBar();
    private readonly Label volumeLabel = new Label();

    private bool english = false;
    private readonly Dictionary<Control, string> captions = new Dictionary<Control, string>();
    private static readonly Dictionary<string, string> English = new Dictionary<string, string> {
        { "Controles", "Controls" },
        { "Cheats", "Cheats" },
        { "Vídeo & Áudio", "Video & Audio" },
        { "Jogador 1", "Player 1" },
        { "Restaurar Padrão", "Restore Defaults" },
        { "ROM do Super Nintendo (USA)", "Super Nintendo ROM (USA)" },
        { "Procurar…", "Browse…" },
        { "Filtro Scale2x (HD)", "Scale2x Filter (HD)" },
        { "Tela cheia", "Fullscreen" },
        { "Sincronização Vertical (V-Sync)", "Vertical Sync (V-Sync)" },
        { "Manter Proporção 4:3", "Maintain 4:3 Aspect Ratio" },
        { "Volume do Áudio:", "Audio Volume:" },
        { "Jogar", "Play" },
        { "Idioma", "Language" },
        { "Atalhos rápidos:", "Quick shortcuts:" },
        { "F1 / L2: Salvar rápido · F2 / R2: Carregar rápido", "F1 / L2: Quick Save · F2 / R2: Quick Load" },
        { "F11 / Share+R1: Navegador de Saves · F6: Alternar HD", "F11 / Share+R1: Save Browser · F6: Toggle HD" },
        { "F10: Ajustes de Vídeo · Alt+Enter: Alternar Tela Cheia", "F10: Video Settings · Alt+Enter: Toggle Fullscreen" },
        { "Selecione os códigos ativos para a próxima partida:", "Select active cheat codes for your next game:" },
        { "Opções de Apresentação e Som", "Display & Audio Settings" }
    };

    private string Translate(string text)
    {
        string trans;
        return english && English.TryGetValue(text, out trans) ? trans : text;
    }

    private void CollectCaptions(Control parent)
    {
        foreach (Control child in parent.Controls)
        {
            if (English.ContainsKey(child.Text) && (child is Label || child is ButtonBase))
                captions[child] = child.Text;
            CollectCaptions(child);
        }
    }

    private void ApplyLanguage(bool isEnglish)
    {
        english = isEnglish;
        foreach (var pair in captions)
            pair.Key.Text = Translate(pair.Value);
    }

    private static Label TextAt(Control host, string text, int x, int y, int w, int h,
                                float size, Color color, bool bold = false)
    {
        var label = new Label
        {
            Text = text,
            ForeColor = color,
            BackColor = Color.Transparent,
            Bounds = new Rectangle(x, y, w, h),
            Font = new Font("Segoe UI", size, bold ? FontStyle.Bold : FontStyle.Regular)
        };
        host.Controls.Add(label);
        return label;
    }

    private static Button ButtonAt(Control host, string text, int x, int y, int w, int h)
    {
        var button = new Button
        {
            Text = text,
            ForeColor = Ink,
            BackColor = Surface,
            FlatStyle = FlatStyle.Flat,
            Cursor = Cursors.Hand,
            Bounds = new Rectangle(x, y, w, h),
            Font = new Font("Segoe UI", 10, FontStyle.Bold)
        };
        button.FlatAppearance.BorderSize = 0;
        host.Controls.Add(button);
        return button;
    }

    public Launcher(string[] args)
    {
        Text = "Mighty Morphin Power Rangers: The Movie - PC Recomp";
        try
        {
            string iconPath = Path.Combine(Folder, "power-rangers.ico");
            if (File.Exists(iconPath))
                Icon = new Icon(iconPath);
            else
                Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        }
        catch { }

        StartPosition = FormStartPosition.CenterScreen;
        Font = new Font("Segoe UI", 9.5f);
        ClientSize = new Size(840, 580);
        BackColor = Night;
        ForeColor = Ink;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;

        // Left sidebar
        var rail = new Panel { Bounds = new Rectangle(0, 0, 220, 580), BackColor = Surface };
        Controls.Add(rail);

        // Logo / Cover panel
        var sleeve = new Panel
        {
            Bounds = new Rectangle(12, 14, 196, 170),
            Padding = new Padding(2),
            BackColor = RangerRed
        };
        rail.Controls.Add(sleeve);

        Image logoImg = null;
        try
        {
            using (var stream = typeof(Launcher).Assembly.GetManifestResourceStream("logo.png"))
            {
                if (stream != null) logoImg = new Bitmap(stream);
            }
        }
        catch { }
        if (logoImg == null)
        {
            string localLogo = Path.Combine(Folder, "logo.png");
            if (File.Exists(localLogo)) logoImg = Image.FromFile(localLogo);
        }
        if (logoImg != null)
        {
            sleeve.Controls.Add(new PictureBox
            {
                Image = logoImg,
                BackColor = Night,
                SizeMode = PictureBoxSizeMode.Zoom,
                Dock = DockStyle.Fill
            });
        }

        var navControls = ButtonAt(rail, "Controles", 12, 200, 196, 42);
        var navCheats = ButtonAt(rail, "Cheats", 12, 248, 196, 42);
        var navVideo = ButtonAt(rail, "Vídeo & Áudio", 12, 296, 196, 42);

        TextAt(rail, "Idioma", 16, 450, 180, 20, 9.5f, Muted, true);
        var languageBox = new ComboBox
        {
            DropDownStyle = ComboBoxStyle.DropDownList,
            FlatStyle = FlatStyle.Flat,
            BackColor = SurfaceLight,
            ForeColor = Ink,
            Bounds = new Rectangle(16, 474, 188, 28)
        };
        languageBox.Items.AddRange(new object[] { "Português (Brasil)", "English" });
        rail.Controls.Add(languageBox);

        TextAt(rail, "SNES · USA  |  v0.2.1", 16, 530, 190, 24, 8.5f, Muted, true);

        // Center display panels
        var padPanel = new Panel { Bounds = new Rectangle(236, 16, 588, 380) };
        var cheatsPanel = new Panel { Bounds = padPanel.Bounds, Visible = false };
        var videoPanel = new Panel { Bounds = padPanel.Bounds, Visible = false };
        Controls.Add(padPanel);
        Controls.Add(cheatsPanel);
        Controls.Add(videoPanel);

        Action<int> switchTab = delegate(int tab)
        {
            padPanel.Visible = (tab == 0);
            cheatsPanel.Visible = (tab == 1);
            videoPanel.Visible = (tab == 2);

            navControls.BackColor = (tab == 0) ? RangerRed : Surface;
            navCheats.BackColor = (tab == 1) ? RangerRed : Surface;
            navVideo.BackColor = (tab == 2) ? RangerRed : Surface;

            navControls.ForeColor = (tab == 0) ? Color.White : Muted;
            navCheats.ForeColor = (tab == 1) ? Color.White : Muted;
            navVideo.ForeColor = (tab == 2) ? Color.White : Muted;
        };

        navControls.Click += delegate { switchTab(0); };
        navCheats.Click += delegate { switchTab(1); };
        navVideo.Click += delegate { switchTab(2); };
        switchTab(0);

        // Title banner on Controls tab
        var header = new Panel { Bounds = new Rectangle(0, 0, 580, 48) };
        header.Paint += delegate(object s, PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            using (var brush = new LinearGradientBrush(new Rectangle(0, 0, 580, 48), RangerRed, RangerGold, 0f))
            using (var font = new Font("Segoe UI", 20, FontStyle.Bold))
            {
                g.DrawString("POWER RANGERS: THE MOVIE", font, brush, new PointF(0, 4));
            }
            using (var pen = new Pen(RangerRed, 2))
                g.DrawLine(pen, 0, 44, 570, 44);
        };
        padPanel.Controls.Add(header);

        TextAt(padPanel, "Jogador 1", 2, 54, 300, 22, 11, RangerGold, true);
        for (int i = 0; i < bindings.Length; i++)
        {
            int col = i / 3;
            int row = i % 3;
            int x = col * 290;
            int y = 84 + row * 44;

            TextAt(padPanel, Actions[i], x + 4, y, 270, 20, 9.5f, Ink);
            var box = new ComboBox
            {
                DropDownStyle = ComboBoxStyle.DropDownList,
                FlatStyle = FlatStyle.Flat,
                BackColor = SurfaceLight,
                ForeColor = Ink,
                Bounds = new Rectangle(x + 4, y + 20, 260, 26)
            };
            box.Items.AddRange(PadButtons);
            box.SelectedIndex = DefaultBindings[i];
            bindings[i] = box;
            padPanel.Controls.Add(box);
        }

        // Shortcuts card
        var card = new Panel { Bounds = new Rectangle(4, 230, 568, 96), BackColor = Surface };
        padPanel.Controls.Add(card);
        TextAt(card, "Atalhos rápidos:", 10, 8, 200, 20, 9.5f, RangerGold, true);
        TextAt(card, "F1 / L2: Salvar rápido · F2 / R2: Carregar rápido", 10, 28, 540, 18, 9f, Muted);
        TextAt(card, "F11 / Share+R1: Navegador de Saves · F6: Alternar HD", 10, 48, 540, 18, 9f, Muted);
        TextAt(card, "F10: Ajustes de Vídeo · Alt+Enter: Alternar Tela Cheia", 10, 68, 540, 18, 9f, Muted);

        var resetBtn = ButtonAt(padPanel, "Restaurar Padrão", 4, 340, 180, 32);
        resetBtn.BackColor = SurfaceLight;
        resetBtn.Font = new Font("Segoe UI", 9f);
        resetBtn.Click += delegate
        {
            for (int i = 0; i < bindings.Length; i++) bindings[i].SelectedIndex = DefaultBindings[i];
        };

        // CHEATS TAB
        TextAt(cheatsPanel, "Cheats", 0, 0, 300, 36, 18, RangerGold, true);
        TextAt(cheatsPanel, "Selecione os códigos ativos para a próxima partida:", 2, 38, 560, 22, 9.5f, Muted);

        var cheatScroll = new Panel
        {
            Bounds = new Rectangle(0, 64, 580, 310),
            AutoScroll = true,
            BackColor = Surface
        };
        cheatsPanel.Controls.Add(cheatScroll);

        string savedMaskStr = ReadIni(LauncherIni, "launcher", "cheats_mask", "0");
        long savedMask = 0;
        long.TryParse(savedMaskStr, out savedMask);

        for (int i = 0; i < CheatTitles.Length; i++)
        {
            int idx = i;
            var chk = new CheckBox
            {
                Text = CheatTitles[i],
                ForeColor = Ink,
                Bounds = new Rectangle(12, 6 + i * 28, 530, 24),
                Checked = (savedMask & (1L << idx)) != 0
            };
            chk.CheckedChanged += delegate
            {
                if (chk.Checked)
                {
                    // Enforce exclusivity
                    foreach (int[] group in ExclusiveGroups)
                    {
                        if (Array.IndexOf(group, idx) >= 0)
                        {
                            foreach (int other in group)
                            {
                                if (other != idx && cheatBoxes[other] != null)
                                    cheatBoxes[other].Checked = false;
                            }
                        }
                    }
                }
            };
            cheatBoxes[i] = chk;
            cheatScroll.Controls.Add(chk);
        }

        // VIDEO & AUDIO TAB
        TextAt(videoPanel, "Opções de Apresentação e Som", 0, 0, 400, 36, 18, RangerGold, true);

        vsyncBox.Text = "Sincronização Vertical (V-Sync)";
        vsyncBox.Checked = ReadIni(ConfigFile, "Graphics", "VSync", "1") != "0";
        vsyncBox.Bounds = new Rectangle(12, 60, 350, 26);
        vsyncBox.ForeColor = Ink;
        videoPanel.Controls.Add(vsyncBox);

        aspectBox.Text = "Manter Proporção 4:3";
        aspectBox.Checked = ReadIni(ConfigFile, "Graphics", "IgnoreAspectRatio", "0") == "0";
        aspectBox.Bounds = new Rectangle(12, 96, 350, 26);
        aspectBox.ForeColor = Ink;
        videoPanel.Controls.Add(aspectBox);

        TextAt(videoPanel, "Volume do Áudio:", 12, 146, 180, 22, 10f, Ink, true);
        int savedVol = 100;
        int.TryParse(ReadIni(ConfigFile, "Sound", "Volume", "100"), out savedVol);

        volumeBar.Minimum = 0;
        volumeBar.Maximum = 100;
        volumeBar.TickFrequency = 10;
        volumeBar.Value = Math.Max(0, Math.Min(100, savedVol));
        volumeBar.Bounds = new Rectangle(12, 172, 300, 40);
        videoPanel.Controls.Add(volumeBar);

        volumeLabel.Text = volumeBar.Value + "%";
        volumeLabel.ForeColor = RangerGold;
        volumeLabel.Bounds = new Rectangle(320, 174, 60, 24);
        videoPanel.Controls.Add(volumeLabel);

        volumeBar.ValueChanged += delegate
        {
            volumeLabel.Text = volumeBar.Value + "%";
        };

        // BOTTOM BAR (ROM & PLAY)
        Controls.Add(new Panel { BackColor = Surface, Bounds = new Rectangle(236, 408, 588, 2) });

        TextAt(this, "ROM do Super Nintendo (USA)", 238, 418, 440, 20, 9.5f, Muted, true);
        romBox.SetBounds(238, 442, 450, 28);
        romBox.BackColor = Surface;
        romBox.ForeColor = Ink;
        romBox.BorderStyle = BorderStyle.FixedSingle;

        string remembered = ReadIni(LauncherIni, "launcher", "rom_path", "");
        string adjacent = Path.Combine(Folder, "Mighty Morphin Power Rangers - The Movie (USA).sfc");
        if (string.IsNullOrEmpty(remembered) && File.Exists(adjacent))
            remembered = adjacent;
        romBox.Text = (args.Length > 0) ? args[0] : remembered;
        Controls.Add(romBox);

        var browseBtn = ButtonAt(this, "Procurar…", 698, 440, 124, 28);
        browseBtn.BackColor = SurfaceLight;
        browseBtn.Click += delegate
        {
            using (var dlg = new OpenFileDialog
            {
                Filter = Translate("ROM SNES (*.sfc;*.smc)|*.sfc;*.smc|Todos os arquivos (*.*)|*.*")
            })
            {
                if (dlg.ShowDialog(this) == DialogResult.OK)
                    romBox.Text = dlg.FileName;
            }
        };

        fullscreenBox.Text = "Tela cheia";
        fullscreenBox.Checked = ReadIni(ConfigFile, "Graphics", "Fullscreen", "1") != "0";
        fullscreenBox.SetBounds(238, 492, 130, 32);
        fullscreenBox.ForeColor = Ink;
        Controls.Add(fullscreenBox);

        scale2xBox.Text = "Filtro Scale2x (HD)";
        scale2xBox.Checked = ReadIni(ConfigFile, "Graphics", "GraphicsFilter", "1") != "0";
        scale2xBox.SetBounds(378, 492, 170, 32);
        scale2xBox.ForeColor = Ink;
        Controls.Add(scale2xBox);

        var playBtn = ButtonAt(this, "JOGAR", 590, 486, 232, 48);
        playBtn.BackColor = RangerRed;
        playBtn.ForeColor = Color.White;
        playBtn.Font = new Font("Segoe UI", 12f, FontStyle.Bold);
        playBtn.Click += delegate { LaunchGame(); };
        AcceptButton = playBtn;

        CollectCaptions(this);
        languageBox.SelectedIndex = (ReadIni(LauncherIni, "launcher", "language", "pt") == "en") ? 1 : 0;
        ApplyLanguage(languageBox.SelectedIndex == 1);
        languageBox.SelectedIndexChanged += delegate
        {
            ApplyLanguage(languageBox.SelectedIndex == 1);
            SaveIni(LauncherIni, "launcher", "language", english ? "en" : "pt");
        };
    }

    private void LaunchGame()
    {
        string romPath = romBox.Text.Trim().Trim('"');
        if (string.IsNullOrEmpty(romPath) || !File.Exists(romPath))
        {
            MessageBox.Show(
                this,
                Translate("Selecione sua ROM original de Super Nintendo (USA)."),
                Text,
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
            return;
        }

        // Validate ROM size and SHA-256
        try
        {
            using (var stream = File.OpenRead(romPath))
            {
                if (stream.Length != RomExpectedSize)
                {
                    MessageBox.Show(
                        this,
                        Translate("Tamanho de ROM incorreto. Esperado: 1.572.864 bytes (sem cabeçalho de copiador)."),
                        Text,
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error
                    );
                    return;
                }
                using (var sha = SHA256.Create())
                {
                    byte[] hash = sha.ComputeHash(stream);
                    string hashHex = BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
                    if (hashHex != RomExpectedHash)
                    {
                        MessageBox.Show(
                            this,
                            Translate("A ROM selecionada não corresponde à versão USA esperada.\nSHA-256 incorreto."),
                            Text,
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error
                        );
                        return;
                    }
                }
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show(this, ex.Message, Text, MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }

        // Save preferences
        try
        {
            SaveIni(LauncherIni, "launcher", "rom_path", romPath);
            SaveIni(ConfigFile, "Graphics", "Fullscreen", fullscreenBox.Checked ? "1" : "0");
            SaveIni(ConfigFile, "Graphics", "GraphicsFilter", scale2xBox.Checked ? "2" : "1");
            SaveIni(ConfigFile, "Graphics", "VSync", vsyncBox.Checked ? "1" : "0");
            SaveIni(ConfigFile, "Graphics", "IgnoreAspectRatio", aspectBox.Checked ? "0" : "1");
            SaveIni(ConfigFile, "Sound", "Volume", volumeBar.Value.ToString());

            // Save active cheats mask
            long mask = 0;
            for (int i = 0; i < cheatBoxes.Length; i++)
            {
                if (cheatBoxes[i] != null && cheatBoxes[i].Checked)
                    mask |= (1L << i);
            }
            SaveIni(LauncherIni, "launcher", "cheats_mask", mask.ToString());
        }
        catch { }

        // Find game executable
        string[] candidates = {
            Path.Combine(Folder, "MightyMorphinPowerRangersTheMovieSNESRecomp.exe"),
            Path.Combine(Folder, "..", "MightyMorphinPowerRangersTheMovieSNESRecomp.exe"),
            Path.Combine(Folder, "..", "build", "Release", "MightyMorphinPowerRangersTheMovieSNESRecomp.exe"),
            Path.Combine(Folder, "build", "Release", "MightyMorphinPowerRangersTheMovieSNESRecomp.exe")
        };

        string exePath = null;
        foreach (var cand in candidates)
        {
            if (File.Exists(cand))
            {
                exePath = Path.GetFullPath(cand);
                break;
            }
        }

        if (exePath == null)
        {
            MessageBox.Show(
                this,
                Translate("MightyMorphinPowerRangersTheMovieSNESRecomp.exe não encontrado na pasta do jogo."),
                Text,
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
            return;
        }

        try
        {
            var startInfo = new ProcessStartInfo(exePath, "\"" + romPath + "\"")
            {
                WorkingDirectory = Path.GetDirectoryName(exePath),
                UseShellExecute = false
            };
            Process.Start(startInfo);
            Close();
        }
        catch (Exception ex)
        {
            MessageBox.Show(this, ex.Message, Text, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    [STAThread]
    private static void Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new Launcher(args));
    }
}
