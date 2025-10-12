Title: Links

## Links

## Essays I\'ve Liked

- [The Atomic Bomb Considered As Hungarian High School Science Fair Project -
  Scott
Alexander](https://slatestarcodex.com/2017/05/26/the-atomic-bomb-considered-as-hungarian-high-school-science-fair-project/)
- [A Mathematician\'s Apology - G.H. Hardy
  \[PDF\]](https://web.njit.edu/~akansu/PAPERS/GHHardy-AMathematiciansApology.pdf)
- [All I really need to know - David
  Stern](http://theory.caltech.edu/~preskill/all-i-really-need-to-know.pdf)
- [What I learned building a parallel processor company from scratch
  -Andreas
  Olofsson](https://parallella.org/wp-content/uploads/2017/01/hipeac_lessons.pdf)
- [Principles of Effective Research - Michael
  Nielsen](https://michaelnielsen.org/blog/principles-of-effective-research/)
- [Avoiding Classic Mistakes \[In Software Engineering\] - Steve
  McConnell](https://stevemcconnell.com/wp-content/uploads/2017/08/ClassicMistakes.pdf)
- [Infinite Monkeys - Wisdom of Hacker
  News](https://thomshutt.github.io/infinite-monkeys/)
- [Reflections on my CS PhD Application Process - Bodun
  Hu](https://www.bodunhu.com/blog/posts/reflections-on-my-cs-phd-application-process/)
- [Lessons from my PhD - Austin
  Henley](https://austinhenley.com/blog/lessonsfrommyphd.html)
- [How To Do Great Work - Paul
  Graham](http://paulgraham.com/greatwork.html)
- [Work Hard - Terence
  Tao](https://terrytao.wordpress.com/career-advice/work-hard/)
- [Turd Sandwiches and Purpose In Life - AvE
  \[video\]](https://youtu.be/E7RgtMGL7CA?si=n-JG-tI3TODkEODk)
- [The TANDBERG Way - Olve
  Maudal](https://youtu.be/34FLhwkrwoQ?si=QU1Q_wMIDMyzutwg)
- [The Bitter
  Lesson](https://www.cs.utexas.edu/~eunsol/courses/data/bitter_lesson.pdf)
- [The story of ispc (auto-vectorization is not a programming
  model)](https://pharr.org/matt/blog/2018/04/30/ispc-all)
- [On being a Senior
  Engineer](https://www.kitchensoap.com/2012/10/25/on-being-a-senior-engineer/)

## Travel Essays

- [Greenland is a beautiful
  nightmare](https://matduggan.com/greenland-is-a-beautiful-nightmare/)
- [Democratic Republic of Congo: Lubumbashi to Kinshasa](https://geoff.greer.fm/congo/)

## Papers I\'ve Liked

- [Compiler Validation via Equivalence Modulo
  Inputs](https://web.cs.ucdavis.edu/~su/publications/emi.pdf)

Interesting approach to testing a program for faults. To summarize: For
a set of inputs \'I\' to a program \'P\', \'P\' can be divided into
executed and unexecuted code (\"dead code\"). Re-ordering/manipulation
on the dead code should cause no variance to the outputs for the inputs.
This technique \"EMI\" allows one to have many versions of a program (in
this case, a compiler) and test for miscompilations.

- [Beyond the Phase Ordering Problem: Finding the Globally
Optimal Code w.r.t. Optimization Phases](https://arxiv.org/pdf/2410.03120)

Makes a case that solving the phase ordering problem of compiler passes
is not the ultimate solution for generating optimal code. For example, 
a compiler will never convert bubble sort into quick sort, no matter
the order in which optimization passes are run because it lacks a semantic
understand of the problem. Urges a "global" view of the optimization problem.

## Programming/Hacking

- [Hacker How To - Eric
  Raymond](http://www.catb.org/~esr/faqs/hacker-howto.html)
- [Architecture of Open Source Projects - Various
  Authors](https://aosabook.org/en/)
- [Linus Torvalds\' linked list argument for good taste,
  explained](https://github.com/mkirchner/linked-list-good-taste)
- [Programming rants hosted on Felix Winkleman\'s (of chicken scheme
  fame) Website](http://call-with-current-continuation.org/)
- [Continuations for
  Curmudgeons](https://intertwingly.net/blog/2005/04/13/Continuations-for-Curmudgeons)
- [Video Lan (VLC) Hacker\'s
  Guide](https://wiki.videolan.org/Hacker_Guide/Audio_Filters/)
- [Fast IO on Unixes by the way of \'yes\'
  command](https://www.reddit.com/r/unix/comments/6gxduc/how_is_gnu_yes_so_fast/)
- [Greppability is an underrated code
  metric](https://morizbuesing.com/blog/greppability-code-metric/)
- [Concise Electronics for
  Geeks](https://lcamtuf.coredump.cx/electronics/)

## Blogs

- [Josh Haberman](https://blog.reverberate.org/)
- [John Regehr](https://blog.regehr.org/)
- [Jannis Harder](https://jix.one/)
- [Max Bernstein](https://bernsteinbear.com/blog/)
- [Evan Martin](https://neugierig.org/software/blog/archive.html)
- [Nirav Patel (of Framework)](https://eclecti.cc/)
- [Krister Walfridsson (compilers, PLs,
  OS)](https://kristerw.github.io/)
- [Matt Pharr (compilers, gpus,
  rendering)](https://pharr.org/matt/blog/)
- [Riya Bisht](https://riyabisht.com/links/)
- [Alex Bradbury (compilers, LLVM)](https://muxup.com/)
- [Nelson Elhage (compilers, SWE)](https://blog.nelhage.com/)
- [Nikita Popov (LLVM)](https://www.npopov.com/)
- [Ramkumar Ramachandra (Compilers, Formal Methods)](https://artagnon.com/)
- [Fangrui Song (compilers, LLVM)](https://maskray.me/)
- [Min-Yih Hsu (compilers, LLVM)](https://myhsu.xyz/blog/)
- [Keith Tsui (compilers, LLVM)](https://juejin.cn/user/4432851098679431/posts)a
- [Fabien Sanglard (graphics, computers)](https://fabiensanglard.net/)

## Books

- [PLAI - Shriram
  Krishnamurthy](http://cs.brown.edu/courses/cs173/2012/book/)
- [Write yourself a scheme in Haskell - Jonathan
  Tang](https://en.wikibooks.org/wiki/Write_Yourself_a_Scheme_in_48_Hours)
- [OS: Three easy
  pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/#book-chapters)
- [OS Design - Xinu Approach](https://xinu.cs.purdue.edu/)

## Other Compilations of Books or Links

- [List of compiler books](https://gcc.gnu.org/wiki/ListOfCompilerBooks)
- [Resources for Amateur Compiler Writers](https://c9x.me/compile/bib/)
- [Freely Available CS Textbooks](https://csgordon.github.io/books.html)
- [Online Math
  Textbooks](http://people.math.gatech.edu/~cain/textbooks/onlinebooks.html)
- [Operating Systems](https://port70.net/~nsz/06_os.html)

## Courses

- [SENG475 - Advanced
  CPP](https://www.ece.uvic.ca/~frodo/cppbook/#videos)

## Misc

- [Simple Strength Fitness](https://ss.fitness/)
- [Nearlyfreespeech hosting](https://www.nearlyfreespeech.net/)
