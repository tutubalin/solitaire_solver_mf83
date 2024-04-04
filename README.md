# Solitaire solver for Möbius Front '83

As most of the Zachtronics games do, Möbius Front '83 includes a built-in Solitaire game.

This project is automatic solver for it. 

***Currently supports only Windows due to AutoHotKey v2 dependency.***

***Currently supports only 2560x1440 resolution***

## Installation

1. Install Python 3
2. Install golang
3. Install AutoHotKey v2
4. Clone this repo

## Usage

```
start screenshot.ahk
python scanner.py | go run solve.go
```

Then while in Solitaire game, press `Scroll Lock` button.

## How it works

`screenshot.ahk` sets up a hook on `Scroll Lock` button. When it's pressed, it saves screenshot to `tmp/screenshot.png` file and waits.

`scanner.py` waits for screenshot, then it uses Convolution NN to detect cards layout and output it as text. It deletes screenshot file afterwards.

`solve.go` takes layout as input and finds the best solution for the current layout. Depending on layout it usually achieve from 95 to 120 points. 
Then it creates `tmp/solution.ahk` which contains mouse commands to solve solitaire.

When `screenshot.ahk` detects that `tmp/solution.ahk` is created, executes it, waits for completion and deletes it.
