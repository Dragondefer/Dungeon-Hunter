__version__ = "260.0"
__creation__ = "23-04-2025"

# Dungeon Hunter - Version 5.1.1

Dungeon Hunter is a text-based dungeon exploration RPG game where you play as a brave adventurer exploring dangerous dungeons, battling enemies, completing quests, collecting loot, and leveling up your character.

Made by Dragondefer,
You can contact me on discord : https://discord.gg/3V7xGCvxEP

## Features

- Procedurally generated dungeons with various room types: combat, treasure, shop, rest, puzzle, and boss rooms.
- Turn-based combat system with skills, critical hits, and stamina management.
- Character progression with leveling, class specialization, and skill acquisition.
- Inventory management with weapons, armor, potions, and other items.
- Quest system with objectives and rewards.
- Save and load your game progress.
- Colorful console interface for immersive gameplay.
- Debug mode for testing and development.

---

## How to Run the game

### If you have downloaded the game from the release page
You can find the latest version of the game with the 3 different ways to run it.
Under here, you will find the 3 ways to run the game, and the one I recommend such as with the source code who will get hotfix and auto update.

### Recomanded : Auto-Update (req: GIT + Python 3)
Why is this the best option:
   - Whenever you launch the game with play.bat, it automatically download the latest version of each files from the repo on github

