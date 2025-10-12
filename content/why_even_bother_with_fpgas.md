Title: Why Even Bother With FPGAs?
Date: 2024-12-22
Tags: fpga

# Why Even Bother With FPGAs?

FPGAs being alternative processors enjoy a fair bit of skepticism,
especially from people higher up in the pyramid of computer abstractions
(Software Engineers and the like). This post is my attempt at trying to
persuade the skeptics by way of an instance where FPGAs blow every other
kind of processor out of the water.

**TLDR**; FPGAs can allow full DNN inference at nanosecond latency only
limited by the time it takes for electrons to move across a circuit. In
comparison, CPU/GPUs may only be able to run a couple instructions in
nanosecond timeframe, entire inference will require many million/billion
of these instructions.

## FPGAs for the Unenlightened

FPGAs are circuit emulators. Digital Circuits consists of logic gates
and connections between them, FPGAs emulate logic gates and their
connections.

Logic gates can be represented by their [Truth
Table](https://en.wikipedia.org/wiki/Truth_table). Truth tables are a
form of hash table where the key is a tuple of binary values
corresponding to each input and output is a single bit representing the
output of the gate. One kind of FPGA (SRAM-based), emulate logic gates
by storing truth tables in memory.

Connections are emulated via Programmable Interconnects. Think of a
network switch, programmable interconnects are pretty much like the same
except on a very low-level. [This
document](https://cse.usf.edu/~haozheng/teach/cda4253/doc/fpga-arch-overview.pdf)
explains in detail the different VLSI architectures present in modern
FPGAs.

A programmer usually does not describe circuits in the form of logic
gates, they use abstractions in the form of HDLs to behaviorally
describe operations that a circuit must perform. A compiler
converts/maps HDL programs to FPGA primitives.

As it should be obvious by now, FPGAs are unlike processors. They do not
have any \"Instruction Set Architecture\". If there is a need, the
programmer must design and implement an ISA[^1]. FPGAs require thinking
of problems as circuits with inputs and outputs.

## The Central Argument for FPGAs

Now, let\'s build the argument.

Deep Neural Networks (DNN) inference on demands a lot of compute and is
a pretty challenging problem. Solutions to this problem manifests in the
form of ASIC accelerators and GPUs. More performance can always be
brought by scaling said processors but of-course there is a limit to how
far one can scale. For example, on the [NVIDIA Jetson
Nano](https://developer.nvidia.com/embedded/jetson-nano) the time taken
to infer a single image for the CNN model ResNet50 is \~72ms. What if we
needed something much faster, say the same inference in integral
nanoseconds? GPUs/ASICs would only be able to execute a couple
instructions in that timeframe let alone complete the inference.
Certainly they won\'t suffice.

This requirement is not made up. Nanosecond DNN inference is a real
problem faced by a team at CERN working on the Large Hadron Collider.

Here\'s a little description of the problem from their
[paper](https://arxiv.org/pdf/2006.10159):

> *The hardware triggering system in a particle detector at the CERN LHC
> is one of the most extreme environments one can imagine deploying
> DNNs. Latency is restricted to O(1)µs, governed by the frequency of
> particle collisions and the amount of on-detector buffers. The system
> consists of a limited amount of FPGA resources, all of which are
> located in underground caverns 50-100 meters below the ground surface,
> working on thousands of different tasks in parallel. Due to the high
> number of tasks being performed, limited cooling capabilities, limited
> space in the cavern, and the limited number of processors, algorithms
> must be kept as resource-economic as possible. In order to minimize
> the latency and maximize the precision of tasks that can be performed
> in the hardware trigger, ML solutions are being explored as fast
> approximations of the algorithms currently in use.*

## Solutions

There are, broadly speaking, two ways of solving this problem:

### 1. The ASIC Way

This includes CPUs/GPUs/TPUs or any other ASIC. The idea would be to to
have a large grid of multipliers and adders to carry out as many
multiply-accumulate operations in parallel. To achieve more performance,
research would be put to increase the frequency of the chip (Moore\'s
law). Compilers and specialized frameworks help abstract computation.
And if, we need more performance, specialized engineers (who have
mastered assembly language) are called upon to write performant kernels,
making use of clever tricks to have the fastest possible dot product.

### 2. The FPGA way

Through this way, the idea is to exploit FPGA\'s programming model.
Instead of writing a program for our problem, we design a circuit for
it. Each layer of a neural network would be represented by a circuit.
Inside the layer, all dot-products themselves are represented by a
circuit. If the neural network is not prohibitively large, we can even
fit the entire NN as a combinational circuit.

As you might have learnt in your digital circuits course, combinational
circuits do not contain any clocks i.e. there\'s no notion of frequency
--- inputs come in, outputs go out. The speed of computation is only
bottleneck\'ed by the time it takes electrons to pass in that chip. How
cool is that?!

## Flaws with the FPGA way

One of the biggest flaw with fitting entire problems on the FPGA is that
of [combinatorial
explosion](https://en.wikipedia.org/wiki/Combinatorial_explosion) in
complexity. For example, in order to design a circuit for a multiplier,
there are [well known
algorithms](https://en.wikipedia.org/wiki/Booth's_multiplication_algorithm)
that result in very efficient multiplier. One can avoid going this route
by directly encoding the multipliers into truth-tables. Instead of
calculating the outputs of a multiplication, we remember and look-it-up.
Here\'s verilog for a 2-bit multiplication:

``` 
module mul ( input signed [1:0] a, input signed [1:0] b, output signed [3:0] out);
 assign out[3] = (a[0] & a[1] & b[0] & b[1]);
 assign out[2] = (~a[0] & a[1] & b[1]) | (a[1] & ~b[0] & b[1]);
 assign out[1] = (~a[0] & a[1] & b[0]) | (a[0] & ~b[0] & b[1]) | (a[0] & ~a[1] & b[1]);
 assign out[0] = (a[0] & b[0]);
endmodule
```

Each output is just a combination of its inputs.

Here\'s the problem: this method of designing multipliers does not
scale! The 2bit multiplier takes 4 LUTs (pretty reasonable). But the
same for an 8bit multiplier takes \~18,000 LUTs and 3+ hrs to synthesize
(awful). The increase is at the rate of 2\^n. Many large neural networks
will have a hard time to fit on the FPGA in this way.

This doesn't signal the end for FPGAs, however. There's still a strong
case to be made for their use---just as the team at CERN has
demonstrated. In fact, they are actively leveraging this potential. They
discovered that neural network layers can be *heterogeneously quantized*
--- meaning each layer can have a different precision level depending on
its significance in the computation pipeline, as outlined in their work
[here](https://fastmachinelearning.org/hls4ml/)

If an entire network cannot fit on an FPGA, fast reconfiguration can
provide a solution. This involves configuring the hardware for one
layer, processing its outputs, then reconfiguring the hardware for the
next layer, and so on. The approach can be further refined to enable
reconfiguration at a per-channel level, allowing smaller FPGAs with
limited resources to participate. A \'compiler\' would orchestrate the
computation offline, determining the sequence and timing of
reconfigurations before the actual computation begins.

Recent interest in hyper-quantization i.e.
[1bit](https://github.com/kyegomez/BitNet), 2bit, 3bit \... networks is
a big win for the FPGA way. The lower the resolution, the more efficient
and practical the solution becomes, making FPGAs a great fit for this
approach.

## Conclusion

With the FPGA way, many problems spanning different domains can be
solved in interesting and (sometimes) superior ways. At my workplace,
we\'ve started research in the FPGA way, trying to bring it out of the
depths of complexities and solve practical problems.

The intention of this post is not to compare ASICs and FPGAs
(comparisons are futile), but to highlight how FPGAs ought to be seen
and used. In the following few months, i\'ll write more on this research
as I uncover it myself. I\'ll leave you with some links advocating for
the FPGA way[^2]

- [Learning and Memorization - Satrajit
  Chatterjee](https://proceedings.mlr.press/v80/chatterjee18a/chatterjee18a.pdf)
- [LUTnet](https://arxiv.org/abs/1904.00938)
- [George Constantinides and his
  team](https://scholar.google.com/citations?user=NTn1NJAAAAAJ&hl=en)
- [hls4ml team](https://fastmachinelearning.org/hls4ml/)

**Footnotes**

[^1]: The term \"architecture\" is a bit overloaded. The first meaning
    is of the VLSI sense i.e. how LUTs and interconnect are organized to
    make the FPGA. Another usage is for describing what all higher level
    components are being designed **on top** of the FPGA. Think matmul
    engines, caches etc. \"Architecture\" has meaning on different
    levels of circuit design.

[^2]: The is a term i\'ve coined myself. I\'ve not seen anyone else use
    it in their works.
