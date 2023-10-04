VERSION = "nanoquiz-v0.2.2.py"

update_check_time = 0

import tkinter, os, shelve, time, random, asyncio

class Flag:
    def __init__(self):
        self.state = False
    
    def set(self):
        self.state = True

async def main() -> None:
    asyncio.create_task(update_check_loop())

    with shelve.open(f"{os.path.dirname(__file__)}/knowledge") as knowledge:
        data: list[tuple[str, str]] = await load_files()
        for i in dict(knowledge):
            if not i in data:
                del knowledge[i]
        
        knowledge_copy = list(dict(knowledge))
        for i in data:
            if not i in knowledge_copy:
                knowledge[i[0]] = (0, 0)
        del knowledge_copy
        
        while True:
            (question, answer), = random.choices(data, gen_weights(data, knowledge))
            correct = await display_question(question, answer)
            knowledge[question] = (time.time(), knowledge[question][1] * 0.5 + correct * 0.5)
            await asyncio.sleep(2)


def gen_weights(data: list[tuple[str, str]], sh: shelve.Shelf) -> list[float]:
    return [(time.time()-sh[i[0]][0])*(1.1-sh[i[0]][1]) for i in data]
        
async def display_question(question: str, answer: str) -> bool:
    window: tkinter.Tk = tkinter.Tk()
    window.title("NanoQuiz")

    confirm: Flag = Flag()
    close: Flag = Flag()

    label: tkinter.Label = tkinter.Label(window, text=question)
    label.grid(row=0, column=0, columnspan=2)
    entry: tkinter.Entry = tkinter.Entry(window)
    entry.grid(row=1, column=0)
    button: tkinter.Button = tkinter.Button(window, text="OK", command=confirm.set)
    button.grid(row=1, column=1)

    window.protocol("WM_DELETE_WINDOW", lambda: (window.destroy(), close.set()))

    entry.bind("<Return>", lambda x:confirm.set())
    
    entry.focus_set()

    while not (confirm.state or close.state):
        if close.state:
            quit()
        window.update()
        await asyncio.sleep(.2)

    if question.startswith("?"):
        confirm.state = False
        good: Flag = Flag()
        label.config(text=answer, fg="#222200")
        entry.grid_remove()
        badbutton: tkinter.Button = tkinter.Button(window, text="ŹLE", command=confirm.set, fg="#550000")
        badbutton.grid(row=1, column=0)
        button.config(text="DOBRZE", fg="#005500", command=good.set)

        while not (confirm.state or good.state):
            window.update()
            await asyncio.sleep(.2)
        window.destroy()
        return good.state

    else:
        if entry.get().lower() == answer.lower():
            label.config(text="DOBRZE!", fg="#005500")
            window.update()
            await asyncio.sleep(1)
            window.destroy()
            return True
        else:
            label.config(text=f"ŹLE: {answer}", fg="#550000")
            window.update()
            await asyncio.sleep(10)
            window.destroy()
            return False
    

async def load_files() -> list[tuple[str, str]]:
    data: list[tuple[str, str]] = []
    quiz_dir: str = f"{os.path.dirname(__file__)}/quiz"
    if not os.path.exists(quiz_dir):
        os.mkdir(quiz_dir)
    if not os.listdir(quiz_dir):
        exit("no quiz found")
    for file in os.listdir(quiz_dir):
        with open(f"{quiz_dir}/{file}", "r") as quiz_file:
            while True:
                question = quiz_file.readline()
                if not question:
                    break
                data.append((question.removesuffix("\n").removesuffix("\r"), quiz_file.readline().removesuffix("\n").removesuffix("\r")))
    return data
        
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

if __name__ == "__main__":
    asyncio.run(main())
