VERSION = "nanoquiz-v0.2.0.py"

update_check_time = 0

import tkinter, os, shelve, time, random, asyncio

class Flag:
    state: bool = False

    def set(self):
        self.state = True

    def unset(self):
        self.state = False

    def flip(self):
        self.state = not self.state

async def main() -> None:
    asyncio.create_task(update_check_loop())
    asyncio.create_task(setup_optional())

    with shelve.open(f"{os.path.dirname(__file__)}/knowledge") as sh:
        data: list[tuple[str, str]] = await load_files()
        for i in dict(sh):
            if not i in data:
                del sh[i]
        
        shk = list(dict(sh))
        for i in data:
            if not i in shk:
                sh[i[0]] = (0, 0)
        del shk
        
        while True:
            (q, a), = random.choices(data, gen_weights(data, sh))
            correct = await display_question(q, a)
            sh[q] = (time.time(), sh[q][1] * 0.5 + correct * 0.5)
            await asyncio.sleep(2)


def gen_weights(data: list[tuple[str, str]], sh: shelve.Shelf) -> list[float]:
    return [(time.time()-sh[i[0]][0])*(1.1-sh[i[0]][1]) for i in data]
        
async def display_question(q: str, a: str) -> bool:
    w: tkinter.Tk = tkinter.Tk()
    w.title("SuperQuiz")

    shouldexit: Flag = Flag()

    label: tkinter.Label = tkinter.Label(w, text=q)
    label.grid(row=0, column=0, columnspan=2)
    entry: tkinter.Entry = tkinter.Entry(w)
    entry.grid(row=1, column=0)
    button: tkinter.Button = tkinter.Button(w, text="OK", command=shouldexit.set)
    button.grid(row=1, column=1)

    w.protocol("WM_DELETE_WINDOW", lambda: (w.destroy(), os._exit(0)))

    while not shouldexit.state:
        w.update()
        await asyncio.sleep(.2)

    if q.startswith("?"):
        shouldexit.state = False
        good: Flag = Flag()
        label.config(text=a, fg="#222200")
        entry.grid_remove()
        badbutton: tkinter.Button = tkinter.Button(w, text="ŹLE", command=shouldexit.set, fg="#550000")
        badbutton.grid(row=1, column=0)
        button.config(text="DOBRZE", fg="#005500", command=good.set)

        while not shouldexit.state or good.state:
            w.update()
            await asyncio.sleep(.2)
        w.destroy()
        return good.state

    else:
        if entry.get().lower() == a.lower():
            label.config(text="DOBRZE!", fg="#005500")
            w.update()
            await asyncio.sleep(1)
            w.destroy()
            return True
        else:
            label.config(text=f"ŹLE: {a}", fg="#550000")
            w.update()
            await asyncio.sleep(10)
            w.destroy()
            return False
    

async def load_files() -> list[tuple[str, str]]:
    data: list[tuple[str, str]] = []
    quizdir: str = f"{os.path.dirname(__file__)}/quiz"
    for file in os.listdir(quizdir):
        with open(f"{quizdir}/{file}", "r") as f:
            while True:
                q = f.readline()
                if not q:
                    break
                data.append((q.removesuffix("\n").removesuffix("\r"), f.readline().removesuffix("\n").removesuffix("\r")))
    return data

async def setup_optional():
    try:
        os.system("python3 -m pip install keyboard")
        import keyboard
        keyboard.add_hotkey("ctrl+shift+q, n, q", exit)
    except ImportError as e:
        print("Ignoring keyboard import error:", e)
        
async def update_check_loop() -> None:
    #setup
    global requests
    os.system("python3 -m pip install requests")
    import requests

    #update
    while True:
        await update()
        await asyncio.sleep(3600)

async def update() -> None:
    print("chcecking for updates...")
    r = requests.get("https://cat24a.github.io/nanoquiz/latestv1.txt")
    if r.status_code != 200:
        print("couldn't check for updates, please check your internet connection")
        return
    latest = r.content.decode("utf-8")
    latest = latest.removesuffix("\n")
    if latest == VERSION:
        print("this is the latest version")
        return

    print(f"downloading update: {latest}")
    r = requests.get(f"https://cat24a.github.io/nanoquiz/v/{latest}")
    if r.status_code != 200:
        print("update failed")
        return
    
    with open(__file__, "wb") as f:
        f.write(r.content)
        os.system(f'open "{__file__}"')
        exit("update completed")

if __name__ == "__main__":
    asyncio.run(main())
