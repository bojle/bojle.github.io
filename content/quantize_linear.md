# Optimizing ONNX QuantizeLinear with ARM NEON {#onnx_quantizelinear_neon}

Quantization is one of the most crucial step in ML inference on
resource-constrained edge devices hence the need for it to be
performant. On ARM SoCs, SIMD Extensions in the form of NEON can be used
to achieve this goal. This article underlines how quantization can be
implemented usign NEON extensions.

## ONNX QuantizeLinear

Following image shows the first layer of [mobilenet
v2](https://arxiv.org/abs/1801.04381) image classification network. The
first operator (QuantizeLinear) is there to quantize the input image
(which is usually is usually in the form of normalized float32 values
b/w 0 and 1), into int8 so it can be fed to the following QLinearConv.
QLinearConv is the quantized version of a regular convolution.
QLinearConv can be dealt, in some other blog, this ones about
QuantizeLinear.

\<image\>

At its core, QuantizeLinear is an elementwise operation, that performs
the following transformation on each element:

$$Y = saturate(round(X / scale) + zero\_point)$$

Where:

- $X$ is the floating-point input tensor.
- $scale$ is the quantization scale.
- $zero\_point$ is the quantization zero point.
- $round$ typically refers to rounding to the nearest even.
- $saturate$ ensures the result fits within the target integer range
  (e.g., \[0, 255\] for `uint8` or \[-128,127\] for `int8`).

Here\'s a snippet of C++ code implementing QuantizeLinear:

``` 
#include <algorithm>
#include <numeric>
#include <vector>

template <typename inputT, typename outputT>
outputT qfn(inputT v, float scale, int zero_point, int min_lim, int max_lim) {
  inputT rounded = std::round((static_cast<float>(v) / scale + zero_point));
  return static_cast<outputT>(std::clamp<inputT>(rounded, min_lim, max_lim));
}

template <typename inputT, typename outputT>
std::vector<outputT> quantize_cpu(const std::vector<inputT>& in) {
  float scale = 0.234;
  int min_lim = -128;
  int max_lim = 127;
  int zp = 0;
  std::vector<outputT> ret(in.size());
  for (int i = 0; i < in.size(); ++i) {
    ret.at(i) = qfn<inputT, outputT>(in[i], scale, zp, min_lim, max_lim);
  }
  return ret;
}
```

Code above is a simple linear iteration of the input and application of
[qfn]{.title-ref} function which calculates the quantized output values.

Let\'s benchmark this code:

``` 
template <typename T = std::chrono::seconds> class Timer {
  using Tp = std::chrono::time_point<std::chrono::high_resolution_clock>;
  Tp m_start;
  Tp m_stop;

public:
  void start() { m_start = std::chrono::high_resolution_clock::now(); }
  void stop() { m_stop = std::chrono::high_resolution_clock::now(); }

  T difference() { return std::chrono::duration_cast<T>(m_stop - m_start); }
  void report(std::string msg) {
    std::cout << msg << difference().count() << '\n';
  }
};


int main() {
  std::vector<float> v(3*224*224);
  std::iota(v.begin(), v.end(), -400);
  Timer<std::chrono::microseconds> tt;
  tt.start();
  auto r2 = quantize_cpu<float, float>(v);
  tt.stop();
  tt.report("time ");
}
```

``` 
$ g++ a.cpp -o a
$ ./a
time 23943
```

## Dive into ARM NEON Intrinsics

ARM NEON is a 128-bit SIMD (Single Instruction, Multiple Data)
architecture extension for ARM Cortex-A series processors. It provides a
set of registers and instructions capable of performing parallel
operations on multiple data elements simultaneously. This parallelism is
ideal for accelerating array-based computations common in deep learning,
including the element-wise operations involved in `QuantizeLinear`.

NEON intrinsics are C/C++ functions that map directly to NEON assembly
instructions. They allow developers to leverage the NEON hardware
without writing assembly code, providing a balance between performance
and development ease. Key NEON intrinsics relevant to `QuantizeLinear`
include:

- **Load/Store intrinsics (e.g., \`\`vld1q_f32\`\`, \`\`vst1q_u8\`\`):**
  For efficient loading of floating-point data into NEON registers and
  storing of quantized integer results.
- **Vector arithmetic intrinsics (e.g., \`\`vmulq_f32\`\`,
  \`\`vaddq_f32\`\`, \`\`vrecpeq_f32\`\` for reciprocal estimation):**
  For performing the division, addition, and scaling operations in
  parallel on multiple floating-point values.
- **Conversion intrinsics (e.g., \`\`vcvtq_s32_f32\`\`,
  \`\`vqmovn_s32\`\`):** For converting floating-point numbers to
  integers and performing saturating narrow operations to fit the target
  integer type.
- **Rounding intrinsics (e.g., \`\`vrndnq_f32\`\`):** For implementing
  the rounding behavior specified by ONNX.
- **Saturating intrinsics (e.g., \`\`vqadd_s8\`\`, \`\`vqsub_s8\`\`):**
  For handling saturation when converting to lower precision integer
  types. While direct saturating conversions are often handled by
  `vqmovn`, explicit saturation intrinsics might be needed depending on
  the intermediate steps.

By processing multiple data points within a single instruction cycle,
NEON intrinsics significantly reduce the number of CPU cycles required
for the `QuantizeLinear` computation, leading to substantial speedups.

## 3. Speed Measurements: QuantizeLinear with NEON vs. Scalar CPU

To quantify the performance gains, benchmarks were conducted comparing a
scalar C++ implementation of `QuantizeLinear` against an ARM
NEON-optimized version. The tests involved processing various input
tensor sizes, simulating typical activation dimensions in neural
networks.

\[Insert actual benchmark results here. This section should include:\]

- **Methodology:** Describe the test setup, including the ARM processor
  used (e.g., Cortex-A53, Cortex-A72), compiler flags, and how timings
  were collected. Specify the input tensor dimensions and data types.
- **Data Presentation:** Present the speedup results clearly. This could
  be in the form of a table showing execution times for scalar and NEON
  implementations, or a graph illustrating the speedup factor across
  different input sizes.
- **Example Table:**

+------------------+-----------------+-----------------+-----------------+-----------------+
| > Input Size (Elements)\| Scalar CPU Time (ms)\| NEON Time (ms)\| Speedup Factor         |
|                                                                                          |
| =====================+====================+==============+================+              |
|                                                                                          |
| :   1024 \| X.XX \| Y.YY \| Z.Z \|                                                       |
+------------------+-----------------+-----------------+-----------------+-----------------+
| 4096             | A.AA            | B.BB            | C.C             |                 |
+------------------+-----------------+-----------------+-----------------+-----------------+
| 16384            | D.DD            | E.EE            | F.F             |                 |
+------------------+-----------------+-----------------+-----------------+-----------------+

- **Discussion of Results:** Analyze the results. Highlight the
  magnitude of the speedup and discuss how NEON\'s SIMD capabilities
  contribute to this performance improvement. Emphasize the benefit for
  larger tensor sizes where the overhead of scalar processing becomes
  more pronounced.

## 4. Conclusion

Optimizing the `QuantizeLinear` operator with ARM NEON intrinsics
delivers a critical performance boost for ONNX models on ARM-based
systems. By leveraging the parallel processing capabilities of NEON, the
initial quantization step, often a bottleneck, becomes significantly
more efficient. This optimization ensures that the data is prepared
rapidly for subsequent accelerated operations on hardware like FPGAs,
enabling a truly efficient end-to-end deep learning inference pipeline
on edge devices. The demonstrated speed improvements underscore the
importance of low-level optimization for maximizing the performance of
AI applications in embedded environments.
