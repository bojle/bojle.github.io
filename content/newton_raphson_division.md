Title: Faster Division With Newton-Raphson Approximation
Date: 2025-10-13
Tags: cs

Many devices, especially embedded (micro-controllers and the like) do not come
with an [FPU](https://en.wikipedia.org/wiki/Floating-point_unit) and the
circuitry required for carrying out integer division. In such a case, one looks
towards methods of approximating the results of division and storing them in
[Fixed Point](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) format.

C has standardized support for such an instance via its stdfix library. The [ISO
Document](https://standards.iso.org/ittf/PubliclyAvailableStandards/c051126_ISO_IEC_TR_18037_2008.zip)
describes the data types and functions available in `stdfix.h`.

This post describes the theory, provides a dependency-free C++ implementation of
the core algorithm and discusses optimizations to speed it up even further. In
that order.

## Theory

The problem at hand is that of division:

$$
C = \frac{N}{D}
$$

The first step to solving this is to split the problem in two: Reciprocal
calculation, followed by multiplication. This is what it looks like:

$$
C = N \cdot \left(\frac{1}{D}\right)
$$

It is assumed that the device has a fast multiplication hardware (which is
mostly the case). Thus, multiplication can be carried out by the good ol' `mul`
instruction. Now for the most tricky part - calculating the reciprocal - which
is a division operation!

As it turns out, this is a known problem and solutions are *approximately* [as
old as](http://degiorgi.math.hr/aaa_sem/Div/702-706.pdf) the [Unix
epoch](https://en.wikipedia.org/wiki/Unix_time).

### Newton-Raphson Method

The [Wikipedia
article](https://en.wikipedia.org/wiki/Division_algorithm#Newton%E2%80%93Raphson_division)
sufficiently describes *what* and *how* of the NR Method. I'll summarize and add some
missing context.

"[Newton's Method](https://en.wikipedia.org/wiki/Newton%27s_method) is a
root-finding algorithm which produces successively better approximations to the
roots (or zeroes) of a real-valued function." This is the generic iterative
equation according to Newton's method:


$$
x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}
$$

The idea is to find a function $f(x)$ for which $x = \frac{1}{D}$ is zero. One such
function is:

$$
f(x) = \frac{1}{x} - D
$$

(Substitue $x = \frac{1}{D}$ in the above equation and it should result in zero)

Next, we find $f'(x)$ and substitue it in the NM equation to give us an equation
that allows successive improvements.

$$
x_{i+1} = x_i - \frac{\frac{1}{x_i} - D}{- \frac{1}{x_i^2}} = x_i \cdot \left(2 - D x_i\right)
$$

Astute readers will notice that the result $x_{i+1}$ depends on $x_i$ (the
previous iteration) i.e. $x_2$ depends on $x_1$ and $x_1$ depends on $x_0$
How do we calculate $x_0$? This is the problem of initial approximation.

### Initial Approximation to the Reciprocal

Lest the curtain be drawn too soon, here is the final equation for calculating
$x_0$, provided $D$ has been scaled to be in the range $[0.5, 1]$:

$$
x_0 = \frac{48}{17} - \frac{32}{17} D
$$

This equation is a **linear**, **smooth**, and **non-periodic** function. In
numerical algorithms like division, the goal is not necessarily the smallest
average error, but guaranteeing the **worst-case error** ($\vert \epsilon_0
\vert$) is as small as possible. This predictability is important because the
initial error directly determines the number of Newton-Raphson iterations
required to reach full machine precision.

We wish to calculate an approximation for the function $1/D$ such that the
worst-case error is minimal. The right tool for this job is the [Chebyshev
Equioscillation Theorem](https://en.wikipedia.org/wiki/Equioscillation_theorem).

Chebyshev approximation is used because it provides the **Best Uniform
Approximation** (or Minimax Approximation). This means that out of all possible
polynomials of a given degree, the Chebyshev method yields the one that
minimizes the maximum absolute error across the entire target interval.

We start by formulating the error function on which equioscillation will be
applied. The error function for figuring out the reciprocal $x_0 = 1/D$ using a
simple straight line $x_0 = T_0 + T_1 \cdot D$ (a linear equation) tells us how
far off our guess is from the perfect answer. Because we want the total result
$D \cdot x_0$ to be near $1$, we make the error function $f(D)$ measure the
difference between that product and $1$. The formula is $f(D) = 1 - D \cdot
x_0$. When we plug in the straight-line guess, the formula becomes:

$$
f(D) = 1 - T_0 D - T_1 D^2
$$

The main goal is to pick the numbers $T_0$ and $T_1$ that minimize the absolute
value of this error $f(D)$ everywhere in the range. This is exactly what the
Chebyshev method does.

Before we apply the theorem on the error equation, we need to constrain the
values that $D$ can take. Bounding $D$ guarantees that the starting error is
small enough for the subsequent iterations to converge quickly and predictably
to full fixed-point precision. Without this bound, a much more complex,
higher-degree polynomial would be needed, defeating the efficiency goal. We
bound $D$ to be $[0.5, 1]$. In code, this scaling can be achieved through simple
bit-shifts. As long as we scale the numerator too, the result remains correct.

The theorem states that a polynomial is the best uniform approximation to a
continuous function over an interval if and only if the error function
alternates between its maximum positive and maximum negative values at least
$(n+2)$ times, where $n$ is the degree of the polynomial. Since $n=1$ (linear
approximation), we need $1+2=3$ alternating extrema: at the two endpoints
($D=1/2$ and $D=1$) and the local extremum ($D_{min}$) between them.

The location of the local extremum is found by setting the derivative to zero:

$$
f'(D) = -T_0 - 2T_1 D = 0, \text{ which gives: }
D_{min} = - \frac{T_0}{2T_1}
$$

The first condition of the theorem is that the error magnitude is equal at
endpoints, i.e., $f(1/2) = f(1)$.

$$
1 - \frac{T_0}{2} - \frac{T_1}{4} = 1 - T_0 - T_1
$$

This simplifies to:

$$
T_0 = - \frac{3}{2} T_1
$$

The second condition states that the error at endpoints must be the negative of
the error at the extremum, i.e., $f(1) = -f(D_{min})$.

$$
1 - T_0 - T_1 = - \left( 1 - T_0 D_{min} - T_1 D_{min}^2 \right)
$$

Substituting $D_{min}$ and simplifying:

$$
1 - T_0 - T_1 = - \left( 1 + \frac{T_0^2}{4T_1} \right)
$$

Substituting the value of $T_0$ from above:

$$
1 - \left( - \frac{3}{2} T_1 \right) - T_1 = -1 - \frac{(-3/2 \cdot T_1)^2}{4T_1}
1 + \frac{1}{2} T_1 = -1 - \frac{9T_1}{16}
$$

Solving this linear equation for $T_1$:

$$
2 = - \frac{17T_1}{16}
T_1 = - \frac{32}{17}
$$

Substituting $T_1$ back into the original equation to find $T_0$:

$$
T_0 = - \frac{3}{2} \cdot \left( - \frac{32}{17} \right)
T_0 = \frac{48}{17}
$$

The resulting linear approximation is $x_0 = T_0 + T_1 D$:

$$
x_0 = \frac{48}{17} - \frac{32}{17} D
$$

This equation gives the optimal initial estimate for the reciprocal that can be
refined by iterations of the Newton-Raphson equation.

## Implementation

(For convenience, here's a
[link](https://gist.github.com/bojle/60f9f9c0a7b0678a2f6b51553217ab6a) to the
complete implementation)

The original rationale for this implementation was two-fold:

1.  **Lack of division circuitry.**
2.  **Lack of support for floating point types.**

Lack of division circuitry is solved by the algorithm design (reciprocal
multiplication). Lack of floating point types is dealt with by using
[Fixed-Point notation](https://en.wikipedia.org/wiki/Fixed-point_arithmetic).
Fixed point allows storing everything in integers and operating using
**bit-shift operations**, which are highly cost-efficient on embedded hardware.

Here's an implementation of a fixed-point type in C++:

```cpp
#include <iostream>
#include <cmath>
#include <cstdint>
#include <type_traits>
#include <limits>
#include <cassert>
#include <numeric>

template <int FRAC_BITS, int TOTAL_BITS>
class FixedPoint {
    using BaseType = decltype([] {
        if constexpr (TOTAL_BITS <= 8) {
            return int8_t{};
        } else if constexpr (TOTAL_BITS <= 16) {
            return int16_t{};
        } else if constexpr (TOTAL_BITS <= 32) {
            return int32_t{};
        } else {
            return int64_t{};
        }
    }());

    using WideType = typename std::conditional<(sizeof(BaseType) <= 4), int64_t, __int128_t>::type;
    BaseType value;

public:
    constexpr static BaseType SCALE = static_cast<BaseType>(1ULL << FRAC_BITS);
    FixedPoint() : value(0) {}
    FixedPoint(float f) : value(static_cast<BaseType>(std::round(f * SCALE))) {}
    BaseType raw() const { return value; }

    static FixedPoint fromRaw(BaseType rawVal) {
        FixedPoint fp;
        fp.value = rawVal;
        return fp;
    }

    float toFloat() const { return static_cast<float>(value) / SCALE; }

    FixedPoint operator+(const FixedPoint &other) const {
        return fromRaw(value + other.value);
    }
    FixedPoint operator-(const FixedPoint &other) const {
        return fromRaw(value - other.value);
    }
    FixedPoint operator*(const FixedPoint &other) const {
        WideType prod = static_cast<WideType>(value) * other.value;
        return fromRaw(static_cast<BaseType>(prod >> FRAC_BITS));
    }
    FixedPoint operator*(float factor) const {
        return FixedPoint(toFloat() * factor);
    }

    friend std::ostream &operator<<(std::ostream &os, const FixedPoint &fp) {
        return os << fp.toFloat();
    }
};
```
The template parameters specify the fractional and total bit lengths. For
example, `FixedPoint<8, 16>` uses a 16-bit integer with the scale $2^8$. The
central idea is that all operations are performed on the integer directly, and
conversion involves scaling and de-scaling with the constant scale value.

The division function below implements the 4-part process: **Normalization**,
**Initial Approximation**, **NR Iterations**, and **Multiplication with
Numerator**. We use the higher precision `FixedPoint<16, 32>`
(`Fx16_32`) for intermediate calculations to minimize approximation
error before truncating to the final `Fx8_16` result.

```cpp
using Fx8_16 = FixedPoint<8, 16>;
using Fx16_32 = FixedPoint<16, 32>;

Fx8_16 fxdiv_corrected(int n, int d) {
    assert(d != 0 && "Divide by zero undefined");

    if (n == 0) return Fx8_16(0.0f);

    bool result_is_negative = ((n < 0) != (d < 0));
    uint32_t nv = static_cast<uint32_t>(std::abs(n));
    uint32_t dv = static_cast<uint32_t>(std::abs(d));

    // 1. Normalization/scaling 'd' to fit between 0.5 and 1.0
    int shift = std::countl_zero<uint32_t>(dv);
    uint32_t scaled_val_raw = dv << shift;
    uint32_t scaled_val_n_raw = nv << shift;
    constexpr int INTERPRETATION_SHIFT = 31 - 16;

    Fx16_32 d_scaled = Fx16_32::fromRaw(static_cast<int32_t>(scaled_val_raw >> INTERPRETATION_SHIFT));
    Fx16_32 n_scaled = Fx16_32::fromRaw(static_cast<int32_t>(scaled_val_n_raw >> INTERPRETATION_SHIFT));

    // 2. Initial approximate calculation (Chebyshev: X0 = 48/17 - 32/17 * D)
    Fx16_32 a {2.8235294f}; // 48/17
    Fx16_32 b {1.8823529f}; // 32/17
    Fx16_32 initial_approx = a - (b * d_scaled);

    // 3. Newton-Raphson iterations
    Fx16_32 val = initial_approx;
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E1: Precision ~8 bits
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E2: Precision ~16 bits (sufficient for Fx16_32)
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E3: Conservative overkill
    val = val * (Fx16_32{2.f} - (d_scaled * val)); // E4: Conservative overkill

    // 4. Multiplication with Numerator
    Fx16_32 res_16_32 = n_scaled * val;

    if (result_is_negative) {
        // Simple negation
        res_16_32 = res_16_32 * -1.0f;
    }

    // Truncate from Fx16_32 (FRAC_BITS=16) to Fx8_16 (FRAC_BITS=8)
    constexpr int TRUNCATION_SHIFT = 16 - 8;

    // Shift the raw 32-bit value right by 8 bits to change the binary point position
    int32_t raw_final_32 = res_16_32.raw();
    int16_t raw_final_16 = static_cast<int16_t>(raw_final_32 >> TRUNCATION_SHIFT);

    Fx8_16 final_res = Fx8_16::fromRaw(raw_final_16);

    return final_res;
}
```

The `INTERPRETATION_SHIFT` and `TRUNCATION_SHIFT` variables account for
correctly aligning the binary point.

  * The `INTERPRETATION_SHIFT` (31 - 16 = 15) adjusts the $Q1.31$ normalized
    input to the $Q15.16$ format used for calculation, ensuring the value is
interpreted as being in the range $[0.5, 1.0]$.
  * The `TRUNCATION_SHIFT` (16 - 8 = 8) reduces the $Q15.16$ result to the
    final $Q7.8$ output format, discarding the lower 8 fractional bits.

The code is compiled and run with an example:

```cpp
int main() {
    std::cout.precision(10);
    int n = 3;
    int d = 4;
    Fx8_16 result = fxdiv_corrected(n, d);
    std::cout << "Approximate division of " << n << "/" << d << ": " << result << std::endl;
    std::cout << "Real division of " << n << "/" << d << ": " << static_cast<float>(3)/static_cast<float>(4) << std::endl;
    return 0;
}
```

```bash
$ clang++ fixed_div.cpp -o a -std=c++20
$ ./a
Approximate division of 3/4: 0.74609375
Real division of 3/4: 0.75
```

The result $0.74609375$ is produced. The error is $\vert 0.75 - 0.74609375 \vert
= 0.00390625$. This error is precisely $2^{-8}$, confirming that the final
precision is limited by the $Q7.8$ output format's smallest bit, which is a key
design feature of fixed-point systems. In fact, the number $0.00390625$ has a
name: [ULP](https://en.wikipedia.org/wiki/Unit_in_the_last_place). Due to our
use of $Q7.8$ as the resultant type, it is impossible to precisely express
$0.75$. What we can express is $0.75 - ULP$ and $0.75 + ULP$

## Optimizations

### Power-of-Two Denominator Shortcut

When the denominator $D$ is a power of two ($\pm 2^k$), the division $N/D$
simplifies to a **bit shift**. This avoids the computationally expensive
Newton-Raphson (NR) iterative loop entirely. The check to detect if an integer
is a power of 2 can be performed in $\mathcal{O}(1)$ time, providing a major
speed increase for such common cases.

### Exploiting Quadratic Convergence

One property of NR iteration is **Quadratic Convergence**. Every iteration
approximately doubles the number of correct bits in the result.

The optimization involves determining the required number of iterations based on
the fractional length of the resultant type. For a required precision of $16$
fractional bits (as in the `Fx16_32` intermediate type), only two
iterations are mathematically necessary after the initial approximation.
[`constexpr if`](https://en.cppreference.com/w/cpp/language/if.html) statements
can be used to compile-time check the required precision and eliminate
unnecessary NR iterations, ensuring no runtime performance penalty.

### Alternative Initial Approximation Methods

While the Chebyshev approximation provides the optimal minimax error for the
initial guess, alternative methods exist:

* [**Remez Algorithm:**](https://en.wikipedia.org/wiki/Remez_algorithm) Can
  generate even better approximations using a higher-degree polynomial. The
trade-off is higher initial calculation complexity for the potential benefit of
requiring fewer subsequent NR iterations.
* **Look-up Tables (LUTs) and Magic Constants:** [Recent
  research](https://dl.acm.org/doi/pdf/10.1145/3708472) shows that pre-computed
LUTs combined with constants can speed up the initial reciprocal approximation.
* [**CORDIC (Coordinate Rotation Digital
  Computer):**](https://en.wikipedia.org/wiki/CORDIC) An alternative iterative
technique that can calculate division and other trigonometric functions using
only additions and shifts. It offers competitive performance in some hardware
environments.

## Conclusion

This article came into being after I spent around a month trying to understand
approximation methods and getting code for it to work. The actual code was
contributed to the [llvm-project](https://github.com/llvm/llvm-project/) as an
addition to the stdfix library in the llvm libc project. Here is the
[PR](https://github.com/llvm/llvm-project/pull/154914).
[Here's](https://github.com/llvm/llvm-project/blob/7eee67202378932d03331ad04e7d07ed4d988381/libc/src/__support/fixed_point/fx_bits.h#L242)
a link to the complete division function implemented with stdfix primitives and
the optimizations mentioned above.