1. Ensure you have [git](https://git-scm.com/downloads) installed
   - You can verify by typing `git` in the cmd

2. Ensure you have python 3 installed
   - You can verify by typing `python --version` in the cmd

3. Clone the repository:
   - Go to the directory you want to put the game in
   - Then open the cmd in the dir and write this command to clone the repo proprely :
   ```bash
      git clone https://github.com/Dragondefer/Dungeon-Hunter
   ```

4. Play the game by clicking on play.bat

---

### If you don't have Python installed (req: Nothing)

1. **Download the `main.exe` file**

2. **Verify its authenticity using the published SHA-256 hash** (see below):
   - Windows users can use the built-in `CertUtil` command:
```bash
CertUtil -hashfile main.exe SHA256
```
   - Linux users can use `sha256sum`:
```bash
sha256sum main.exe
```
   - MacOS users can use `shasum`:
```bash
shasum -a 256 main.exe
```

   Compare the result with the official hash:
```
df333dd96319a620199a4e4aa130537ef89078f9dbf9c7d6f1f00a6b99494c83
```

   If it doesn't match, **do not run the file** — it may have been tampered with.

3. **Execute it to play the game**  
   Double-click the `.exe` or launch it from the terminal.

> 🛠️ This `.exe` file was built using:
```bash
pyinstaller --onefile main.py
```

> Then the .exe file was given a SHA-256 hash to be able to prove his authenticity using the published hash with the command:
```bash
CertUtil -hashfile main.exe SHA256
```

The output shouls look like this:
```
SHA256 hash of main.exe:
df333dd96319a620199a4e4aa130537ef89078f9dbf9c7d6f1f00a6b99494c83
CertUtil: -hashfile command completed successfully.
```
And now your main.exe file is marked with the given hash

---

### If you only want to test the game quickly (req: Python 3)
1. Ensure you have python 3 installed
   - You can verify by typing `python --version` in the terminal

2. Install the merge python file

3. Click on it to play

3. Open a terminal or command prompt in the game directory.
4. Run the game executing:

   ```bash
   python main.py
   ```

5. Follow the on-screen prompts to start a new game or load a saved game.

---

## Gameplay Overview

- **Exploration:** Choose to explore new rooms in the dungeon. Rooms can contain enemies, treasures, shops, puzzles, or resting spots.
- **Combat:** Engage in turn-based battles with enemies. Use attacks, skills, and items strategically to survive.
- **Quests:** Complete quests such as exploring rooms or defeating enemies to earn rewards.
- **Inventory:** Manage your items, equip weapons and armor, use potions, and sell or buy items in shops.
- **Resting:** Recover health, stamina, and mana at rest rooms or by resting in the dungeon.
- **Leveling Up:** Gain experience points (XP) to level up, increase stats, and choose class specializations at certain levels.
- **Saving:** Save your progress anytime and load saved games on startup.

## Controls and Commands

- Input numbers or letters as prompted to make choices.
- In combat, choose actions like attack, use skill, use item, or attempt to run.
- Manage inventory by equipping, using, unequipping, or dropping items.
- Interact with shops to buy and sell items.
- Solve puzzles by answering riddles, guessing numbers, or making choices.
- Use the debug mode (enter "dev" during gameplay) for testing features.

## Saving and Loading

- The game automatically detects saved games in the directory.
- You can save your game progress with a custom save name.
- Load saved games on startup by choosing to load a save file.

---

# Developer playground

## Reviewing Suspicious Files 🔍

Whenever you encounter code or binaries you didn’t write yourself—especially on GitHub or any public download—treat them with healthy suspicion. Below is a step-by-step audit guide.

---

### 🐍 1. Python Scripts (`*.py`)

All Python source is plain text. You can learn exactly what it does by reading it.

#### A. Identify potentially dangerous imports

- **`import os`**  
  Grants direct OS control.  
  ```python
  import os
  os.remove("data.db")        # Deletes a file
  os.system("rm -rf /tmp/*")  # Runs a shell command
  ```
- **`import subprocess`**  
  Executes external programs:
  ```python
  import subprocess
  subprocess.Popen(["curl", "-X", "DELETE", "https://api.example.com"])
  ```
- **`eval(...)`** / **`exec(...)`**  
  Runs dynamically constructed Python code—open door for injection:
  ```python
  user_code = input(">>> ")
  exec(user_code)  # Danger: any code can run!
  ```
- **`open(..., 'w')`** or **`open(..., 'a')`**  
  Writing files; could overwrite or create malicious scripts:
  ```python
  f = open("startup.bat", "w")
  f.write("del /Q C:\\Windows\\System32\\*.*")
  f.close()
  ```

> 🔎 **Tip:** In your editor, search for `os.`, `subprocess`, `eval`, `exec`, and `open(`. Read the surrounding lines—ask “which file paths?”, “what commands?”.

#### B. Trace “tainted” inputs

1. **User-supplied strings**  
   ```python
   filename = input("File to delete: ")
   os.remove(filename)
   ```
   If `filename` is `"/etc/passwd"`, you’d wipe system files!
2. **Environment variables**  
   ```python
   path = os.environ.get("SOME_PATH")
   open(path, "r")
   ```
   Always check defaults or sanitization.

#### C. Example audit

```python
# BAD: blindly deletes based on user input
import os
target = input("What to delete? ")
os.remove(target)

# GOOD: restrict to a safe directory
import os
target = input("What to delete? ")
safe_dir = "/home/user/saves/"
path = os.path.join(safe_dir, os.path.basename(target))
if os.path.exists(path):
    os.remove(path)
else:
    print("Not allowed!")
```

---

### 🧱 2. Windows Batch Files (`*.bat`)

Batch files are also text—open in Notepad or your IDE.

#### A. Auto-update script

Typical safe content:

```bat
@echo off
git pull        REM Fetches latest code
python main.py  REM Launches game
```

#### B. Danger patterns

- **`del /S /Q`**, **`erase`**  
  ```bat
  del C:\Users\%USERNAME%\Documents\*.* /S /Q
  ```
  Deletes files/folders quietly—be careful!
- **`format`**  
  ```bat
  format C: /FS:NTFS /Q
  ```
  Can wipe entire drive fast.
- **`reg add`** / **`reg delete`**  
  ```bat
  reg delete HKLM\Software\MyApp /f
  ```
  Alters Windows Registry.

#### C. Example audit

```bat
:: Inspect this before running!
@echo off
echo "Pulling updates..."
git pull

:: BAD: would delete your Documents folder
:: del "%USERPROFILE%\Documents" /S /Q

:: GOOD: just backup saves directory
XCOPY saves backup\saves /E /I
```

---

### 🛡️ 3. Executables (`*.exe`)

Compiled binaries hide their contents. Treat with extra caution.

#### A. Why `.exe` can be risky

- It could contain hidden backdoors, file-wiping routines, keyloggers, etc.
- You **cannot** read it in a text editor to see what it does.

#### B. Build-your-own vs. download

Since you have the full Python source, you can **reproduce** the `.exe` yourself:

```bash
pip install pyinstaller
pyinstaller --onefile main.py
# Now compare your ./dist/main.exe to theirs
```

##### SHA-256 verification

1. Publish a hash:
   ```bash
   sha256sum dist/main.exe > official.sha256
   ```
2. Users verify:
   ```bash
   sha256sum downloaded.exe
   diff downloaded.exe official.sha256
   ```

If they match, you know it wasn’t tampered with.

#### C. Sandbox testing

- **Virtual Machine**: spin up a clean Windows VM.
- **Container/VM snapshots**: revert after testing.
- **Network isolation**: prevent any exfiltration.

---

### 🔄 Putting It All Together

1. **Search**  
   - Python: `grep -R "os\." -R "subprocess" -R "eval" -R "exec" .`
   - Batch: open and scan for `del`, `format`, `reg`.
   - Executable: verify checksum or rebuild locally.
2. **Read context**  
   - Check parameters or loops around dangerous calls.
   - Ensure file paths are sanitized.
3. **Test safely**  
   - Use dummy directories or VMs.
   - Validate behavior before trusting.

---

By walking through real code snippets, command explanations, and hands-on checks, you’ll build the muscle memory to audit **any** project—protecting your machine and learning valuable security practices in the process.

---

## Contributing & Feedback 💬

I welcome contributions, suggestions, and bug reports from everyone, whatever it is, it will always help — whether you’re a seasoned developer or just starting out!

- **Report Issues**: If you find a bug or have an idea for improvement, please open an [issue](https://github.com/Dragondefer/Dungeon-Hunter/issues) as it would help me a lot, thanks.
- **Suggest Features**: Use GitHub issues or pull requests to propose new mechanics, balancing tweaks, or quality-of-life (QoL) enhancements.

If you want to contact me, ask question / help, or just talk / play don't hesitate
- **Email**: For direct inquiries or if you prefer email, reach out to `dragondefer7@proton.com`.
- You can also contact me with discord :
   My discord is open to everyone, supporded language : fr/en, comming not so soon: jp/de and maybe ru
   invite link : https://discord.gg/3V7xGCvxEP

## For Beginners

- **Learning Path**:
  - Read through `game_utility.py` and `entity.py` to see how classes and functions are structured.
  - Experiment by adding simple print statements or modifying values—this is the best way to learn!
  - Also, you can look at the `debug_menu` function in the `class Player` in `entity.py`

And don't forget to ask help if needed

---

This project is licensed under the CC BY-NC 4.0 License. See [LICENSE](./LICENSE) for details.


## Credits

- Made by Dragondefer
- Uses Python 3.10.6 and standard libraries such as `random`, `os`, `sys`, `random`, `json`...
- Colorful console output powered by custom Colors module

Thank you for playing Dungeon Hunter! Enjoy your adventure and may you finish the dungeon!


---


## 📄 License – CC BY-NC 4.0

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are **free to**:

* ✅ **Share** — copy and redistribute the material in any medium or format
* ✅ **Adapt** — remix, transform, and build upon the material

As long as you:

* 📌 **Give appropriate credit** — you **must clearly credit** the original author: `@Dragondefer`, and link to this repository.
* 🚫 **Do not use the material for commercial purposes** — this includes selling, monetizing, or distributing for profit in any form.
* ⚠️ **Do not imply endorsement** — you may not suggest that the creator endorses your use.

---
