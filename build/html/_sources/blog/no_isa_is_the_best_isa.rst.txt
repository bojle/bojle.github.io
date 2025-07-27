No-ISA is the Best ISA
######################

Last Change: |today|

This week, me and my colleague were present at the first `compilertech.org
<https://compilertech.org/>`_ workshop talking about the work we are doing at `Vicharak
<https://vicharak.in/>`_ involving FPGAs, Reconfigurable Computing and Compilers for such
computers. This small blog post is a brief summary of the talk. 

The slides (and the extended slides) for the presentation are available at:
`github.com/vicharak-in/noisa <https://github.com/vicharak-in/noisa>`_. Video for
the talk will soon be available.

Summary
*******

The talk is divided into four chapters: 

Chapter 1
---------

Chapter 1 lists the problems with modern compute, key problems being the
slowdown and end of Moore's law and Dennard scaling and the von-neumann
bottleneck. We ask ourselves whether compute should be restricted to a small
selection of available processors/architectures. Last slide in chapter 1 lists
some concrete problems where using existing compute is difficult.

Chapter 2
---------

Chapters 2 and 3 include an introduction to reconfigurable/heterogeneous
computing and EDA compilers. 

Reconfiguration and Heterogeneity are the two key ideas of the architecture that
we propose. A separation from von-neumann architectures, by the way of
flow-based reconfigurable computers is discussed.  The central theme of the idea
is to make it easy/automate the generation of **hardware** for our algorithms
instead of **programs**. In essence, the idea is to have a unique and optimal
hardware for every software. 

Chapter 3
---------

Since solving problems through reconfigurable/heterogeneous require generation
of hardware, EDA compilers and their efficiency has to be considered too.
Chapter 3 is about EDA compilers being a nightmare to deal with in terms of
flexibility, hackability, performance and adaptability.

Chapter 4
---------

The last chapter is on the work done so far. For this, we've designed our
own hardware (`Vaaman
<https://docs.vicharak.in/vicharak_sbcs/vaaman/vaaman-home/>`_) on which
applications utilizing the Reconfigurable paradigm will be designed. Two
applications on which we are actively working are: Gati (CNN accelerator)
and Periplex (Peripheral Generator).

Gati is a CNN accelerator that can generate custom (optimal) accelerator
hardware for every NN model.

Periplex provides easy generation and multiplexing of peripheral (UART, I2C,
CAN, SPI etc.) along with linux device drivers for accessing them through
POSIX APIs.
