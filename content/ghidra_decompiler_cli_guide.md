Title: Ghidra Decompiler - CLI guide
Date: 2024-08-16
Tags: reverse engineering

# Ghidra Decompiler - CLI guide

[Ghidra](https://ghidra-sre.org/) has a decompiler that unlike the rest
of the program (written in java) is written in C++. This caught my
attention so I started to hack on it. Unfortunately, there isn\'t much
written on the decompiler if one wants to use it standalone, in the
terminal without the ghidra GUI. This article tries to fill that void.

## Building The Decompiler

Fetch and unzip the ghidra package from [their github release
page](https://github.com/NationalSecurityAgency/ghidra/releases)

``` 
$ unzip ghidra_11.1.2_PUBLIC_20240709.zip
```

`cd` into the decompiler directory and build it

``` 
$ cd ghidra_11.1.2_PUBLIC/Ghidra/Features/Decompiler/src/decompile/cpp
$ make decomp_opt -j $(nproc --all)
```

You should end up with a executable called `decomp_opt`.

## Running the Decompiler

While inside the directory, export the SLEIGHHOME env variable so our
decompiler can find it, then run the executable.

``` 
$ export SLEIGHHOME=/home/shreeyash/ghidra_11.1.2_PUBLIC
$ ./decomp_opt
[decomp]>
```

The compiler is running now waiting for commands.

**Note**:

Remember to always export the environment variable before running
decomp_opt. You could consider tossing the two commands into a script,
making life easier for you.

## Decompile and view an ELF executable

Let\'s start with a trivial c++ program with some control flow, compile
it into an executable (ELF) and decompile it.

Here\'s the program, save and compile it:

``` 
$ cat a.cpp
#include <iostream>
#define THRESHOLD 20
int foo() {
  return 10;
}
int main() {
  int b = foo();
  std::cout << "The threshold is " << THRESHOLD << '\n';
  std::cout << "You returned " << b << '\n';
  if (b < THRESHOLD) {
    std::cout << "get in\n";
  } else {
    std::cout << "get out!\n";
  }
}
$ g++ -no-pie a.cpp -o a
$ ./a
The threshold is 20
You returned 10
get in
```

The executable is ready, what\'s left now is decompilation.

Let\'s start the decompiler, and load our file:

``` 
$ ./decomp_opt
[decomp]> load file a                        
a successfully loaded: Intel/AMD 64-bit x86     
```

We\'ve loaded our executable in the decompiler. c++ is an abstract language with constructs that do not make any sense
to a CPU. These include, but are not limited to: functions, structs, loops etc. In order to implement these, the
compiler has to translate abstractions into concrete implementation which manifests itself in the form of control flow
instructions like branch, compare, and jump. If we peep into an executable, we\'ll notice what we called functions are
now \'addresses\' i.e. a number that represents a location in memory. Functions are run by jumping (i.e. setting the
program counter) to an address. Essentially, if we wish to decompile a function we had in source, we\'ll have to find
the corresponding address at which it resides. `a.cpp` has two functions: `main` and `foo`. To find the address where a
functions resides in the executable, we could use `objdump`.

``` 
$ objdump -C -D a
...
00000000004011c5 <main>:
4011c5:       f3 0f 1e fa             endbr64
4011c9:       55                      push   %rbp
4011ca:       48 89 e5                mov    %rsp,%rbp
4011cd:       48 83 ec 10             sub    $0x10,%rsp
4011d1:       e8 e0 ff ff ff          call   4011b6 <_Z5todayv>
4011d6:       89 45 fc                mov    %eax,-0x4(%rbp)
4011d9:       48 8d 05 24 0e 00 00    lea    0xe24(%rip),%rax        # 402004 <_IO_stdin_used+0x4>
4011e0:       48 89 c6                mov    %rax,%rsi
4011e3:       48 8d 05 96 2e 00 00    lea    0x2e96(%rip),%rax        # 404080 <_ZSt4cout@GLIBCXX_3.4>
4011ea:       48 89 c7                mov    %rax,%rdi
4011ed:       e8 9e fe ff ff          call   401090 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
4011f2:       48 89 c2                mov    %rax,%rdx
4011f5:       8b 45 fc                mov    -0x4(%rbp),%eax
...
```

Searching for \'main\' reveals its label which resides at address
`0x4011c5`.

``` 
[decomp]> load addr 0x4011c5 main                  
Function main: 0x004011c5                          
```

`load addr` takes an address and an optional \'label\'.
Label is essentially a name that we assign to that address. In this
case, it was \'main\'---could\'ve been anything for what its worth.

``` 
[decomp]> decompile                             
Decompiling main                                   
Decompilation complete                          
[decomp]> print C                               

xunknown8 main(void)

{
  int4 iVar1;
  xunknown8 xVar2;

  iVar1 = func_0x004011b6();
  xVar2 = func_0x00401090(0x404080,0x402004);
  xVar2 = func_0x004010c0(xVar2,0x14);
  func_0x004010a0(xVar2,10);
  xVar2 = func_0x00401090(0x404080,0x402016);
  xVar2 = func_0x004010c0(xVar2,iVar1);
  func_0x004010a0(xVar2,10);
  if (iVar1 < 0x14) {
    func_0x00401090(0x404080,0x402024);
  }
  else {
    func_0x00401090(0x404080,0x40202c);
  }
  return 0;
}
[decomp]>
```

Just like that, we\'ve decompiled our program. Notice how the names are
garbled. This is because names (of variables and functions) are really
neccessary to execute a program.

Let\'s analyze the decompiled output. The latter part of all function
names are their address. This means, we can look them up in the
`objdump`. Moreover, if the set of commands that got us
`main` s decompilation we to be repeated for all the
functions present in in the output, the resulting decompilation of main
would replace all address with the labels we assign to them. Looking up
in `objdump`, we find `func_0x004011b6` to be
foo:

``` 
...
00000000004011b6 <foo()>:
4011b6:       f3 0f 1e fa             endbr64
4011ba:       55                      push   %rbp
4011bb:       48 89 e5                mov    %rsp,%rbp
4011be:       b8 0a 00 00 00          mov    $0xa,%eax
...
```

`func_0x00401090` is not present in the executable, however,
the calls to this function are shown in the objdump thusly:

``` 
4011ed:       e8 9e fe ff ff          call   401090 <std::basic_ostream<char, std::char_traits<char> >& std::operator<< <std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&, char const*)@plt>
```

Its quite obvious from the hint that `func_0x00401090` is the operator `\<\<` overloaded to accept a
`std::basic_ostream` object and a `const char \*`. The `\@plt` at the end indicates that this
function can be found in the `.plt` section of the executable. `.plt` which stands for Procedure
Linkage Table is a redirection table of external functions that can be found in shared objects. So,
`func_0x00401090` is `operator\<\<` found in `libstdc++.so` that the program is
linked to. It takes two arguments: both addresses to objects. A search reveals that the first argumnet is the object
`std::cout` of which the definition resides in an external library (`libstdc++.so`) and the
other argument is a char literal that can be found in the `.rodata` section of the executable.

``` 
$ objdup -s -j .rodata a
Contents of section .rodata:
402000 01000200 54686520 74687265 73686f6c  ....The threshol
402010 64206973 2000596f 75207265 7475726e  d is .You return
402020 65642000 67657420 696e0a00 67657420  ed .get in..get
402030 6f757421 0a00                        out!..
```

Indeed, the string `\"The threshold is \"` is present at
address `0x0402004`.

Likewise, all following functions till `func_0x004010a0` are
overloads of `operator\<\<` that handle different types of
data. What remains is the control flow. It checks if `iVar1`
which is `b` in the original source is less than
`0x14` (`THRESHOLD`) and calls the familiar
`func_0x00401090` i.e. (`operator\<\<`).

## Conclusion

Our work was made much easier by the fact that the executable was not
\'stripped\'. Stripping is a process that gets rid of all the symbols
that are not absolutely neccessary for execution (greatly reduces
executable size). In the real world, especially if we are dealing with
propreitary software, executables might be stripped. Unstripped
executables allows us to tread faster by simply searching for symbols
like we did to find main. Stripped executables require us to trace, find
and deduce what we need. In a later article, I may demo decompilation of
stripped executables.
