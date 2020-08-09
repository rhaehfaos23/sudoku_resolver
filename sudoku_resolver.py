from asyncio.exceptions import CancelledError
from asyncio.tasks import create_task
import os
import time
import asyncio
import itertools
import sys

sudoku = [
    "39   2   ",
    "  7  48  ",
    "  4 5 196",
    "6721   84",
    " 3194    ",
    " 4 7  61 ",
    "92 4 356 ",
    "  35 14 9",
    "    69   "
]

sudoku_position = []

def check_resolved():
    global sudoku
    for row in sudoku:
        if len(set(row)) != 9:
            return False
    
    for col in range(9):
        column = ''
        for row in range(9):
            column += sudoku[row][col]
        if len(set(column)) != 9:
            return False

    for x in range(3):
        for q in range(3):
            block = ''
            for y in range(3):
                for z in range(3):
                    block += sudoku[3*x+y][3*q+z]
            if len(set(block)) != 9:
                return False

    return True


def check_item(row_index, col_index, num):
    """
    지금 현재 넣을 수 있는 숫자인가?
    """
    global sudoku
    if sudoku[row_index].find(num) != -1:
        return False

    col = ''
    for row in sudoku:
        col += row[col_index]
    if col.find(num) != -1:
        return False
    
    col = ''
    row_block_index = int(row_index / 3)
    col_block_index = int(col_index / 3)

    row_index_in_block = row_index % 3
    col_index_in_block = col_index % 3

    for y in range(3):
        for x in range(3):
            if x == col_index_in_block and y == row_index_in_block:
                continue
            col += sudoku[3*row_block_index + y][3*col_block_index+x]

    return col.find(num) == -1


def init_sudoku_position():
    global sudoku, sudoku_position
    sudoku_position = []
    for row in sudoku:
        block = ''
        for item in row:
            if item != ' ':
                block += 'O'
            else:
                block += 'X'
        sudoku_position.append(block)


def is_all_filled():
    global sudoku

    for row in sudoku:
        if set(row) != {'1', '2', '3', '4', '5', '6', '7', '8', '9'}:
            return False
    
    return True
        

def resolve_sudoku(y=0, x=0):
    global sudoku, sudoku_position #, verbose
    
    if is_all_filled():
        if check_resolved():
            return True
        else:
            return False

    if sudoku_position[y][x] == 'O':
        if x < 8:
            return resolve_sudoku(y, x+1)
        else:
            return resolve_sudoku(y+1, 0)
    else:
        for candi in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if check_item(y, x, candi):
                sudoku[y] = sudoku[y][:x] + candi + sudoku[y][x+1:]
                if x < 8:
                    if resolve_sudoku(y, x+1):
                        return True
                else:
                    if resolve_sudoku(y+1, 0):
                        return True
                sudoku[y] = sudoku[y][:x] + ' ' + sudoku[y][x+1:]


def print_sudoku():
    global sudoku, start, sudoku_position
    print("\033[%d;%dH" % (0, 0))
    for index, row in enumerate(sudoku):
        if index % 3 == 0:
            print("-" * 59)
        row_str = ''
        for i, ch in enumerate(row):
            if i % 3 == 0:
                row_str += '||'
            else:
                row_str += '|'
            if sudoku_position[index][i] == 'O':
                row_str += '\033[31m'
            row_str += f'  {ch}  '
            if sudoku_position[index][i] == 'O':
                row_str += '\033[39m'
        print(f'{row_str}||')
        print("-" * 59)

verbose = False

def input_sudoku():
    global sudoku #, verbose

    for i in range(9):
        row = input(f'스도쿠를 입력하세요 {i+1} 번째 행 (빈칸은 0으로 적으세요): ')
        sudoku[i] = row.replace('0', ' ')
    os.system('cls')
    init_sudoku_position()
    print_sudoku()
    ok = input("제대로 입력하셨나요?(y/n): ")
    if ok.lower() == 'y':
        # v = input("과정을 출력할까요? (시간 오래걸리지도 모름)(y/n): ")
        # verbose = True if v.lower() == 'y' else False
        return
    else:
        input_sudoku()

def input_sudoku_file():
    global sudoku

    with open('sudoku') as fp:
        row = 0
        while True:
            line = fp.readline()
            if not line:
                break
            sudoku[row] = line.strip().replace('0', ' ')
            row += 1
    
    init_sudoku_position()
    print_sudoku()
    ok = input("제대로 입력하셨나요?(y/n): ")
    if ok.lower() == 'y':
        return
    else:
        exit(1)


async def print_calculating(msg):
    write, flush = sys.stdout.write, sys.stdout.flush
    for ch in itertools.cycle('|/-\\'):
        status = ch + f' {msg}'
        write(status)
        flush()
        write(f'\033[{len(status)*2}D')
        try:
            await asyncio.sleep(0.1)
        except CancelledError:
            break

async def main():
    while True:
        os.system('cls')
        input_sudoku_file()
        os.system('cls')
        task = asyncio.create_task(print_calculating('스도쿠 푸는중!!'))
        # task = asyncio.create_task(async_print_sudoku())
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, resolve_sudoku)
        task.cancel()
        await task
        os.system('cls')
        print_sudoku()
        restart = input('재시작?? (y/n): ')
        
        if restart.lower() == 'n':
            break

if __name__ == '__main__':
    asyncio.run(main())