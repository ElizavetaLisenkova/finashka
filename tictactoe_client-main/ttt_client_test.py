from tkinter import *
from PIL import ImageTk, Image
import socket
import threading

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

field = [None, None, None, None, None, None, None, None, None] # O = 0, X = 1
centers = [(200, 100), (300, 100), (400, 100), (200, 200), (300, 200), (400, 200), (200, 300), (300, 300), (400, 300)]
current_move = 1
your_move = 3
game_ended = False
labels = []

buttons = []
images = []
x_images = []
o_images = []

root = Tk()
root.resizable(width=False, height=False)
c = Canvas(width=700, height=450)
c.pack(fill=BOTH)


def click(mv, isServer):  # проверка всех параметров при клике пользователя на ячейку игрового поля и дальнейший вызов
    if not game_ended and (current_move == your_move or isServer):
        mv=int(mv)
        move(mv)
        buttons[mv].place_forget()
        if not isServer:  # если функция вызывается сервером то сообщение клика не отправится
            client.send(f'click {mv}'.encode(FORMAT))
    if not game_ended and your_move == 3:
        client.send('my move is'.encode(FORMAT))


def restart(isServer):  # рестарт игры
    global field, game_ended, current_move
    c.delete('object')
    field = [None, None, None, None, None, None, None, None, None]
    game_ended = False
    current_move = 1
    for i in range(9):
        buttons[i].place(x=centers[i][0], y=centers[i][1], height=100, width=100)
    for i in labels:
        i.place_forget()
    move_label = Label(image=move_x_img)
    move_label.place(x=175, y=3, width=350, height=97)
    if not isServer:
        client.send('restart'.encode(FORMAT))


def restart_bt():
    restart(False)


def move(cell):  # функция отрисовки хода и проверки победы
    global current_move, game_ended, your_move
    if current_move == 1:
        field[cell] = 1
        draw_x(cell)
        current_move = 0
        move_label = Label(image=move_o_img)
        move_label.place(x=175, y=3, width=350, height=97)
    elif current_move == 0:
        field[cell] = 0
        draw_o(cell)
        current_move = 1
        move_label = Label(image=move_x_img)
        move_label.place(x=175, y=3, width=350, height=97)
    if win(field) == 0:
        move_label = Label(image=win_o_img)
        move_label.place(x=175, y=3, width=350, height=97)
        game_ended = True
    elif win(field) == 1:
        move_label = Label(image=win_x_img)
        move_label.place(x=175, y=3, width=350, height=97)
        game_ended = True
    elif win(field) == 2:
        move_label = Label(image=draw_img)
        move_label.place(x=175, y=3, width=350, height=97)
        game_ended = True


def win(field):  # функция определяющая победу
    win_combinations = ((0, 1, 2), (2, 5, 8), (6, 7, 8), (0, 3, 6), (0, 4, 8), (2, 4, 6), (3, 4, 5), (1, 4, 7))
    for i in win_combinations:
        if field[i[0]] == field[i[1]] == field[i[2]] and field[i[0]] != None:
            return field[i[0]]
    none_count = 0
    for i in range(9):
        if field[i] is None:
            none_count +=1
    if none_count == 0:
        return 2
    return None


def draw_x(number):
    global centers, labels
    labels.append(Label(image=x_images[number]))
    labels[-1].place(x=centers[number][0], y=centers[number][1], width=100, height=100)


def draw_o(number):
    global centers, labels
    labels.append(Label(image=o_images[number]))
    labels[-1].place(x=centers[number][0], y=centers[number][1], width=100, height=100)


def exit(isServer):
    if not isServer:
        client.send('!DISCONNECT'.encode(FORMAT))
    root.destroy()


def exit_bt():
    exit(False)


def your_move_setter(arg):
    global your_move
    your_move = arg


def server_scan():  # сканнер серверных сообщений
    while True:
        msg = client.recv(HEADER).decode(FORMAT)
        isServer = True

        for i in range(9):
            if msg == f'click {i}':
                click(i, isServer)

        if msg == 'restart':
            restart(isServer)

        if msg == '!DISCONNECT':
            exit(isServer)

        if msg == 'play x':
            your_move_setter(1)

        if msg == 'play o':
            your_move_setter(0)


background_img = Image.open(f'images/fon.jpg').resize((700, 450))
background_img = ImageTk.PhotoImage(background_img)
c.create_image(0, 0, image=background_img, anchor=NW)


for i in range(9):
    img = Image.open(f'images/{i+1}.jpg').resize((100, 100))
    images.append(ImageTk.PhotoImage(img))
    img = Image.open(f'images/x{i+1}.jpg').resize((100, 100))
    x_images.append(ImageTk.PhotoImage(img))
    img = Image.open(f'images/o{i+1}.jpg').resize((100, 100))
    o_images.append(ImageTk.PhotoImage(img))

for i in range(9):
    buttons.append(Button(text='', bd=0, image=images[i]))
    buttons[i].place(x=centers[i][0], y=centers[i][1], height=100, width=100)


buttons[0].config(command=lambda: click(0, False))
buttons[1].config(command=lambda: click(1, False))
buttons[2].config(command=lambda: click(2, False))
buttons[3].config(command=lambda: click(3, False))
buttons[4].config(command=lambda: click(4, False))
buttons[5].config(command=lambda: click(5, False))
buttons[6].config(command=lambda: click(6, False))
buttons[7].config(command=lambda: click(7, False))
buttons[8].config(command=lambda: click(8, False))

close_img = Image.open(f'images/vykhod.jpg').resize((100, 100))
close_img = ImageTk.PhotoImage(close_img)
restart_img = Image.open(f'images/restart.jpg').resize((100, 100))
restart_img = ImageTk.PhotoImage(restart_img)

restart_btn = Button(text='', command=restart_bt, image=restart_img, bd=0)
restart_btn.place(x=550, y=200, height=100, width=100)
close = Button(text='', command=exit_bt, image=close_img, bd=0)
close.place(x=50, y=200, height=100, width=100)

move_o_img = Image.open(f'images/khod_o.jpg').resize((350, 97))
move_o_img = ImageTk.PhotoImage(move_o_img)
move_x_img = Image.open(f'images/khod_x.jpg').resize((350, 97))
move_x_img = ImageTk.PhotoImage(move_x_img)
win_o_img = Image.open(f'images/vyigral_o.jpg').resize((350, 97))
win_o_img = ImageTk.PhotoImage(win_o_img)
win_x_img = Image.open(f'images/vyigral_x.jpg').resize((350, 97))
win_x_img = ImageTk.PhotoImage(win_x_img)
draw_img = Image.open(f'images/nichya.jpg').resize((350, 97))
draw_img = ImageTk.PhotoImage(draw_img)

move_label = Label(image=move_x_img)
move_label.place(x=175, y=3, width=350, height=97)

thread = threading.Thread(target=server_scan)
thread.start()

root.mainloop()
