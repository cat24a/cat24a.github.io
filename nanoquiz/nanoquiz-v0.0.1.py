VERSION = "nanoquiz-v0.0.1.py"

import tkinter, os, shelve, time, random, requests

try:
    import keyboard
except ImportError as e:
    print("Ignoring keyboard import error:", e)
else:
    keyboard.add_hotkey("ctrl+shift+q, l, s", os._exit)

def main() -> None:
    with shelve.open(f"{os.path.dirname(__file__)}/knowledge") as sh:
        data: list[tuple[str, str]] = load_files()
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
            correct = display_question(q, a)
            sh[q] = (time.time(), sh[q][1] * 0.5 + correct * 0.5)
            time.sleep(2)


def gen_weights(data: list[tuple[str, str]], sh: shelve.Shelf) -> list[float]:
    weights: list[float] = []
    for q, _ in data:
        weights.append((time.time()-sh[q][0])*(1.1-sh[q][1]))
    return weights
        
def display_question(q: str, a: str) -> bool:
    w: tkinter.Tk = tkinter.Tk()
    w.title("SuperQuiz")

    label: tkinter.Label = tkinter.Label(w, text=q)
    label.grid(row=0, column=0, columnspan=2)
    entry: tkinter.Entry = tkinter.Entry(w)
    entry.grid(row=1, column=0)
    tkinter.Button(w, text="OK", command=w.quit).grid(row=1, column=1)

    w.mainloop()

    if entry.get().lower() == a.lower():
        label.config(text="DOBRZE!", fg="#005500")
        w.update()
        time.sleep(1)
        w.destroy()
        return True
    else:
        label.config(text=f"ŹLE: {a}", fg="#550000")
        w.update()
        time.sleep(10)
        w.destroy()
        return False
    

def load_files() -> list[tuple[str, str]]:
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

def update():
    print("chcecking for updates...")
    r = requests.get("https://cat24a.github.io/nanoquiz/latestv1.txt")
    if r.status_code != 200:
        print("couldn't check for updates, please check your internet connection")
        return
    latest = r.content.decode("utf-8")
    if latest == VERSION:
        print("this is the latest version")
        return

    print(f"downloading update: {latest}")
    r = requests.get("https://cat24a.github.io/nanoquiz/{latest}")
    if r.status_code != 200:
        print("update failed")
        return
    
    with open(__file__, "wb") as f:
        f.write(r.content)
        exit("update completed")

if __name__ == "__main__":
    main()
