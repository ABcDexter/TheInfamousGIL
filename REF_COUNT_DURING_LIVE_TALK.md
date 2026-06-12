# When I was giving this talk on Saturday, May 23rd 2026, an issue emerged which got me perplexed enough to say "I don't know" during the talk.

```python  


➜  TheInfamousGIL git:(main) python                               
Python 3.14.5+ free-threading build (heads/3.14:6588ca5, May 10 2026, 22:21:10) [Clang 17.0.0 (clang-1700.6.3.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Cmd click to launch VS Code Native REPL
>>> a=list()
>>> b=a
>>> 
>>> a=[1,2,3]
>>> b=a
>>> a[0]=1024
>>> b
[1024, 2, 3]
>>> import sys
>>> sys.getrefcount(a)
4
>>> 
KeyboardInterrupt
>>> exit()

```
This got me thinking... What!!!

___________________________________________________________

Now, the 'Why' part... 

I tried redoing this with Python 3.12 (which has GIL)

```python

➜  TheInfamousGIL git:(main) pyenv shell 3.12
➜  TheInfamousGIL git:(main) python
Python 3.12.11 (main, May 28 2026, 23:01:59) [Clang 17.0.0 (clang-1700.6.3.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Cmd click to launch VS Code Native REPL
>>> a=list()
>>> b=a
>>> a=[1,2,3]
>>> b=a
>>> a[0]=1024
>>> b
[1024, 2, 3]
>>> import sys
>>> sys.getrefcount(a)
4
>>> exit()

```

Hmmm, interesting... So this probably has nothing to do with Python version?

Letls try with Python 2.7
```python
➜  TheInfamousGIL git:(main) pyenv shell 2.7 
➜  TheInfamousGIL git:(main) python
Python 2.7.18 (default, Apr 25 2026, 11:32:33) 
[GCC Apple LLVM 17.0.0 (clang-1700.6.3.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Cmd click to launch VS Code Native REPL
>>> a=lsit()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'lsit' is not defined
>>> a=list()
>>> b=a
>>> a=[1,2,3]
>>> b=a
>>> a[0]=1024
>>> b
[1024, 2, 3]
>>> import sys
>>> sys.getrefcount(a)
4

```
Yes, do matter what version I try it with, it's still the same...

Then I start digging deeper into it and came across this StackOverflow question : https://stackoverflow.com/a/52129124/3209112


# reason = In a standard CPython REPL, evaluating an expression stores its result in the special variable _ ("last result")

so continued with Python2.7 and Bingo!!!
```python
>>> _
4
>>> sys.getrefcount(a)
3
```

100 points to Gryffindor ;)