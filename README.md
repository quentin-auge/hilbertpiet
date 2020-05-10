# Hilbertpiet

Generate
[Piet](https://www.dangermouse.net/esoteric/piet.html) programs that print a given string to
stdout. Make them represent [Hilbert curves](https://en.wikipedia.org/wiki/Hilbert_curve).

Execute the resulting Piet program with [npiet](https://www.bertnase.de/npiet/).

## What does it look like?

### Hello World!

```
$ hilbertpiet -i 'Hello World!' -o images/hello_world.png
```

![Hello World!](images/hello_world.png)

### Pi

```
$ hilbertpiet -i '3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679' -o images/pi.png
```

![Hello World!](images/pi.png)

### Cowsay Lorem Ipsum

```
$ cat lorem.txt | cowsay | hilbertpiet -o images/cowsay.png
```

![Cowsay Lorem Ipsum](images/cowsay.png)

```
$ npiet images/cowsay.png
 _________________________________________
/ Lorem ipsum dolor sit amet, consectetur \
| adipiscing elit. Curabitur eu maximus   |
| enim. Curabitur velit eros, placerat    |
| sit amet leo vel, pretium tincidunt     |
| eros. Integer consectetur ante vel      |
| sapien ullamcorper interdum. Proin in   |
| porttitor turpis. Donec cursus erat     |
| quis consectetur hendrerit. Suspendisse |
| est arcu, hendrerit eu maximus in,      |
| ultricies non ipsum. Praesent porta     |
| ornare sem ac euismod. Etiam quis odio  |
| hendrerit, elementum eros nec,          |
| scelerisque ex. Class aptent taciti     |
| sociosqu ad litora torquent per conubia |
| nostra, per inceptos himenaeos. Mauris  |
| luctus vel mauris pharetra efficitur.   |
\ Sed quis porta orci.                    /
 -----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

## How is it done?

1. Encode input string as a list of Piet operations that push ascii codes to stack and dump them
back as characters to stdout. 
    ```
    $ hilbertpiet -i 'Hello World!' -o images/hello_world.png -v
    ...
    Input length = 12
    ...
    165 codels before mapping
    Piet operations = [Init(), PushNumber(n=72), OutChar(), PushNumber(n=101), OutChar(), PushNumber(n=108), OutChar(), PushNumber(n=108), OutChar(), PushNumber(n=111), OutChar(), PushNumber(n=32), OutChar(), PushNumber(n=87), OutChar(), PushNumber(n=111), OutChar(), PushNumber(n=114), OutChar(), PushNumber(n=108), OutChar(), PushNumber(n=100), OutChar(), PushNumber(n=33), OutChar()]
    ```

2. Find and serialize the list of Piet operations that represents each ascii code with the smallest
number of codels, modifying the stack through arithmetic operations.
    ```
    $ optimize-piet-numbers --limit 127 hilbertpiet/data/numbers.pkl -v --show-only
    ...

    111 = (4 ** 2 - 1) ** 2 // 2 - 1
    PushNumber(n=111).ops = [Extend(), Extend(), Extend(), Push(), Duplicate(), Multiply(), Push(), Substract(), Duplicate(), Multiply(), Extend(), Push(), Divide(), Push(), Substract()]
    cost = 15
    
    112 = (4 ** 2 - 1) ** 2 // 2
    PushNumber(n=112).ops = [Extend(), Extend(), Extend(), Push(), Duplicate(), Multiply(), Push(), Substract(), Duplicate(), Multiply(), Extend(), Push(), Divide()]
    cost = 13
    
    113 = 2 * 4 ** 2 + (3 ** 2) ** 2
    PushNumber(n=113).ops = [Extend(), Push(), Extend(), Extend(), Extend(), Push(), Duplicate(), Multiply(), Multiply(), Extend(), Extend(), Push(), Duplicate(), Multiply(), Duplicate(), Multiply(), Add()]
    cost = 17
    
    114 = 7 ** 3 // 3
    PushNumber(n=114).ops = [Extend(), Extend(), Extend(), Extend(), Extend(), Extend(), Push(), Duplicate(), Duplicate(), Multiply(), Multiply(), Extend(), Extend(), Push(), Divide()]
    cost = 15
    
    115 = 5 * (5 ** 2 - 2)
    PushNumber(n=115).ops = [Extend(), Extend(), Extend(), Extend(), Push(), Extend(), Extend(), Extend(), Extend(), Push(), Duplicate(), Multiply(), Extend(), Push(), Substract(), Multiply()]
    cost = 16
    ```

3. Iteratively generate all moves needed to produce a
[Hilbert curve II](https://elc.github.io/posts/plotting-fractals-step-by-step-with-python/#hilbert-curve-ii)
with enough iterations to accomodate the codels, using
[L-systems](https://en.wikipedia.org/wiki/L-system).

4. Map Piet operations onto U-turns of the Hilbert curve, making sure the directional pointer is
always positioned in a way that the next codel remains on the curve.
    ```
    $ hilbertpiet -i 'Hello World!' -o images/hello_world.png
    ...
    2 Hilbert curve iterations
    ```

5. Map the Piet operations printing the string onto the remaining spots of the curve.
    ```
    $ hilbertpiet -i 'Hello World!' -o images/hello_world.png
    ...
    403 codels after mapping
    ```

6. Run the resulting Piet operations to get the position and color of each codel.
    ```
    $ hilbertpiet -i 'Hello World!' -o images/hello_world.png -v
    ...
    # Operation Stack Value Position DP
    Push  [2, 6] 1 (9+0j) 🡺
    Duplicate  [2, 6, 6] 1 (10+0j) 🡺
    UTurnClockwise 
      Push  [2, 6, 6, 1] 1 (11+0j) 🡺
      Duplicate  [2, 6, 6, 1, 1] 1 (12+0j) 🡺
      Duplicate  [2, 6, 6, 1, 1, 1] 1 (13+0j) 🡺
      Pointer  [2, 6, 6, 1, 1] 1 (13+1j) 🡻
      Pop  [2, 6, 6, 1] 1 (13+2j) 🡻
      Pointer  [2, 6, 6] 1 (12+2j) 🡸
    Multiply  [2, 36] 1 (11+2j) 🡸
    Multiply  [72] 1 (10+2j) 🡸
    OutChar  [] 1 (9+2j) 🡸
    Extend  [] 2 (8+2j) 🡸
    Push  [2] 1 (7+2j) 🡸
    Extend  [2] 2 (6+2j) 🡸
    Push  [2, 2] 1 (5+2j) 🡸
    UTurnAntiClockwise 
      Extend  [2, 2] 2 (4+2j) 🡸
      Extend  [2, 2] 3 (3+2j) 🡸
      Push  [2, 2, 3] 1 (2+2j) 🡸
      Duplicate  [2, 2, 3, 3] 1 (1+2j) 🡸
      Duplicate  [2, 2, 3, 3, 3] 1 2j 🡸
      Pointer  [2, 2, 3, 3] 1 3j 🡻
      Pop  [2, 2, 3] 1 4j 🡻
      Pointer  [2, 2] 1 (1+4j) 🡺
    ...
    ```

7. Since (in our case) the color of each codel is determined by the first codel of the program,
we're getting for free as many program as valid colors in Piet (18 of them).

```
$ hilbertpiet -i 'Hello World!' -o images/hello_world.gif
```

![Animated Hello World!](images/hello_world.gif)

## How is it run?

Requires Python >= 3.7.

* Clone the repository:
    ```
    git clone https://github.com/quentin-auge/hilbertpiet.git
    ```

* Move into the directory:
    ```
    cd hilbertpiet/
    ```

* (Optional) Create a virtual environment and activate it:
    ```
    virtualenv -p python3 .venv
    source .venv/bin/activate
    ```

* Install the application inside the virtualenv
    ```
    pip install .
    ```

* Run the tests
   ```
   pip install tox
   tox 
   ```

* Show script usage
    ```
    $ hilbertpiet --help
    usage: hilbertpiet [-h] [--file INPUT | --input INPUT] [--verbose] [--codel-size CODEL_SIZE] [--initial-color INITIAL_COLOR] --out OUT
    
    Generate a Hilbert-curve-shaped Piet program printing a given string
    
    optional arguments:
      -h, --help            show this help message and exit
      --file INPUT, -f INPUT
                            input string file (default stdin)
      --input INPUT, -i INPUT
                            input string (default stdin)
      --verbose, -v         debug mode
      --codel-size CODEL_SIZE, -n CODEL_SIZE
                            output codel size (default: 20)
      --initial-color INITIAL_COLOR, -c INITIAL_COLOR
                            initial color (default: red)
      --out OUT, -o OUT     output image file
    ```

* Run the script
    ```
    $ hilbertpiet -i 'Hello World!' -o images/hello_world.png
    Input length = 12
    Skipping 0 non-ascii characters
    
    165 codels before mapping
    
    2 Hilbert curve iterations
    404 codels after mapping
    
    Ouput: Hello World!
    
    Saving program to images/hello_world.png
    ```
